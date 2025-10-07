import asyncio
import json
from logging import Logger
from typing import Any, Awaitable, Callable, Dict, Optional, Set

from aiokafka import AIOKafkaConsumer, TopicPartition  # type: ignore
from aiokafka.structs import ConsumerRecord  # type: ignore
from services.messaging.interface.consumer import MessagingConsumer
from services.messaging.kafka.config import KafkaSettings

MAX_CONCURRENT_TASKS = 5


class KafkaMessagingConsumer(MessagingConsumer):
    """
    Kafka consumer that accepts a message_handler(msg_dict) -> Awaitable[bool]
    and does commits only on successful processing.
    """

    def __init__(
        self,
        logger: Logger,
        kafka_config: KafkaSettings,
        max_concurrency: int = MAX_CONCURRENT_TASKS,
    ) -> None:
        self.logger = logger
        self.kafka_config = kafka_config
        self.consumer: Optional[AIOKafkaConsumer] = None

        self._running = False
        self._consume_task: Optional[asyncio.Task] = None
        self.message_handler: Optional[Callable[[Dict[str, Any]], Awaitable[bool]]] = (
            None
        )

        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._active_tasks: Set[asyncio.Task] = set()
        # processed offsets per topic-partition: "topic-partition" -> set(offsets)
        self._processed_offsets: Dict[str, Set[int]] = {}

    def is_running(self) -> bool:
        """Check if consumer is running"""
        return self._running

    async def initialize(self) -> None:
        """Initialize the Kafka consumer"""
        try:
            if not self.kafka_config:
                raise ValueError("Kafka configuration is not valid")

            # Convert KafkaConsumerConfig to dictionary format for aiokafka
            kafka_dict = self.kafka_config.model_dump()
            topics = kafka_dict.pop("topics")

            # Initialize consumer with aiokafka
            self.consumer = AIOKafkaConsumer(*topics, **kafka_dict)

            await self.consumer.start()  # type: ignore
            self.logger.info("Successfully initialized aiokafka consumer")
        except Exception as e:
            self.logger.error(f"Failed to create consumer: {e}")
            raise

    async def cleanup(self) -> None:
        # wait running background tasks to finish or cancel them
        # cancel active tasks if still running
        for t in list(self._active_tasks):
            if not t.done():
                t.cancel()
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)
            self._active_tasks.clear()

        if self.consumer:
            try:
                await self.consumer.stop()
                self.logger.info("Kafka consumer stopped (cleanup)")
            except Exception as e:
                self.logger.exception("Error stopping consumer: %s", e)
            finally:
                self.consumer = None

    async def start(
        self, message_handler: Callable[[Dict[str, Any]], Awaitable[bool]]
    ) -> None:
        """Start consuming messages with the provided handler"""
        try:
            self._running = True
            self.message_handler = message_handler

            # initialize consumer
            if not self.consumer:
                await self.initialize()

            # create a task for consuming messages
            self._consume_task = asyncio.create_task(self.__consume_loop())
            self.logger.info("Started Kafka consumer task")
        except Exception as e:
            self.logger.error(f"Failed to start Kafka consumer: {str(e)}")
            raise

    async def stop(self) -> None:
        """Request stop and wait for loop + tasks to finish."""
        self._running = False
        # cancel the consume loop task (it will call cleanup in finally)
        if self._consume_task:
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
            except Exception:
                self.logger.exception("Error awaiting consume task")

    def _is_processed(self, topic: str, partition: int, offset: int) -> bool:
        key = f"{topic}-{partition}"
        return key in self._processed_offsets and offset in self._processed_offsets[key]

    def _mark_processed(self, topic: str, partition: int, offset: int) -> None:
        key = f"{topic}-{partition}"
        s = self._processed_offsets.setdefault(key, set())
        s.add(offset)

    async def _process_and_commit(self, rec: ConsumerRecord) -> None:
        """Wrapper to process a message, commit on success and mark offset."""
        topic = rec.topic
        partition = rec.partition
        offset = rec.offset
        tp = TopicPartition(topic, partition)
        message_id = f"{topic}-{partition}-{offset}"

        try:
            # parse
            value = rec.value
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8")
                except Exception as e:
                    self.logger.error(
                        "Failed to decode bytes for %s: %s", message_id, e
                    )
                    return
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    # handle double-encoded JSON
                    if isinstance(parsed, str):
                        parsed = json.loads(parsed)
                except json.JSONDecodeError as e:
                    self.logger.error("JSON parse error for %s: %s", message_id, e)
                    return
            elif isinstance(value, dict):
                parsed = value
            else:
                self.logger.error(
                    "Unsupported message type for %s: %s", message_id, type(value)
                )
                return

            # call handler
            if self.message_handler is None:
                self.logger.error("No message handler provided")
                return

            success = await self.message_handler(parsed)
            if success:
                # commit offset (next offset)
                try:
                    if self.consumer:
                        await self.consumer.commit({tp: offset + 1})
                        self._mark_processed(topic, partition, offset)
                        self.logger.info("Processed & committed %s", message_id)
                except Exception as e:
                    self.logger.exception(
                        "Failed to commit offset for %s: %s", message_id, e
                    )
            else:
                self.logger.warning(
                    "Handler returned failure for %s; not committing", message_id
                )

        except Exception as e:
            self.logger.exception("Unhandled error processing %s: %s", message_id, e)
        finally:
            # Release semaphore slot is done by wrapper
            pass

    async def __consume_loop(self) -> None:
        try:
            self.logger.info("Entering consume loop")
            assert self.consumer is not None

            while self._running:
                try:
                    batch = await self.consumer.getmany(timeout_ms=1000, max_records=10)
                    if not batch:
                        await asyncio.sleep(0.1)
                        continue

                    for tp, records in batch.items():
                        for rec in records:
                            if self._is_processed(rec.topic, rec.partition, rec.offset):
                                self.logger.debug(
                                    "Skipping already processed %s-%s-%s",
                                    rec.topic,
                                    rec.partition,
                                    rec.offset,
                                )
                                continue

                            # concurrency control
                            await self._semaphore.acquire()

                            task = asyncio.create_task(self._task_wrapper(rec))
                            self._active_tasks.add(task)
                            # cleanup done tasks
                            self._cleanup_tasks()

                except asyncio.CancelledError:
                    self.logger.info("Consume loop cancelled")
                    break
                except Exception as e:
                    self.logger.exception("Error in consume loop: %s", e)
                    await asyncio.sleep(1)

        finally:
            await self.cleanup()

    async def _task_wrapper(self, rec: ConsumerRecord) -> None:
        try:
            await self._process_and_commit(rec)
        finally:
            self._semaphore.release()

    def _cleanup_tasks(self) -> None:
        done = {t for t in self._active_tasks if t.done()}
        if not done:
            return
        for t in done:
            self._active_tasks.discard(t)
            if t.cancelled():
                continue
            exc = t.exception()
            if exc:
                self.logger.error("Background task error: %s", exc)
