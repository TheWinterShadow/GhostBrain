"""Application configuration management via environment variables and settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings.

    Loads runtime configuration from environment variables and the local `.env` file.
    API keys and external service identifiers are managed here and injected
    via Secret Manager in production deployments.
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="GHOST_BRAIN_", extra="ignore")

    groq_api_key: str = ""
    deepgram_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gcp_bucket_name: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""

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
    Retrieve the singleton application settings instance.

    Returns:
        Settings: The cached configuration settings.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
