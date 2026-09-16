from abc import ABC, abstractmethod
from typing import Any

from app.domain.models import TripData


class CompanyAdapter(ABC):

    name: str

    @abstractmethod
    def can_handle(self, payload: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def normalize(self, payload: dict[str, Any], index: int) -> TripData:
        pass
