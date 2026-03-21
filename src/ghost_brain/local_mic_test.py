#!/usr/bin/env python
"""
Simple local testing script using PyAudio for microphone input.
This bypasses Twilio and uses your local microphone for testing the voice pipeline.

Requirements:
    pip install pyaudio wave

Usage:
    python -m ghost_brain.local_mic_test
"""

import asyncio
import logging
import sys
from pathlib import Path

try:
    import pyaudio
except ImportError:
    print("PyAudio not installed. Please run: pip install pyaudio")
    print("On macOS, you may need: brew install portaudio")
    sys.exit(1)

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import BotStartedSpeakingFrame, BotStoppedSpeakingFrame, Frame
from pipecat.pipeline.base_task import PipelineTaskParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.transports.local.audio import LocalAudioTransport, LocalAudioTransportParams

from ghost_brain.config import Settings, get_settings
from ghost_brain.utils.transcript import format_transcript

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MuteInputMonitor(FrameProcessor):
    """Processor to mute input transport when bot is speaking."""

    def __init__(self, input_transport):
        super().__init__()
        self.input_transport = input_transport

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, BotStartedSpeakingFrame):
            logger.info("Bot started speaking - muting input")
            self.input_transport._params.audio_in_enabled = False
        elif isinstance(frame, BotStoppedSpeakingFrame):
            logger.info("Bot stopped speaking - unmuting input")
            self.input_transport._params.audio_in_enabled = True

        await self.push_frame(frame, direction)


class LocalMicrophoneBot:
    """Bot for testing with local microphone instead of Twilio."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.context = LLMContext()
        self.transport = LocalAudioTransport(
            params=LocalAudioTransportParams(
                audio_out_sample_rate=24000,
                audio_in_sample_rate=16000,
                audio_out_enabled=True,
                audio_in_enabled=True,
                audio_out_channels=1,
                audio_in_channels=1,
            )
        )

    def build_pipeline(self) -> tuple[Pipeline, PipelineTask]:
        """Build the voice pipeline with local microphone transport."""

        # Create VAD and aggregators
        vad_analyzer = SileroVADAnalyzer(
            sample_rate=16000,
            params=VADParams(
                stop_secs=0.5,  # Slightly longer pause detection for local testing
                min_volume=0.1,
            ),
        )

        user_params = LLMUserAggregatorParams(vad_analyzer=vad_analyzer)
        user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
            self.context,
            user_params=user_params,
        )

        # Create services
        stt = DeepgramSTTService(
            api_key=self.settings.deepgram_api_key,
            model="nova-2",
        )

        llm = GroqLLMService(
            api_key=self.settings.groq_api_key,
            settings=GroqLLMService.Settings(
                model="llama-3.3-70b-versatile",
                system_instruction=(
                    "You are Ghost Brain, a friendly voice interviewer. "
                    "Keep responses concise and natural for spoken conversation. "
                    "Ask one question at a time and listen before continuing. "
                    "Start by greeting the user and asking how you can help them today."
                ),
            ),
        )

        tts = OpenAITTSService(
            api_key=self.settings.openai_api_key,
            settings=OpenAITTSService.Settings(
                voice="alloy",
                model="tts-1",
            ),
        )

        # Build pipeline
        mute_monitor = MuteInputMonitor(self.transport.input())

        pipeline = Pipeline(
            [
                self.transport.input(),
                stt,
                user_aggregator,
                llm,
                tts,
                mute_monitor,
                self.transport.output(),
                assistant_aggregator,
            ]
        )

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,
                audio_in_sample_rate=16000,
                audio_out_sample_rate=24000,
            ),
        )

        return pipeline, task

    async def run(self):
        """Run the bot with local microphone."""
        try:
            # Build pipeline
            pipeline, task = self.build_pipeline()

            print("\n" + "=" * 60)
            print("🎤 Ghost Brain Local Microphone Test")
            print("=" * 60)
            print("\nInstructions:")
            print("  • Speak clearly into your microphone")
            print("  • Wait for the bot to finish speaking before responding")
            print("  • Press Ctrl+C to stop and save the transcript")
            print("\nStarting... Say hello to begin!\n")

            # Run pipeline
            task_params = PipelineTaskParams(loop=asyncio.get_running_loop())
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


async def main():
    """Main entry point."""
    # Check for required environment variables
    settings = get_settings()

    required_vars = [
        ("GHOST_BRAIN_DEEPGRAM_API_KEY", "Deepgram API key for speech-to-text"),
        ("GHOST_BRAIN_GROQ_API_KEY", "Groq API key for LLM"),
        ("GHOST_BRAIN_OPENAI_API_KEY", "OpenAI API key for text-to-speech"),
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
