import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

class ObserverManager:
    """
    Singleton manager responsible for initializing and coordinating all observers.

    Each data source can have multiple observer targets (e.g., webhooks, APIs, storage services).
    This manager handles observer creation from configuration and provides
    an asynchronous interface to push updates to all relevant observers.
    """

    _instance = None

    def __new__(cls):
        """Ensure a single instance of `ObserverManager` and initialize observers once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_observers()
        return cls._instance

    def _init_observers(self):
        """
        Initialize all observers based on configuration.

        Creates all corresponding observer targets using the `create_observer()` factory.

        Each observer is logged individually upon successful initialization.
        """
        
        self.observers = {}
        # code here

    async def send(self,):
        """
        Push a message asynchronously to all observer targets of a specific source.
        """
        # load all target push from settings
        targets = self.observers.get(...)

        # gather all push tasks
        tasks = [t.push(...) for t in targets if t]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # handle results and log errors
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"[Observer] Observer update failed: {str(result)}")
                raise Exception
