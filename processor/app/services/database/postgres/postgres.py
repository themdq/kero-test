import json
from datetime import datetime
from logging import Logger

import asyncpg
from services.database.interface.database import DBService
from services.database.postgres.config import PostgresSettings


class PostgresDatabase(DBService):
    def __init__(self, logger: Logger, config: PostgresSettings):
        self.logger = logger
        self.config = config
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.config.dsn.encoded_string(), init=self._init_connection
            )
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_timestamp TIMESTAMPTZ NOT NULL,
                    event_data JSONB NOT NULL,
                    UNIQUE (user_id, event_type, event_timestamp)
                );
            """)
        self.logger.info("✅ PostgreSQL connected")

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.logger.info("🛑 PostgreSQL disconnected")

    async def _init_connection(self, conn: asyncpg.Connection) -> None:
        """Настраивает кодеки и другие параметры соединения"""
        await conn.set_type_codec(
            "json",
            encoder=json.dumps,
            decoder=json.loads,
            schema="pg_catalog",
        )

    async def save_event(
        self,
        user_id: str,
        event_type: str,
        event_timestamp: datetime,
        event_data: dict,
    ) -> bool:
        if not self.pool:
            raise RuntimeError("Database not connected")

        async with self.pool.acquire() as conn:
            row_id = await conn.fetchval(
                """
                INSERT INTO events (user_id, event_type, event_timestamp, event_data)
                VALUES ($1, $2, $3, $4::json)
                ON CONFLICT (user_id, event_type, event_timestamp) DO NOTHING
                RETURNING id
                """,
                user_id,
                event_type,
                event_timestamp,
                event_data,
            )
            return bool(row_id)
