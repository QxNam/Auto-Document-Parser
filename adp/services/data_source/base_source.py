from abc import abstractmethod


class DataSourceBase:
    """
    Abstract base class for DataSource services.
    """

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def pull(self):
        raise NotImplementedError("Subclasses should implement this method.")
