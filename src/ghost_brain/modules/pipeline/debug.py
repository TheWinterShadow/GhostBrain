"""Debug processors for pipeline inspection."""

import logging

from pipecat.frames.frames import AudioRawFrame, Frame, TextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger(__name__)


class AudioLogger(FrameProcessor):
    """Processor that logs details about audio frames passing through the pipeline."""

    def __init__(self, name: str = "AudioLogger") -> None:
        """Initialize the audio logger.

        Args:
            name: The display name used in log output.
        """
        super().__init__()
        self._name: str = name
        self._log_every: int = 50
        self._count: int = 0

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        """Process and potentially log an incoming frame.

        Args:
            frame: The frame to inspect and pass through.
            direction: The direction of the frame in the pipeline.
        """
        if not isinstance(frame, AudioRawFrame | TextFrame):
            logger.debug("[%s] System frame: %s", self._name, frame)

        if isinstance(frame, AudioRawFrame):
            self._count += 1
            if self._count % self._log_every == 0:
                logger.debug(
                    "[%s] Audio frame #%d: len=%d, rate=%d, channels=%d",
                    self._name,
                    self._count,
                    len(frame.audio),
                    frame.sample_rate,
                    frame.num_channels,
                )
        elif isinstance(frame, TextFrame):
            logger.info("[%s] Text frame: %s", self._name, frame.text)

        await super().process_frame(frame, direction)
