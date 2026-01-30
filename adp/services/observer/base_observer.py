from abc import ABC, abstractmethod


class BaseObserver(ABC):
    @abstractmethod
    def update(self, data):
        pass

    @abstractmethod
    async def close(self):
        pass
