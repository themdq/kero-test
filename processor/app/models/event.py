from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator
from app.utils.time_conversion import parse_timestamp

class EventPayload(BaseModel):
    item_id: str
    price: float
    tags: List[str] = Field(default_factory=list)


class EventIn(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: datetime
    event_data: EventPayload

    @field_validator("event_timestamp", mode="before")
    def parse_ts(cls, v: datetime | str) -> datetime:
        if v is None:
            raise ValueError("event_timestamp is required")
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return parse_timestamp(v)
            except Exception as e:
                raise ValueError(f"invalid ISO8601 timestamp: {v}") from e
        raise ValueError("event_timestamp must be datetime or ISO string")
