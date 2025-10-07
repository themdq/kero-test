import json
from logging import Logger
from typing import Any

from aiokafka import AIOKafkaProducer  # type: ignore

from app.services.messaging.interface.producer import MessagingProducer
from app.services.messaging.kafka.config import KafkaSettings


class KafkaMessagingProducer(MessagingProducer):
    """Kafka implementation of messaging producer"""

    def __init__(self, logger: Logger, kafka_config: KafkaSettings) -> None:
        self.logger = logger
        self.producer: AIOKafkaProducer | None = None
        self.kafka_config = kafka_config
        self.processed_messages: dict[str, list[int]] = {}

    async def initialize(self) -> None:
        """Initialize the Kafka producer"""
        try:
            if not self.kafka_config:
                raise ValueError("Kafka configuration is not valid")

            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.kafka_config.bootstrap_servers,
                client_id=self.kafka_config.client_id,
            )
            await self.producer.start()
            self.logger.info(
                f"✅ Kafka producer initialized and started with client_id: {self.kafka_config.client_id}"
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Kafka producer: {str(e)}")
            raise

    async def cleanup(self) -> None:
        """Stop the Kafka producer and clean up resources"""
        if self.producer:
            try:
                await self.producer.stop()
                self.producer = None
                self.logger.info("✅ Kafka producer stopped successfully")
            except Exception as e:
                self.logger.error(f"❌ Error stopping Kafka producer: {str(e)}")

    async def start(self) -> None:
        """Start the Kafka producer"""
        if self.producer is None:
            await self.initialize()

    async def stop(self) -> None:
        """Stop the Kafka producer"""
        if self.producer:
            await self.cleanup()

    async def send_message(
        self, topic: str, message: dict[str, Any], key: str | None = None
    ) -> bool:
        """Send a message to a Kafka topic"""
        try:
            if self.producer is None:
                await self.initialize()

            message_value = json.dumps(message).encode("utf-8")
            message_key = key.encode("utf-8") if key else None

            record_metadata = await self.producer.send_and_wait(  # type: ignore
                topic=topic, key=message_key, value=message_value
            )

            self.logger.info(
                "✅ Message successfully produced to %s [%s] at offset %s",
                record_metadata.topic,
                record_metadata.partition,
                record_metadata.offset,
            )

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to send message to Kafka: {str(e)}")
            return False

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
        try:
            # Prepare the message
            message = {
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data,
                "event_timestamp": event_timestamp,
            }

            # Send the message to sync-events topic using aiokafka
            await self.send_message(topic=topic, message=message, key=key)

            self.logger.info(
                f"Successfully sent event with type: {event_type} to topic: {topic}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error sending sync event: {str(e)}")
            return False
