from logging import Logger
from typing import Union

from services.database.interface.database import DBService
from services.database.postgres.config import PostgresSettings
from services.database.postgres.postgres import PostgresDatabase


class DatabaseFactory:
    """Factory for creating database instances"""

    @staticmethod
    def create_database(
        logger: Logger,
        config: Union[PostgresSettings, None] = PostgresSettings,
        db_type: str = "postgres",
    ) -> DBService:
        """Create a database connection"""
        if db_type.lower() == "postgres":
            if config is None:
                raise ValueError("Postgres config is required")
            return PostgresDatabase(logger, config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
