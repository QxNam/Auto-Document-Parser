from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Tuple, Union


class Parser(ABC):
    """
    Abstract base class for document parsers.
    """

    @abstractmethod
    def parse(self, file: Union[str, Path, BinaryIO], file_name: str) -> Tuple[str, str, int]:
        """
        Convert the document at the given file path into text representation.
        """
        pass
