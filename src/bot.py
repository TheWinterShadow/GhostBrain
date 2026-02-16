"""
GhostBrain: Ultra-low-latency voice interviewer bot.
Uses Pipecat with Groq LLM, Deepgram STT, OpenAI TTS.
Transcripts are saved to GCS on call end.
"""

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.cloud import storage

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from deepgram import LiveOptions
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.groq import GroqLLMService
from pipecat.services.openai import OpenAITTSService
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

load_dotenv(override=True)

app = FastAPI(title="GhostBrain Voice Bot")

SYSTEM_PROMPT = """You are a thoughtful voice interviewer. Your role is to have a natural conversation, ask follow-up questions, and draw out ideas from the caller. Keep responses concise for voice—no lists or markdown. Speak naturally as in a phone call."""


def format_transcript_to_markdown(messages: list, call_id: str, from_number: Optional[str] = None) -> str:
    """Format LLM context messages into Markdown with frontmatter."""
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    frontmatter_lines = [f"date: {date_str}", f"call_id: {call_id}"]
    if from_number:
        frontmatter_lines.append(f"from_number: {from_number}")
    frontmatter = "---\n" + "\n".join(frontmatter_lines) + "\n---\n\n"

    body_lines = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not content:
            continue
        if role == "system":
            continue
        if role == "user":
            body_lines.append(f"**User:** {content}\n")
        elif role == "assistant":
            body_lines.append(f"**Assistant:** {content}\n")

    return frontmatter + "\n".join(body_lines)


async def upload_transcript_to_gcs(markdown: str, call_id: str) -> None:
    """Upload transcript Markdown to GCS bucket."""
    bucket_name = os.getenv("GCP_BUCKET_NAME")
    if not bucket_name:
        return
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{date_str}-{call_id}.md"
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(markdown, content_type="text/markdown")
    except Exception as e:
        # Log but don't fail the disconnect flow
        import logging
        logging.getLogger(__name__).error(f"Failed to upload transcript to GCS: {e}")


async def run_bot(websocket: WebSocket, call_data: dict) -> None:
    """Build and run the Pipecat pipeline for a single call."""
    serializer = TwilioFrameSerializer(
        stream_sid=call_data["stream_id"],
        call_sid=call_data["call_id"],
        account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
    )

    transport = FastAPIWebsocketTransport(
        websocket=websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            serializer=serializer,
        ),
    )

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        live_options=LiveOptions(model="nova-2"),
    )

    llm = GroqLLMService(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-70b-versatile",
    )

    tts = OpenAITTSService(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="tts-1",
        voice="alloy",
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    context = LLMContext(messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.cancel()
        # Format and upload transcript
        md = format_transcript_to_markdown(
            context.messages,
            call_id=call_data["call_id"],
            from_number=call_data.get("body", {}).get("from"),
        )
        if len(context.messages) > 1:  # More than just system message
            await upload_transcript_to_gcs(md, call_data["call_id"])

    runner = PipelineRunner(handle_sigint=False, force_gc=True)
    await runner.run(task)


@app.get("/voice")
async def voice_twiml():
    """Return TwiML that starts a Media Stream to our WebSocket."""
    service_url = os.getenv("SERVICE_URL", "").rstrip("/")
    ws_url = f"{service_url}/ws" if service_url else "wss://localhost:8080/ws"
    # Twilio expects wss:// for Stream url
    if not ws_url.startswith("wss://"):
        ws_url = ws_url.replace("https://", "wss://", 1)
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Start>
    <Stream url="{ws_url}"/>
  </Start>
  <Say>Connecting to GhostBrain.</Say>
</Response>'''
    from fastapi.responses import Response
    return Response(content=twiml, media_type="application/xml")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle Twilio Media Stream WebSocket connection."""
    await websocket.accept()
    try:
        transport_type, call_data = await parse_telephony_websocket(websocket)
        if transport_type != "twilio":
            await websocket.close(code=4000)
            return
        await run_bot(websocket, call_data)
    except ValueError as e:
        await websocket.close(code=4001)
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close(code=1011)
