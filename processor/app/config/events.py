from typing import List, Optional

from pydantic import BaseModel, Field


class EventFilterSettings(BaseModel):
    allowed_types: Optional[List[str]] = Field(
        default=["purchase"],
        description="Allowed types for events",
    )
    denied_types: Optional[List[str]] = Field(
        default=None, description="Denied types for events"
    )
    commit_skipped: bool = Field(
        default=True, description="Commit offset if message skipped"
    )
