from abc import ABC, abstractmethod


class DBService(ABC):
    """Interface for database"""

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError("connect() is not implemented")

    @abstractmethod
    async def disconnect(self) -> None:
        raise NotImplementedError("disconnect() is not implemented")
