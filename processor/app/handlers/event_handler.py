import logging
from typing import Any, Callable

from app.config.config import settings
from app.models.event import EventIn
from app.services.database.interface.database import DBService

logger = logging.getLogger("handler")


def _passes_type_filter(event_type: str | None) -> bool:
    if event_type is None:
        return False

    if settings.events.allowed_types:
        return event_type in set(settings.events.allowed_types)

    if settings.events.denied_types:
        if event_type in set(settings.events.denied_types):
            return False

    return True


async def message_handler_factory(db: DBService) -> Callable:
    async def handler(msg: dict[str, Any]) -> bool:
        evt_type = msg.get("event_type")

        if not _passes_type_filter(evt_type):
            logger.info("Event type '%s' filtered out", evt_type)
            return bool(settings.events.commit_skipped)

        # Validation
        try:
            event = EventIn(**msg)
        except Exception as e:
            logger.exception("Validation error for message: %s", e)
            return False

        # Save in database
        try:
            inserted = await db.save_event(
                user_id=event.user_id,
                event_type=event.event_type,
                event_timestamp=event.event_timestamp,
                event_data=event.event_data.model_dump(),
            )
            logger.info(
                "Event processed: user=%s type=%s ts=%s inserted=%s",
                event.user_id,
                event.event_type,
                event.event_timestamp.isoformat(),
                inserted,
            )

            return True
        except Exception as e:
            logger.exception("DB error while saving event: %s", e)
            return False

    return handler
