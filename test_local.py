#!/usr/bin/env python
"""
Quick local test of the GhostBrain pipeline components without Twilio.
This script tests that all the AI services are working correctly.
"""

from ghost_brain.pipeline import create_stt, create_llm, create_tts
from ghost_brain.config import get_settings
import asyncio
import logging
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_pipeline():
    """Test the pipeline components independently."""

    print("\n" + "=" * 60)
    print("🧪 GhostBrain Component Test")
    print("=" * 60)

    # Load settings
    try:
        settings = get_settings()
        print("✅ Settings loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        print("\nMake sure you have a .env file with:")
        print("  GHOST_BRAIN_DEEPGRAM_API_KEY=...")
        print("  GHOST_BRAIN_GROQ_API_KEY=...")
        print("  GHOST_BRAIN_OPENAI_API_KEY=...")
        return

    # Test STT
    print("\n📝 Testing Speech-to-Text (Deepgram)...")
    try:
        stt = create_stt(settings)
        print("✅ STT service created successfully")
    except Exception as e:
        print(f"❌ STT failed: {e}")
        return

    # Test LLM
    print("\n🤖 Testing Language Model (Groq)...")
    try:
        llm = create_llm(settings)
        print("✅ LLM service created successfully")

        # Test a simple completion
        from pipecat.processors.aggregators.llm_context import LLMContext

        context = LLMContext()
        context.add_message(
            {"role": "user", "content": "Say hello in exactly 5 words."})

        # Note: Actually running the LLM would require the full pipeline
        # For now, just verify it's configured correctly
        print("   Model: llama-3.3-70b-versatile")
        print("   Provider: Groq")

    except Exception as e:
        print(f"❌ LLM failed: {e}")
        return

    # Test TTS
    print("\n🔊 Testing Text-to-Speech (OpenAI)...")
    try:
        tts = create_tts(settings)
        print("✅ TTS service created successfully")
        print("   Voice: alloy")
        print("   Model: tts-1")
    except Exception as e:
        print(f"❌ TTS failed: {e}")
        return

    print("\n" + "=" * 60)
    print("✨ All components initialized successfully!")
    print("=" * 60)
    print("\nTo test with your microphone, you'll need to:")
    print("1. Set up a Twilio phone number")
    print("2. Configure webhooks to point to your server")
    print("3. Run: hatch run uvicorn ghost_brain.app:app --port 8080")
    print("\nOr wait for the PyAudio-based local test to be implemented.")


if __name__ == "__main__":
    asyncio.run(test_pipeline())
