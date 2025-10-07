from fastapi import Request

from app.services.messaging.interface.producer import MessagingProducer


def get_producer(request: Request) -> MessagingProducer:
    prod: MessagingProducer = request.app.state.messaging_producer  # type: ignore[attr-defined]
    return prod
