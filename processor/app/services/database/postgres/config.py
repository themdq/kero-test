from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    user: str = Field(default="admin")
    password: str = Field(default="admin")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    database: str = Field(default="processor")

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_", env_file=".env", extra="ignore"
    )

    @computed_field  # type: ignore[misc]
    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        )
