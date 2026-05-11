from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InsightAgent"
    app_version: str = "v6"
    app_env: str = "development"
    log_level: str = "INFO"
    docs_enabled: bool = True
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60
    rate_limit_uploads_per_minute: int = 5
    rate_limit_window_seconds: int = 60

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
    document_max_file_size_mb: int = 20
    allowed_document_extensions: tuple[str, ...] = (".pdf", ".txt", ".md")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_cors_allowed_origins(self) -> list[str]:
        origins = [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

        if self.app_env.lower() == "production" and "*" in origins:
            raise ValueError("Wildcard CORS origins are not allowed in production.")

        return origins


settings = Settings()
