from unittest.mock import AsyncMock

import pytest

from config.config import settings
from handlers.event_handler import _passes_type_filter, message_handler_factory


@pytest.fixture
def fake_settings(monkeypatch):
    from config.events import EventFilterSettings

    fake = EventFilterSettings(
        allowed_types=["purchase"],
        denied_types=["spam", "view"],
        commit_skipped=True,
    )
    monkeypatch.setattr(settings, "events", fake)
    return fake


@pytest.mark.asyncio
async def test_passes_type_filter(fake_settings):
    assert _passes_type_filter("purchase") is True
    assert _passes_type_filter("click") is False
    assert _passes_type_filter("spam") is False


@pytest.mark.asyncio
async def test_message_handler_valid_event(fake_settings):
    mock_db = AsyncMock()
    mock_db.save_event.return_value = True

    handler = await message_handler_factory(mock_db)
    msg = {
        "user_id": "user-123",
        "event_type": "purchase",
        "event_timestamp": "2025-10-07T12:00:00Z",
        "event_data": {"item_id": "item-42", "price": 9.99},
    }

    result = await handler(msg)

    assert result is True
    mock_db.save_event.assert_awaited_once()

    _, kwargs = mock_db.save_event.call_args
    assert kwargs["event_type"] == "purchase"
    assert kwargs["user_id"] == "user-123"
    assert isinstance(kwargs["event_data"], dict)