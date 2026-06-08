from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generator

from meridian.models import Client, Signal


class BaseMonitor(ABC):
    """All monitors yield Signal objects for a given client list."""

    name: str = "base"

    @abstractmethod
    def scan(self, clients: list[Client]) -> Generator[Signal, None, None]:
        """Yield signals found for any of the given clients."""
        ...

    def _now(self) -> datetime:
        return datetime.utcnow()
