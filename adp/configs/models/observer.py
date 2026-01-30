from typing import Dict, List, Union

from pydantic import BaseModel

from .http_request_config import HttpRequestConfig
from .message_queue import RabbitMQConfig as RabbitMQTargetConfig

TargetConfig = Union[HttpRequestConfig, RabbitMQTargetConfig]


class SourceObserverConfig(BaseModel):
    targets: List[TargetConfig]


class ObserverConfig(BaseModel):
    """Map source → list of targets."""

    items: Dict[str, SourceObserverConfig]

    def get_targets(self, source: str) -> List[TargetConfig]:
        return self.items.get(source, SourceObserverConfig(targets=[])).targets
