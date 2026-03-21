"""Debug processors for pipeline inspection."""

import logging

from pipecat.frames.frames import AudioRawFrame, Frame, TextFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

logger = logging.getLogger(__name__)


class AudioLogger(FrameProcessor):
    """Logs details about audio frames passing through."""

    def __init__(self, name: str = "AudioLogger"):
        super().__init__()
        self._name = name
        self._log_every = 50  # Log every 50th frame to avoid spam
        self._count = 0

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        logger.debug("[%s] Processing frame: %s", self._name, frame)
        if isinstance(frame, AudioRawFrame):
            self._count += 1
            if self._count % self._log_every == 0:
                logger.info(
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
