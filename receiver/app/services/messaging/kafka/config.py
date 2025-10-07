from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = Field(default="kafka:9092")
    client_id: str = "123"
    topics: list = Field(default=["incoming_events"])

    model_config = SettingsConfigDict(
        env_prefix="KAFKA_", env_file=".env", extra="ignore"
    )
