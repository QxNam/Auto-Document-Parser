from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

class BaseMessageQueueService(ABC):
    """
    Abstract base class for message queue service implementations.
    """

    @abstractmethod
    def publish_message_sync(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Publish a message to the specified topic.
        """
        pass

    @abstractmethod
    async def publish_message_async(
        self, topic: str, message: Dict[str, Any]
    ) -> bool:
        """
        Publish a message to the specified topic.
        """
        pass

    @abstractmethod
    def start_consuming_sync(
        self, topic: str, callback: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """
        Consume a message from the specified topic, keep connection.
        """
        pass

    @abstractmethod
    async def start_consuming_async(
        self, topic: str, callback: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """
        Consume a message from the specified topic, keep connection.
        """
        pass
    
    async def wait_connection_closed(self):
        pass