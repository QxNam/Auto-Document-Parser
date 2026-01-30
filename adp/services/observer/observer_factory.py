from adp.services.observer.targets.cache_target import CacheTarget
from adp.services.observer.targets.local_target import LocalTarget
from adp.services.observer.targets.s3_target import S3Target


class ObserverFactory:
    _mapping = {"local": LocalTarget, "s3": S3Target, "cache": CacheTarget}

    @classmethod
    def create_observer(cls, target_name: str):
        target_class = cls._mapping.get(target_name.lower())
        if not target_class:
            raise ValueError(f"Target '{target_name}' is not supported.")
        return target_class()
