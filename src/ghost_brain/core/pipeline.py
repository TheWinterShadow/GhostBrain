"""Core pipeline assembly logic."""

import logging

from pipecat.audio.resamplers.soxr_stream_resampler import SOXRStreamAudioResampler
from pipecat.frames.frames import Frame, InputAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

from ghost_brain.config import Settings
from ghost_brain.core.debug import AudioLogger
from ghost_brain.services.context import create_context_and_aggregators
from ghost_brain.services.llm import create_llm
from ghost_brain.services.stt import create_stt
from ghost_brain.services.tts import create_tts

logger = logging.getLogger(__name__)


class AudioResampler(FrameProcessor):
    """Processor to resample audio frames."""

    def __init__(self, input_rate: int, output_rate: int):
        super().__init__()
        self._input_rate = input_rate
        self._output_rate = output_rate
        self._resampler = SOXRStreamAudioResampler()

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, InputAudioRawFrame):
            if not frame.audio or len(frame.audio) == 0:
                # Skip empty frames to avoid STT warnings
                return

            # Resample audio
            resampled_audio = await self._resampler.resample(
                frame.audio, self._input_rate, self._output_rate
            )

            if not resampled_audio or len(resampled_audio) == 0:
                return

            # Update frame with new audio and sample rate
            frame.audio = resampled_audio
            frame.sample_rate = self._output_rate

            # Recalculate num_frames since length changed
            frame.num_frames = int(len(frame.audio) / (frame.num_channels * 2))

        await self.push_frame(frame, direction)


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
    # Create services
    # Note: STT and VAD (in context aggregator) need 16kHz even if input is 8kHz
    stt = create_stt(settings, sample_rate=16000)
    context, user_agg, assistant_agg = create_context_and_aggregators(sample_rate=16000)
    llm = create_llm(settings)
    tts = create_tts(settings)

    # If input is 8k, we need to upsample to 16k for STT/VAD
    resampler = AudioResampler(input_rate=sample_rate, output_rate=16000)

    pipeline = Pipeline(
        [
            transport.input(),
            AudioLogger("InputAudio"),
            resampler,  # Upsample 8k -> 16k
            stt,  # Expects 16k
            user_agg,  # VAD expects 16k
            llm,
            tts,
            transport.output(),
            assistant_agg,
        ]
    )

    params = PipelineParams(
        audio_in_sample_rate=sample_rate,  # 8000
        audio_out_sample_rate=sample_rate,  # 8000
    )
    task = PipelineTask(pipeline, params=params)
    return pipeline, task, context
