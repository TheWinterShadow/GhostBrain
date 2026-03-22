"""Core pipeline assembly logic."""

import audioop

from loguru import logger
from pipecat.frames.frames import Frame, InputAudioRawFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

from ghost_brain.config import Settings
from ghost_brain.services.context import create_context_and_aggregators
from ghost_brain.services.llm import create_llm
from ghost_brain.services.stt import create_stt
from ghost_brain.services.tts import create_tts


class DebugFrameLogger(FrameProcessor):
    """Debug processor that logs all frames passing through."""

    def __init__(self, label: str = "DebugLogger"):
        super().__init__()
        self.label = label
        self.frame_count = 0
        self.audio_frame_count = 0

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        # Allow the base class to handle internal state (like StartFrame)
        await super().process_frame(frame, direction)

        self.frame_count += 1

        if isinstance(frame, InputAudioRawFrame):
            self.audio_frame_count += 1
            if self.audio_frame_count <= 10 or self.audio_frame_count % 100 == 0:
                logger.info(
                    f"{self.label}: Audio frame #{self.audio_frame_count} - "
                    f"size={len(frame.audio) if frame.audio else 0} bytes, "
                    f"sample_rate={frame.sample_rate}"
                )
        elif self.frame_count <= 20:  # Log first 20 frames of any type
            frame_type = type(frame).__name__
            logger.info(f"{self.label}: Frame #{self.frame_count} - {frame_type}")

        await self.push_frame(frame, direction)


class AudioResampler(FrameProcessor):
    """Processor to resample audio frames."""

    def __init__(self, input_rate: int, output_rate: int):
        super().__init__()
        self._input_rate = input_rate
        self._output_rate = output_rate
        self._state = None
        logger.info(f"AudioResampler initialized: {input_rate} -> {output_rate}")

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        # Handle StartFrame specially to ensure proper state tracking
        if "StartFrame" in str(type(frame)):
            logger.debug("AudioResampler: Received StartFrame, forwarding")
            # For StartFrame, we MUST call super() first to set self._started = True
            await super().process_frame(frame, direction)
            # Don't return - continue to check if it's audio or pass through

        if isinstance(frame, InputAudioRawFrame):
            logger.debug(
                f"AudioResampler: Received audio frame - "
                f"size={len(frame.audio) if frame.audio else 0} bytes, "
                f"sample_rate={frame.sample_rate}, "
                f"num_frames={frame.num_frames}"
            )
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
                logger.debug(
                    f"AudioResampler: Resampled {len(frame.audio)} bytes -> "
                    f"{len(resampled_audio)} bytes ({self._input_rate}Hz -> {self._output_rate}Hz)"
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
            # For non-audio frames, just push them through
            frame_type = type(frame).__name__
            if frame_type not in ["SystemFrame", "EndFrame"]:  # Don't log every system frame
                logger.debug(f"AudioResampler: Forwarding non-audio frame: {frame_type}")
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

    # Add debug logger to track frames from transport
    debug_logger = DebugFrameLogger("TransportDebug")

    pipeline = Pipeline(
        [
            transport.input(),
            debug_logger,  # Debug: log what comes from transport
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
