from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator


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
            s = v.strip()
            # replace Z with +00:00 for fromisoformat
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            try:
                return datetime.fromisoformat(s)
            except Exception as e:
                raise ValueError(f"invalid ISO8601 timestamp: {v}") from e
        raise ValueError("event_timestamp must be datetime or ISO string")
