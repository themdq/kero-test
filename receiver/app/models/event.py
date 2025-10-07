from pydantic import BaseModel


class EventData(BaseModel):
    item_id: str
    price: float # I prefer decimal fields for prices
    tags: list[str]

class Event(BaseModel):
    user_id: str
    event_type: str
    event_timestamp: str # ADD Validation
    event_data: EventData
