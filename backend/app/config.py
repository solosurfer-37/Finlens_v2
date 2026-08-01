from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the FinLens backend.

    Every environment variable is loaded from the .env file
    and can be accessed anywhere using the `settings` object.
    """

    # ==========================
    # Application
    # ==========================

    app_name: str = "FinLens Backend"
    app_version: str = "1.0.0"
    debug: bool = True

    # ==========================
    # Database
    # ==========================

    database_url: str

    # ==========================
    # AI
    # ==========================

    gemini_api_key: str

    # ==========================
    # Security
    # ==========================

    secret_key: str

    algorithm: str = "HS256"

    access_token_expire_minutes: int = 60

    # ==========================
    # File Uploads
    # ==========================

    upload_directory: str = "uploads"

    max_upload_size_mb: int = 100

    # ==========================
    # CORS
    # ==========================

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ]

    # ==========================
    # Environment Configuration
    # ==========================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()