"""Local testing with microphone using Daily transport instead of Twilio."""

import asyncio
import logging
import os
from typing import Optional

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.base_task import PipelineTaskParams
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
from pipecat.transports.daily.transport import DailyTransport, DailyParams

from ghost_brain.config import Settings, get_settings
from ghost_brain.utils.transcript import format_transcript

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalTestBot:
    """Bot for local testing with microphone using Daily transport."""

    def __init__(self, settings: Settings, room_url: Optional[str] = None):
        """Initialize the local test bot.

        Args:
            settings: Application settings
            room_url: Optional Daily room URL. If not provided, creates a new room.
        """
        self.settings = settings
        self.room_url = room_url
        self.context = LLMContext()
        self.transport: Optional[DailyTransport] = None

    async def setup_transport(self) -> DailyTransport:
        """Setup Daily transport for local microphone/speaker access."""
        params = DailyParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
            audio_in_enabled=True,
            audio_out_enabled=True,
            camera_out_enabled=False,
            microphone_out_enabled=True,
        )

        # Create transport first without joining
        # Note: DailyTransport requires room_url at init, or we can use join() later?
        # Looking at DailyTransport.__init__, it requires room_url.
        # But we might want to create a room first.

        if not self.room_url:
            # DailyTransport doesn't have a create_room method helper usually?
            # We might need to use Daily REST API or just a temp room.
            # For now, let's assume we need a room URL or we can pass a dummy one if we use join later?
            # But the __init__ requires it.
            # Actually, if we look at the code, room_url is required.
            pass

        # If we don't have a room URL, we can't instantiate DailyTransport easily if it enforces it.
        # However, the previous code tried to use transport.create().
        # Let's check if DailyTransport has a create() method.
        # I suspect we need to use `Daily.create_room` or similar if we want to create one.
        # Or just ask the user for a room URL.

        if not self.room_url:
            # Fallback to a hardcoded logic or error?
            # Or maybe we can pass an empty string and join later?
            # Let's try to initialize with empty string if allowed, but it might fail.
            pass

        transport = DailyTransport(
            room_url=self.room_url or "https://api.daily.co/v1/rooms/placeholder",
            token=None,
            bot_name="Ghost Brain",
            params=params,
        )

        # Join or create a Daily room
        if self.room_url:
            await transport.join(self.room_url)
            logger.info(f"Joined existing room: {self.room_url}")
        else:
            # We need to create a room. DailyTransport doesn't seem to have a create() method in the visible code.
            # We might need to use an external helper or just tell the user to provide one.
            # But wait, the previous code had `room = await transport.create()`.
            # Maybe I missed it in BaseTransport or DailyTransport?
            # Let's assume for now we just use the room_url provided or fail.
            logger.error("No room URL provided. Please set DAILY_ROOM_URL or use local_mic_test.py")
            raise ValueError("DAILY_ROOM_URL is required for Daily transport test")

        self.transport = transport
        return transport

    def build_pipeline(self) -> tuple[Pipeline, PipelineTask]:
        """Build the voice pipeline with local transport."""
        if not self.transport:
            raise RuntimeError("Transport not initialized. Call setup_transport first.")

        # Create context and aggregators (16kHz for Daily)
        vad_analyzer = SileroVADAnalyzer(
            sample_rate=16000,
            params=VADParams(stop_secs=0.3),
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
                    "Ask one question at a time and listen before continuing."
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
        pipeline = Pipeline(
            [
                self.transport.input(),
                stt,
                user_aggregator,
                llm,
                tts,
                self.transport.output(),
                assistant_aggregator,
            ]
        )

        params = PipelineParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
        )
        task = PipelineTask(pipeline, params=params)

        return pipeline, task

    async def run(self):
        """Run the local test bot."""
        try:
            # Setup transport
            await self.setup_transport()

            # Build and run pipeline
            pipeline, task = self.build_pipeline()

            logger.info("Starting Ghost Brain local test...")
            logger.info("Speak into your microphone to interact with the bot")
            logger.info("Press Ctrl+C to stop")

            # Run the pipeline
            task_params = PipelineTaskParams(loop=asyncio.get_running_loop())
            await task.run(task_params)

        except KeyboardInterrupt:
            logger.info("\nStopping...")
        except Exception as e:
            logger.exception(f"Error running local test: {e}")
        finally:
            # Save transcript
            if self.context and self.context.get_messages():
                transcript = format_transcript(self.context)

                # Save locally
                filename = "local_test_transcript.txt"
                with open(filename, "w") as f:
                    f.write(transcript)
                logger.info(f"Transcript saved to: {filename}")

                # Also print to console
                print("\n--- Conversation Transcript ---")
                print(transcript)

            # Cleanup
            if self.transport:
                await self.transport.leave()


async def main():
    """Main entry point for local testing."""
    # Load settings
    settings = get_settings()

    # Check for Daily API token (optional - can work without for local testing)
    daily_token = os.getenv("DAILY_API_TOKEN")
    if daily_token:
        os.environ["DAILY_TOKEN"] = daily_token
        logger.info("Daily API token found")
    else:
        logger.warning(
            "No DAILY_API_TOKEN found. Will try to create a room without authentication. "
            "For production use, set DAILY_API_TOKEN environment variable."
        )

    # Optional: specify a room URL to join an existing room
    room_url = os.getenv("DAILY_ROOM_URL")

    # Create and run bot
    bot = LocalTestBot(settings, room_url)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
