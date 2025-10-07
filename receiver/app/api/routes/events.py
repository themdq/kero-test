from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.config.config import settings
from app.deps import get_producer
from app.models.event import Event
from app.services.messaging.interface.producer import MessagingProducer
from app.utils.logger import create_logger

logger = create_logger("events")
router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", status_code=202)  # add response model
async def create_event(
    *, event: Event, producer: MessagingProducer = Depends(get_producer)
) -> Any:
    """
    Accept event and publish to Kafka. Returns 202 Accepted on success, 500 on failed produce.
    """

    # normalize payload to dict:
    payload_dict = event.model_dump()

    ok = await producer.send_event(
        topic=settings.kafka.topics[0],
        event_type=payload_dict.get("event_type"),
        event_data=payload_dict.get("event_data") or {},
        event_timestamp=payload_dict.get("event_timestamp"),
        user_id=payload_dict.get("user_id"),
        key=payload_dict.get("user_id"),
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to produce message")
    return {"status": "accepted"}
