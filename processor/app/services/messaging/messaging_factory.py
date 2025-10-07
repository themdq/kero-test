from logging import Logger

from services.messaging.interface.consumer import MessagingConsumer
from services.messaging.kafka.config import (
    KafkaSettings,
)
from services.messaging.kafka.consumer import KafkaMessagingConsumer


class MessagingFactory:
    """Factory for creating messaging service instances"""

    @staticmethod
    def create_consumer(
        logger: Logger,
        config: KafkaSettings | None = None,
        broker_type: str = "kafka",
    ) -> MessagingConsumer:
        """Create a messaging consumer"""
        if broker_type.lower() == "kafka":
            if config is None:
                raise ValueError("Kafka consumer config is required")
            return KafkaMessagingConsumer(logger, config)
        else:
            raise ValueError(f"Unsupported broker type: {broker_type}")
