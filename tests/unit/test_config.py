"""Unit tests for ghostwriter.config."""

import os

import pytest

from ghostwriter.config import Settings, get_settings


def test_settings_loads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings should read values from environment variables."""
    monkeypatch.setenv("GROQ_API_KEY", "env-groq")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "env-dg")
    monkeypatch.setenv("OPENAI_API_KEY", "env-openai")
    monkeypatch.setenv("GCP_BUCKET_NAME", "env-bucket")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "env-sid")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "env-token")
    # Clear cache so we get fresh load
    import ghostwriter.config as m
    m._settings = None
    s = get_settings()
    assert s.groq_api_key == "env-groq"
    assert s.deepgram_api_key == "env-dg"
    assert s.openai_api_key == "env-openai"
    assert s.gcp_bucket_name == "env-bucket"
    assert s.twilio_account_sid == "env-sid"
    assert s.twilio_auth_token == "env-token"


def test_settings_defaults() -> None:
    """Settings should have empty string defaults when env is unset."""
    import ghostwriter.config as m
    m._settings = None
    # Ensure no env vars are set for these (or unset them)
    for key in ("GROQ_API_KEY", "DEEPGRAM_API_KEY", "OPENAI_API_KEY",
                "GCP_BUCKET_NAME", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"):
        os.environ.pop(key, None)
    s = Settings()
    assert s.groq_api_key == ""
    assert s.gcp_bucket_name == ""


def test_get_settings_caches() -> None:
    """get_settings should return the same instance on subsequent calls."""
    import ghostwriter.config as m
    m._settings = None
    a = get_settings()
    b = get_settings()
    assert a is b
