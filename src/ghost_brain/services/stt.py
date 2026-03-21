"""STT Service factory."""

from pipecat.services.deepgram.stt import DeepgramSTTService

from ghost_brain.config import Settings


def create_stt(settings: Settings) -> DeepgramSTTService:
    """
    Create Deepgram STT service (nova-2 model).

    Args:
        settings: Application settings containing Deepgram API key.

    Returns:
        Configured DeepgramSTTService instance.
    """
    return DeepgramSTTService(
        api_key=settings.deepgram_api_key,
        settings=DeepgramSTTService.Settings(model="nova-2"),
    )
