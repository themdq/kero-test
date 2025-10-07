from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes.events import router
from app.deps import get_producer


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.mark.asyncio
async def test_create_event_success(app):
    mock_producer = AsyncMock()
    mock_producer.send_event.return_value = True

    async def override_get_producer():
        return mock_producer

    app.dependency_overrides[get_producer] = override_get_producer

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        event = {
            "user_id": "user-1",
            "event_type": "purchase",
            "event_timestamp": "2025-10-07T10:00:00Z",
            "event_data": {"item_id": "42", "price": 9.99},
        }
        response = await client.post("/events/", json=event)

    assert response.status_code == 202
    assert response.json() == {"status": "accepted"}
    mock_producer.send_event.assert_awaited_once()
