from abc import ABC, abstractmethod
from typing import Any


class MessagingProducer(ABC):
    """Interface for messaging producers"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the messaging producer"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources"""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the messaging producer"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the messaging producer"""
        pass

    @abstractmethod
    async def send_message(
        self, topic: str, message: dict[str, Any], key: str | None = None
    ) -> bool:
        """Send a message to a topic"""
        pass

    @abstractmethod
    async def send_event(
        self,
        topic: str,
        event_type: str,
        event_timestamp: str,
        user_id: str,
        event_data: dict[str, Any],
        key: str | None = None,
    ) -> bool:
        """Send an event message with standardized format"""
        pass
