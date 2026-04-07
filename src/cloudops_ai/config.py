"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM Backend ("anthropic" or "ollama")
    llm_backend: str = "ollama"  # Default to Ollama

    # Anthropic (only used if llm_backend == "anthropic")
    anthropic_api_key: str = ""

    # Ollama (only used if llm_backend == "ollama")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:7b"  # lightweight for classification

    # Azure
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_subscription_id: str = ""

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    webhook_secret: str = "change-me-in-production"

    # LLM (legacy, kept for backward compat)
    classifier_model: str = "claude-haiku-4-5"
    classifier_max_tokens: int = 128  # clasificación es corta


settings = Settings()  # type: ignore[call-arg]
