"""Pipeline runner and event handlers: connect, disconnect, transcript upload."""

import logging
from typing import Any

from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

from ghostwriter.config import Settings
from ghostwriter.transcript import format_transcript_markdown, upload_transcript_to_gcs

logger = logging.getLogger(__name__)


def register_handlers(
    transport: FastAPIWebsocketTransport,
    task: PipelineTask,
    context: LLMContext,
    settings: Settings,
    session_id: str,
) -> None:
    """
    Register transport event handlers for client connect/disconnect.

    On connect: queue LLMRunFrame so the bot speaks first.
    On disconnect: format transcript from context.messages, upload to GCS, then cancel task.
    """

    @transport.event_handler("on_client_connected")
    async def on_client_connected(_transport: Any, _client: Any) -> None:
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(_transport: Any, _client: Any) -> None:
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
                logger.info("Uploaded transcript to gs://%s/%s", settings.gcp_bucket_name, blob_path)
        except Exception as e:
            logger.exception("Failed to upload transcript: %s", e)
        await task.cancel()


async def run_pipeline(task: PipelineTask) -> None:
    """
    Run the pipeline task with the default runner (no SIGINT handling for Cloud Run).
    """
    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)
