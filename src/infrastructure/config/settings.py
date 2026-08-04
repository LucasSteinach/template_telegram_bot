from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    log_level: str = "INFO"
    fsm_storage: str = ""
    redis_url: str | None = None
    support_user: str | None = None
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8"
    )


settings = Settings()
