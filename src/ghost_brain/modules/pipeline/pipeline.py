"""Core pipeline assembly logic."""

import audioop
from typing import Any

from loguru import logger
from pipecat.frames.frames import Frame, InputAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.base_transport import BaseTransport

from ghost_brain.config import Settings
from ghost_brain.modules.ai.context import create_context_and_aggregators
from ghost_brain.modules.ai.llm import create_llm
from ghost_brain.modules.ai.stt import create_stt
from ghost_brain.modules.ai.tts import create_tts
from ghost_brain.tools.search import search_web


class AudioResampler(FrameProcessor):
    """Processor to resample audio frames."""

    def __init__(self, input_rate: int, output_rate: int) -> None:
        """Initialize the audio resampler.

        Args:
            input_rate: The sample rate of incoming audio.
            output_rate: The target sample rate for outgoing audio.
        """
        super().__init__()
        self._input_rate: int = input_rate
        self._output_rate: int = output_rate
        self._state: Any | None = None

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process an incoming frame and resample if it contains audio.

        Args:
            frame: The frame to process.
            direction: The direction of the frame in the pipeline.
        """
        if "StartFrame" in str(type(frame)):
            await super().process_frame(frame, direction)

        if isinstance(frame, InputAudioRawFrame):
            if not frame.audio or len(frame.audio) == 0:
                logger.warning("AudioResampler: Received empty audio frame, skipping")
                return

            try:
                resampled_audio, self._state = audioop.ratecv(
                    frame.audio,
                    2,
                    1,
                    self._input_rate,
                    self._output_rate,
                    self._state,
                )
            except Exception as e:
                logger.error(f"AudioResampler: Resampling error: {e}")
                return

            if not resampled_audio or len(resampled_audio) == 0:
                logger.warning("AudioResampler: Resampling resulted in empty audio")
                return

            frame.audio = resampled_audio
            frame.sample_rate = self._output_rate
            frame.num_frames = int(len(frame.audio) / (frame.num_channels * 2))

            await self.push_frame(frame, direction)
        else:
            await self.push_frame(frame, direction)


async def build_pipeline(
    transport: BaseTransport,
    settings: Settings,
    sample_rate: int = 8000,
) -> tuple[Pipeline, PipelineTask, LLMContext]:
    """Build the full Pipecat pipeline and task for the Ghost Brain bot.

    Args:
        transport: FastAPI WebSocket transport.
        settings: Application settings for API keys.
        sample_rate: Audio I/O sample rate.

    Returns:
        Tuple of (pipeline, task, context).
    """
    stt = create_stt(settings, sample_rate=16000)
    context, user_agg, assistant_agg = create_context_and_aggregators(sample_rate=16000)
    llm = create_llm(settings)
    tts = create_tts(settings)

    resampler = AudioResampler(input_rate=sample_rate, output_rate=16000)

    logger.info("Initializing Native Web Search Tool...")
    llm.register_direct_function(search_web)
    logger.info("Web Search Tool registered successfully!")

    pipeline = Pipeline(
        [
            transport.input(),
            resampler,
            stt,
            user_agg,
            llm,
            tts,
            transport.output(),
            assistant_agg,
        ]
    )

    params = PipelineParams(
        allow_interruptions=False,
        audio_in_sample_rate=sample_rate,
        audio_out_sample_rate=sample_rate,
    )
    task = PipelineTask(pipeline, params=params)
    return pipeline, task, context
