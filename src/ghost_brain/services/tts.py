"""TTS Service factory."""

from pipecat.services.openai.tts import OpenAITTSService

from ghost_brain.config import Settings


def create_tts(settings: Settings) -> OpenAITTSService:
    """
    Create OpenAI TTS service (tts-1, voice alloy).

    Args:
        settings: Application settings containing OpenAI API key.

    Returns:
        Configured OpenAITTSService instance.
    """
    return OpenAITTSService(
        api_key=settings.openai_api_key,
        settings=OpenAITTSService.Settings(
            voice="alloy",
            model="tts-1",
        ),
    )
