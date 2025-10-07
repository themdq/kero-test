from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.services.messaging.kafka.config import KafkaSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str = "receiver"

    kafka: KafkaSettings = KafkaSettings()

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()  # type: ignore
