from logging import Logger

from app.services.messaging.interface.producer import MessagingProducer
from app.services.messaging.kafka.config import (
    KafkaSettings,
)
from app.services.messaging.kafka.producer import KafkaMessagingProducer


class MessagingFactory:
    """Factory for creating messaging service instances"""

    @staticmethod
    def create_producer(
        logger: Logger,
        config: KafkaSettings | None = None,
        broker_type: str = "kafka",
    ) -> MessagingProducer:
        """Create a messaging producer"""
        if broker_type.lower() == "kafka":
            if config is None:
                raise ValueError("Kafka producer config is required")
            return KafkaMessagingProducer(logger, config)
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")
