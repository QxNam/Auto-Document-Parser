# adp/services/observer/observer_manager.py
import asyncio
from adp.configs.logger import worker_logger as logger
from adp.configs.settings import settings
from adp.services.observer.observer_factory import ObserverFactory

class ObserverManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_observers()
        return cls._instance

    def _init_observers(self):
        """
        Initialize observers based on configured targets.
        """
        self.observers = []
        enabled_targets = settings.OBSERVER_TARGETS
        for target_name in enabled_targets:
            try:
                observer = ObserverFactory.create_observer(target_name)
                self.observers.append(observer)
                logger.info(f"[Observer] Initialized target: {target_name}")
            except Exception as e:
                logger.error(f"[Observer] Failed to init {target_name}: {e}")

    async def send(self, data: str, file_name: str, *args, **kwargs) -> dict:
        """
        Send data to all configured observers asynchronously.
        """
        if not self.observers:
            logger.warning("[Observer] No observers registered. Skipping send.")
            return {}

        tasks = [observer.update(data, file_name, *args, **kwargs) for observer in self.observers]
        
        # return_exceptions=True helps ensure one target's failure doesn't crash the whole system
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = {}
        for idx, result in enumerate(results):
            target_name = self.observers[idx].__class__.__name__.lower().replace("target", "")
            
            if isinstance(result, Exception):
                logger.error(f"[Observer] {target_name} failed: {result}")
                final_results[target_name] = None
            else:
                final_results[target_name] = result
                
        return final_results
    
    async def close_all(self):
        # Giả sử các target có hàm close()
        tasks = [t.close() for t in self.observers if hasattr(t, 'close')]
        if tasks:
            await asyncio.gather(*tasks)
