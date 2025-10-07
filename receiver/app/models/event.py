from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from app.utils.time_conversion import convert_to_iso


class EventData(BaseModel):
    item_id: str
    price: float  # I prefer decimal fields for prices
    tags: List[str] = Field(default_factory=list)


class Event(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: str
    event_data: EventData

    @field_validator("event_timestamp", mode="before")
    def parse_ts(cls, v: datetime | str) -> str:
        if v is None:
            raise ValueError("event_timestamp is required")
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return str(convert_to_iso(v))
            except Exception as e:
                raise ValueError(f"invalid ISO8601 timestamp: {v}") from e
        raise ValueError("event_timestamp must be datetime or ISO string")
