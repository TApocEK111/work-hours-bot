from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Returns timezone-aware UTC datetime"""

    @abstractmethod
    def now(self) -> datetime: ...
