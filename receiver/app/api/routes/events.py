from typing import Any
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter
import uuid

from app.models import Event
from app.core.config import settings

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/") # add response model
async def create_event(
    *, event: Event
) -> Any:
    """
    Create new event.
    """
    event = Event.model_validate(event)
    uid = str(uuid.uuid4())
    answer = await kafka_producer(event.model_dump_json(), uid)
    print(answer)
    return answer

async def kafka_producer(request_data: str, uid: str) -> str:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()
    try:
        answer = await producer.send_and_wait(
            settings.KAFKA_TOPIC,
            f"{uid}:{request_data}".encode("utf-8"), partition=0
        )
    finally:
        await producer.stop()
    return answer