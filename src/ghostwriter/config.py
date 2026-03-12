"""Application configuration from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings loaded from environment (and .env).

    All API keys and the GCS bucket name are read from the environment.
    In production these are typically injected via Secret Manager (Cloud Run).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = ""
    deepgram_api_key: str = ""
    openai_api_key: str = ""
    gcp_bucket_name: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""


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
