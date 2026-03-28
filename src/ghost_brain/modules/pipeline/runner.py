"""Pipeline runner and event handlers: connect, disconnect, transcript upload."""

import logging
from typing import Any

from pipecat.frames.frames import LLMMessagesAppendFrame, LLMRunFrame
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

from ghost_brain.config import Settings
from ghost_brain.utils.transcript import format_transcript_markdown, upload_transcript_to_gcs

logger = logging.getLogger(__name__)


def register_handlers(
    transport: FastAPIWebsocketTransport,
    task: PipelineTask,
    context: LLMContext,
    settings: Settings,
    session_id: str,
) -> None:
    """Register transport event handlers for client connect and disconnect.

    Args:
        transport: The WebSocket transport for handling connections.
        task: The active pipeline task.
        context: LLM context containing conversation history.
        settings: Application settings.
        session_id: The unique identifier for the current session.
    """

    @transport.event_handler("on_client_connected")
    async def on_client_connected(_transport: Any, _client: Any) -> None:
        """Handle new client connection and initiate the conversation.

        Args:
            _transport: The transport instance.
            _client: The connected client object.
        """
        logger.info("Client connected! Queueing initial LLMRunFrame.")
        msg = (
            "The user has connected to the phone call. "
            "Please begin the conversation by saying exactly your initial greeting, "
            "and nothing else."
        )
        await task.queue_frames(
            [
                LLMMessagesAppendFrame([{"role": "system", "content": msg}]),
                LLMRunFrame(),
            ]
        )

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(_transport: Any, _client: Any) -> None:
        """Handle client disconnection, process the transcript, and clean up.

        Args:
            _transport: The transport instance.
            _client: The disconnected client object.
        """
        try:
            messages = getattr(context, "messages", []) or []
            if messages:
                markdown = format_transcript_markdown(
                    messages,
                    session_id=session_id,
                )
                blob_path = f"transcripts/{session_id}.md"
                upload_transcript_to_gcs(
                    settings.gcp_bucket_name,
                    markdown,
                    blob_path,
                )
                logger.info(
                    "Uploaded transcript to gs://%s/%s", settings.gcp_bucket_name, blob_path
                )
        except Exception as e:
            logger.exception("Failed to upload transcript: %s", e)
        await task.cancel()


async def run_pipeline(task: PipelineTask) -> None:
    """Execute the pipeline task.

    Args:
        task: The configured pipeline task to run.
    """
    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)
