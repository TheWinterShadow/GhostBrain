"""Core pipeline assembly logic."""

import audioop

from loguru import logger
from pipecat.frames.frames import Frame, InputAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.base_transport import BaseTransport

from ghost_brain.config import Settings
from ghost_brain.services.context import create_context_and_aggregators
from ghost_brain.services.llm import create_llm
from ghost_brain.services.stt import create_stt
from ghost_brain.services.tts import create_tts


class AudioResampler(FrameProcessor):
    """Processor to resample audio frames."""

    def __init__(self, input_rate: int, output_rate: int):
        super().__init__()
        self._input_rate = input_rate
        self._output_rate = output_rate
        self._state = None

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        # Handle StartFrame specially to ensure proper state tracking
        if "StartFrame" in str(type(frame)):
            # For StartFrame, we MUST call super() first to set self._started = True
            await super().process_frame(frame, direction)

        if isinstance(frame, InputAudioRawFrame):
            if not frame.audio or len(frame.audio) == 0:
                logger.warning("AudioResampler: Received empty audio frame, skipping")
                return

            # Resample audio using audioop (low latency)
            try:
                resampled_audio, self._state = audioop.ratecv(
                    frame.audio,
                    2,  # 16-bit
                    1,  # mono
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

            # Update frame with new audio and sample rate
            frame.audio = resampled_audio
            frame.sample_rate = self._output_rate

            # Recalculate num_frames since length changed
            frame.num_frames = int(len(frame.audio) / (frame.num_channels * 2))

            await self.push_frame(frame, direction)
        else:
            await self.push_frame(frame, direction)


# ...
async def build_pipeline(
    transport: BaseTransport,
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

    # Attach native Pipecat function for DuckDuckGo web search
    from ghost_brain.tools.search import search_web

    logger.info("Initializing Native Web Search Tool...")
    llm.register_function("search_web", search_web)
    logger.info("Web Search Tool registered successfully!")

    pipeline = Pipeline(
        [
            transport.input(),
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
