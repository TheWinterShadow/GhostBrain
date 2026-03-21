"""Core pipeline assembly logic."""

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

from ghost_brain.config import Settings
from ghost_brain.services.context import create_context_and_aggregators
from ghost_brain.services.llm import create_llm
from ghost_brain.services.stt import create_stt
from ghost_brain.services.tts import create_tts


def build_pipeline(
    transport: FastAPIWebsocketTransport,
    settings: Settings,
    sample_rate: int = 8000,
) -> tuple[Pipeline, PipelineTask, LLMContext]:
    """
    Build the full Pipecat pipeline and task for the Ghost Brain bot.

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
