from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret: str
    access_exp_sec: int
    refresh_exp_sec: int
    bot_token: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str = "5432"
    db_name: str
    log_level: str = "INFO"
    fsm_storage: str = ""
    redis_url: str | None = None
    support_user: str | None = None
    rabbitmq_url: str | None = None

    @classmethod
    @model_validator(mode='before')
    def assemble_rabbitmq_url(cls, data: dict) -> dict:
        print(data.get("RABBITMQ_URL"))
        if not data.get("RABBITMQ_URL"):
            user = data.get("RABBITMQ_USER")
            password = data.get("RABBITMQ_PASSWORD")
            if user and password:
                data["RABBITMQ_URL"] = f"amqp://{user}:{password}@localhost:5672/"
        return data

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_file_extra="ignore"
    )


settings = Settings()


class ROUTE:
    LOGIN = "/login"
    REFRESH = "/refresh"
    LOGOUT = "/logout"

    OPERATOR = "/operator"
