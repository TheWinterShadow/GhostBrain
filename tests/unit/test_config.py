"""Unit tests for ghost_brain.config."""

import os

import pytest

from ghost_brain.config import Settings, get_settings


def test_settings_loads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read values from environment variables."""
    monkeypatch.setenv("GHOST_BRAIN_GROQ_API_KEY", "env-groq")
    monkeypatch.setenv("GHOST_BRAIN_DEEPGRAM_API_KEY", "env-dg")
    monkeypatch.setenv("GHOST_BRAIN_OPENAI_API_KEY", "env-openai")
    monkeypatch.setenv("GHOST_BRAIN_GCP_BUCKET_NAME", "env-bucket")
    monkeypatch.setenv("GHOST_BRAIN_TWILIO_ACCOUNT_SID", "env-sid")
    monkeypatch.setenv("GHOST_BRAIN_TWILIO_AUTH_TOKEN", "env-token")

    import ghost_brain.config as m

    m._settings = None
    s = get_settings()
    assert s.groq_api_key == "env-groq"
    assert s.deepgram_api_key == "env-dg"
    assert s.openai_api_key == "env-openai"
    assert s.gcp_bucket_name == "env-bucket"
    assert s.twilio_account_sid == "env-sid"
    assert s.twilio_auth_token == "env-token"


def test_settings_personality(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow overriding personality configuration."""
    monkeypatch.setenv("GHOST_BRAIN_AI_NAME", "Jarvis")
    monkeypatch.setenv("GHOST_BRAIN_SYSTEM_INSTRUCTIONS", "You are sarcastic.")
    monkeypatch.setenv("GHOST_BRAIN_AI_GREETING", "Greetings, human.")

    import ghost_brain.config as m

    m._settings = None
    s = get_settings()

    assert s.ai_name == "Jarvis"
    assert s.system_instructions == "You are sarcastic."
    assert s.ai_greeting == "Greetings, human."


def test_settings_defaults() -> None:
    """Default to empty strings when env is unset."""
    import ghost_brain.config as m

    m._settings = None

    for key in list(os.environ.keys()):
        if key.startswith("GHOST_BRAIN_"):
            os.environ.pop(key)

    s = Settings(_env_file=None)

    assert s.groq_api_key == ""
    assert s.gcp_bucket_name == ""


def test_get_settings_caches() -> None:
    """get_settings should return the same instance on subsequent calls."""
    import ghost_brain.config as m

    m._settings = None
    a = get_settings()
    b = get_settings()
    assert a is b
