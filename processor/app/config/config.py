from app.config.events import EventFilterSettings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.services.database.postgres.config import PostgresSettings
from app.services.messaging.kafka.config import KafkaSettings


class AppSettings(BaseSettings):
    env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    kafka: KafkaSettings = KafkaSettings()
    postgres: PostgresSettings = PostgresSettings()
    events: EventFilterSettings = EventFilterSettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = AppSettings()
