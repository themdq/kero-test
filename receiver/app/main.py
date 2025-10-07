from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.config.config import settings
from app.services.messaging.messaging_factory import MessagingFactory
from app.utils.logger import create_logger


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


logger = create_logger("app")
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Create producer via factory
    producer = MessagingFactory.create_producer(
        logger=logger, config=settings.kafka, broker_type="kafka"
    )
    # start (connect) producer
    await producer.start()
    # attach to app.state for DI
    app.state.messaging_producer = producer
    logger.info("Application startup complete")
    try:
        yield
    finally:
        logger.info("Application shutdown: stopping producer")
        try:
            await producer.stop()
        except Exception:
            logger.exception("Error stopping producer")
        logger.info("Shutdown complete")


app.router.lifespan_context = lifespan  # register lifespan

app.include_router(api_router, prefix=settings.API_V1_STR)
