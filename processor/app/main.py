import asyncio
import signal

from config.config import settings
from handlers.event_handler import message_handler_factory
from services.database.database_factory import DatabaseFactory
from services.messaging.messaging_factory import MessagingFactory
from utils.logger import create_logger

logger = create_logger("main")


async def main() -> None:
    # Initialize dependencies
    db = DatabaseFactory.create_database(
        logger=logger, config=settings.postgres, db_type="postgres"
    )
    consumer = MessagingFactory.create_consumer(
        logger=logger, config=settings.kafka, broker_type="kafka"
    )

    await db.connect()
    handler = await message_handler_factory(db)
    await consumer.start(handler)

    # graceful shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _stop() -> None:
        logger.info("Stop requested")
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, _stop)
    loop.add_signal_handler(signal.SIGTERM, _stop)

    await stop_event.wait()
    logger.info("Shutting down...")

    await consumer.stop()
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
