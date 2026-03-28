"""Unit tests for LLM service factory."""

from unittest.mock import patch

from ghost_brain.config import Settings
from ghost_brain.modules.ai.llm import create_llm


def test_create_llm_system_prompt() -> None:
    """Include AI name, personality, and greeting in system prompt."""
    settings = Settings(
        groq_api_key="test-key",
        ai_name="TestBot",
        system_instructions="You are helpful.",
        ai_greeting="Hi, I am {name}.",
    )

    with patch("ghost_brain.modules.ai.llm.GroqLLMService") as mock_service:
        create_llm(settings)

        mock_settings_cls = mock_service.Settings
        mock_settings_cls.assert_called_once()
        _, settings_kwargs = mock_settings_cls.call_args
        instruction = settings_kwargs.get("system_instruction")

        assert instruction is not None
        assert "You are TestBot." in instruction
        assert "You are helpful." in instruction
        assert "Hi, I am TestBot." in instruction
