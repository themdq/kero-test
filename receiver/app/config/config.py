from typing import Literal

from app.services.messaging.kafka.config import KafkaSettings
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str = "receiver"

    kafka: KafkaSettings = KafkaSettings()

    model_config = SettingsConfigDict()


settings = Settings()  # type: ignore
