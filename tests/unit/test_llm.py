"""Unit tests for LLM service factory."""

from unittest.mock import patch

from ghost_brain.config import Settings
from ghost_brain.services.llm import create_llm


def test_create_llm_system_prompt() -> None:
    """System prompt should include AI name, personality, and greeting."""
    settings = Settings(
        groq_api_key="test-key",
        ai_name="TestBot",
        ai_personality="You are helpful.",
        ai_greeting="Hi, I am {name}.",
    )

    with patch("ghost_brain.services.llm.GroqLLMService") as mock_service:
        create_llm(settings)

        # Verify GroqLLMService.Settings call
        mock_settings_cls = mock_service.Settings
        mock_settings_cls.assert_called_once()
        _, settings_kwargs = mock_settings_cls.call_args
        instruction = settings_kwargs.get("system_instruction")

        # Verify system instruction contains all parts
        assert instruction is not None
        assert "You are TestBot." in instruction
        assert "You are helpful." in instruction
        assert "Hi, I am TestBot." in instruction
