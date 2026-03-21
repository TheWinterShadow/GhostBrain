"""Pytest fixtures and configuration for Ghost Brain tests."""

import os
from unittest.mock import MagicMock

import pytest

from ghost_brain.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    """Settings with non-empty stub values for testing."""
    return Settings(
        groq_api_key="test-groq",
        deepgram_api_key="test-deepgram",
        openai_api_key="test-openai",
        gcp_bucket_name="test-bucket",
        twilio_account_sid="test-sid",
        twilio_auth_token="test-token",
    )


@pytest.fixture
def sample_messages() -> list[dict]:
    """Sample conversation messages (OpenAI-style) for transcript tests."""
    return [
        {"role": "user", "content": "Hello."},
        {"role": "assistant", "content": "Hi! How can I help you today?"},
        {"role": "user", "content": "I'd like to schedule an interview."},
    ]


@pytest.fixture(autouse=True)
def reset_settings_cache() -> None:
    """Reset the global settings cache so tests get fresh Settings."""
    import ghost_brain.config as config_module
    config_module._settings = None
    yield
    config_module._settings = None


@pytest.fixture
def mock_storage_bucket() -> MagicMock:
    """Mock GCS bucket and blob for upload tests."""
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    return mock_bucket
