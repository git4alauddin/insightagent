from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InsightAgent"
    app_version: str = "v1"
    log_level: str = "INFO"

    llm_provider: str = "groq"
    llm_model: str = "llama-3.1-8b-instant"
    llm_api_key: str | None = None
    llm_base_url: str | None = "https://api.groq.com/openai/v1"
    llm_timeout_seconds: float = 30.0

    api_key: str | None = None

    csv_max_file_size_mb: int = 10
    csv_max_rows: int = 100000
    csv_max_columns: int = 200
    upload_dir: str = "uploads"
    allowed_dataset_extensions: tuple[str, ...] = (".csv",)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
