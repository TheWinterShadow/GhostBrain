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
    system_prompt = (
        f"You are {settings.ai_name}. {settings.ai_personality} "
        "When greeting the user for the first time, introduce yourself "
        f"using the name {settings.ai_name}."
    )

    return GroqLLMService(
        api_key=settings.groq_api_key,
        settings=GroqLLMService.Settings(
            model="llama-3.3-70b-versatile",
            system_instruction=system_prompt,
        ),
    )
