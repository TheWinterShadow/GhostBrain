"""LLM Service factory."""

from pipecat.services.groq.llm import GroqLLMService

from ghost_brain.config import Settings


def create_llm(settings: Settings) -> GroqLLMService:
    """
    Create Groq LLM service (llama-3.3-70b-versatile).

    Args:
        settings: Application settings containing Groq API key.

    Returns:
        Configured GroqLLMService instance with system instructions.
    """
    return GroqLLMService(
        api_key=settings.groq_api_key,
        settings=GroqLLMService.Settings(
            model="llama-3.3-70b-versatile",
            system_instruction=(
                "You are Ghost Brain, a friendly voice interviewer. "
                "Keep responses concise and natural for spoken conversation. "
                "Ask one question at a time and listen before continuing."
            ),
        ),
    )
