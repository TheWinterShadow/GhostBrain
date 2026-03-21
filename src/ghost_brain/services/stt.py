"""STT Service factory."""

from pipecat.services.deepgram.stt import DeepgramSTTService

from ghost_brain.config import Settings


def create_stt(settings: Settings, sample_rate: int = 16000) -> DeepgramSTTService:
    """
    Create Deepgram STT service (nova-2 model).

    Args:
        settings: Application settings containing Deepgram API key.
        sample_rate: Audio sample rate (default 16000).

    Returns:
        Configured DeepgramSTTService instance.
    """
    return DeepgramSTTService(
        api_key=settings.deepgram_api_key,
        sample_rate=sample_rate,
        settings=DeepgramSTTService.Settings(model="nova-2"),
    )
