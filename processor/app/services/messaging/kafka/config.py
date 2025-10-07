from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = Field(default="kafka:9092")
    group_id: str = Field(default="consumer_group")
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    client_id: str = ""
    topics: list = Field(default=["incoming_events"])

    model_config = SettingsConfigDict(env_prefix="KAFKA_")
