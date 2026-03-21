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
    ai_name: str = "Ghost Brain"
    ai_personality: str = (
        "You are a friendly voice interviewer. "
        "Keep responses concise and natural for spoken conversation. "
        "Ask one question at a time and listen before continuing."
    )
    ai_greeting: str = "Hello, this is {name}. I'm here to interview you."


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
