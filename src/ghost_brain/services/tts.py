"""TTS Service factory."""

from pipecat.services.deepgram.tts import DeepgramTTSService

from ghost_brain.config import Settings


def create_tts(settings: Settings) -> DeepgramTTSService:
    """
    Create Deepgram TTS service (aura-2-orpheus-en).

    Args:
        settings: Application settings containing Deepgram API key.

    Returns:
        Configured DeepgramTTSService instance.
    """
    return DeepgramTTSService(
        api_key=settings.deepgram_api_key,
        voice="aura-2-orpheus-en",
        sample_rate=8000,
    )
