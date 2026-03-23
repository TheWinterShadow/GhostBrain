"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings loaded from environment (and .env).

    All API keys and the GCS bucket name are read from the environment.
    In production these are typically injected via Secret Manager (Cloud Run).
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GHOST_BRAIN_", extra="ignore")

    groq_api_key: str = ""
    deepgram_api_key: str = ""
    openai_api_key: str = ""
    gcp_bucket_name: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

    # Personality Configuration
    ai_name: str = "Orion"
    allowed_caller_id: str = ""
    system_instructions: str = (
        f"You are {ai_name} — Eli's trusted thinking partner "
        "and friend. You help him work through ideas, "
        "brainstorm, debug complex technical challenges, and generally "
        "process his thoughts. "
        "\n\n"
        "Your tone should be highly conversational, informal, and direct. "
        "Avoid overly verbose or 'assistant-like' language. Talk like a "
        "peer and a friend. Keep responses reasonably concise so they work "
        "well in a spoken, back-and-forth voice format."
    )
    ai_greeting: str = f"Hello, this is {ai_name}. How can I help you?"


_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Return cached settings; load from env on first call.

    Returns:
        Settings: The application settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
