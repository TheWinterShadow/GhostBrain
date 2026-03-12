"""Pipecat pipeline construction: STT, LLM, TTS, context, and VAD."""

from typing import Any

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

from ghostwriter.config import Settings


def create_context_and_aggregators(
    sample_rate: int = 8000,
) -> tuple[LLMContext, Any, Any]:
    """
    Create shared LLM context and user/assistant context aggregators with VAD.

    Args:
        sample_rate: Audio sample rate (8000 for Twilio). Silero supports 8000 or 16000.

    Returns:
        Tuple of (context, user_aggregator, assistant_aggregator).
    """
    context = LLMContext()
    vad_analyzer = SileroVADAnalyzer(
        sample_rate=sample_rate,
        params=VADParams(stop_secs=0.2),
    )
    user_params = LLMUserAggregatorParams(vad_analyzer=vad_analyzer)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=user_params,
    )
    return context, user_aggregator, assistant_aggregator


def create_stt(settings: Settings) -> DeepgramSTTService:
    """Create Deepgram STT service (nova-2 model)."""
    return DeepgramSTTService(
        api_key=settings.deepgram_api_key,
        model="nova-2",
    )


def create_llm(settings: Settings) -> GroqLLMService:
    """Create Groq LLM service (llama-3.1-70b-versatile)."""
    return GroqLLMService(
        api_key=settings.groq_api_key,
        model="llama-3.1-70b-versatile",
        system_instruction=(
            "You are Ghostwriter, a friendly voice interviewer. "
            "Keep responses concise and natural for spoken conversation. "
            "Ask one question at a time and listen before continuing."
        ),
    )


def create_tts(settings: Settings) -> OpenAITTSService:
    """Create OpenAI TTS service (tts-1, voice alloy)."""
    return OpenAITTSService(
        api_key=settings.openai_api_key,
        voice="alloy",
        model="tts-1",
    )


def build_pipeline(
    transport: FastAPIWebsocketTransport,
    settings: Settings,
    sample_rate: int = 8000,
) -> tuple[Pipeline, PipelineTask, LLMContext]:
    """
    Build the full Pipecat pipeline and task for the Ghostwriter bot.

    Args:
        transport: FastAPI WebSocket transport (with Twilio serializer).
        settings: Application settings for API keys.
        sample_rate: Audio I/O sample rate (8000 for Twilio).

    Returns:
        Tuple of (pipeline, task, context). Context is used for transcript on disconnect.
    """
    context, user_agg, assistant_agg = create_context_and_aggregators(sample_rate)
    stt = create_stt(settings)
    llm = create_llm(settings)
    tts = create_tts(settings)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_agg,
            llm,
            tts,
            transport.output(),
            assistant_agg,
        ]
    )

    params = PipelineParams(
        audio_in_sample_rate=sample_rate,
        audio_out_sample_rate=sample_rate,
    )
    task = PipelineTask(pipeline, params=params)
    return pipeline, task, context
