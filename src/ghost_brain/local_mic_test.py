#!/usr/bin/env python
"""
Simple local testing script using PyAudio for microphone input.
This bypasses Twilio and uses your local microphone for testing the voice pipeline.

Requirements:
    pip install pyaudio wave

Usage:
    python -m ghost_brain.local_mic_test

IMPORTANT: Use headphones to prevent the bot from hearing itself through your speakers!
           Without headphones, the bot will hear and respond to its own voice.
"""

import asyncio
import logging
import sys
from pathlib import Path

try:
    import pyaudio  # noqa: F401
except ImportError:
    print("PyAudio not installed. Please run: pip install pyaudio")
    print("On macOS, you may need: brew install portaudio")
    sys.exit(1)

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMRunFrame,
)
from pipecat.pipeline.base_task import PipelineTaskParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from ghost_brain.config import Settings, get_settings
from ghost_brain.modules.pipeline.pipeline import build_pipeline
from ghost_brain.utils.transcript import format_transcript

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MuteInputMonitor(FrameProcessor):
    """Processor to mute input transport when bot is speaking."""

    def __init__(self, input_transport: LocalAudioTransport) -> None:
        super().__init__()
        self.input_transport = input_transport

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        if isinstance(frame, BotStartedSpeakingFrame):
            logger.info("Bot started speaking - muting input")
            self.input_transport._params.audio_in_enabled = False
        elif isinstance(frame, BotStoppedSpeakingFrame):
            logger.info("Bot stopped speaking - unmuting input")
            self.input_transport._params.audio_in_enabled = True

        await super().process_frame(frame, direction)


class LocalMicrophoneBot:
    """Bot for testing with local microphone instead of Twilio."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.context = LLMContext()
        # Local transport usually needs 16k/24k, but we force 8k to match production
        self.transport = LocalAudioTransport(
            params=LocalAudioTransportParams(
                audio_out_sample_rate=8000,
                audio_in_sample_rate=8000,
                audio_out_enabled=True,
                audio_in_enabled=True,
                audio_out_channels=1,
                audio_in_channels=1,
            )
        )

    async def build_pipeline(self) -> tuple[Pipeline, PipelineTask]:
        """Build the voice pipeline using the production pipeline builder."""

        # Use the core build_pipeline function but pass our local transport
        pipeline, task, context = await build_pipeline(
            transport=self.transport, settings=self.settings, sample_rate=8000
        )
        self.context = context

        # For local testing, disable interruptions to prevent the bot from hearing itself
        # and interrupting. This is a simpler solution than trying to mute the mic.
        task._params.allow_interruptions = False

        return pipeline, task

    async def run(self) -> None:
        """Run the bot with local microphone."""
        try:
            # Build pipeline
            pipeline, task = await self.build_pipeline()

            print("\n" + "=" * 60)
            print("🎤 Ghost Brain Local Microphone Test")
            print("=" * 60)
            print("\n⚠️  IMPORTANT: Use headphones to prevent echo!")
            print("    Without headphones, the bot will hear its own voice.")
            print("\nInstructions:")
            print("  • Speak clearly into your microphone")
            print("  • Wait for the bot to finish speaking before responding")
            print("  • Press Ctrl+C to stop and save the transcript")
            print("\nStarting...\n")

            # Run pipeline
            task_params = PipelineTaskParams(loop=asyncio.get_running_loop())

            # Start a background task to trigger the bot to speak first
            async def trigger_start() -> None:
                await asyncio.sleep(2)  # Give pipeline time to initialize
                print("Bot connecting...")
                await task.queue_frames([LLMRunFrame()])

            asyncio.create_task(trigger_start())

            await task.run(task_params)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping...")
        except Exception as e:
            logger.exception(f"Error during execution: {e}")
        finally:
            # Save transcript
            if self.context and self.context.get_messages():
                transcript = format_transcript(self.context)

                # Save to file
                transcript_file = Path("local_mic_transcript.txt")
                transcript_file.write_text(transcript)
                print(f"\n💾 Transcript saved to: {transcript_file}")

                # Print transcript
                print("\n" + "=" * 60)
                print("📝 Conversation Transcript")
                print("=" * 60)
                print(transcript)


async def main() -> None:
    """Main entry point."""
    # Check for required environment variables
    settings = get_settings()

    required_vars = [
        ("GHOST_BRAIN_DEEPGRAM_API_KEY", "Deepgram API key for speech-to-text"),
        ("GHOST_BRAIN_GROQ_API_KEY", "Groq API key for LLM"),
    ]

    missing = []
    for var, desc in required_vars:
        if not os.getenv(var):
            missing.append(f"  • {var}: {desc}")

    if missing:
        print("❌ Missing required environment variables:")
        print("\n".join(missing))
        print("\nSet these in your .env file or environment")
        sys.exit(1)

    # Run bot
    bot = LocalMicrophoneBot(settings)
    await bot.run()


if __name__ == "__main__":
    import os

    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv

        load_dotenv()

    asyncio.run(main())
