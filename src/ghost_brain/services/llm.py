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
    greeting = settings.ai_greeting.format(name=settings.ai_name)
    system_prompt = (
        f"You are {settings.ai_name}. {settings.system_instructions} "
        "When greeting the user for the first time, introduce yourself "
        f"using exactly these words: '{greeting}'."
    )

    return GroqLLMService(
        api_key=settings.groq_api_key,
        settings=GroqLLMService.Settings(
            model="llama-3.1-8b-instant",
            system_instruction=system_prompt,
        ),
    )
