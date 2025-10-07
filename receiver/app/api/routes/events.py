from typing import Any

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter

from app.core.config import settings
from app.models import Event

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/")  # add response model
async def create_event(*, event: Event) -> Any:
    """
    Create new event.
    """
    event = Event.model_validate(event)
    answer = await kafka_producer(event.model_dump_json())
    print(answer)
    return answer


async def kafka_producer(request_data: str) -> str:
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    try:
        answer = await producer.send_and_wait(
            settings.KAFKA_TOPIC, f"{request_data}".encode("utf-8"), partition=0
        )
    finally:
        await producer.stop()
    return answer
