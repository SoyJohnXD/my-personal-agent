from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.db.memory.schema import Memory


class IMemoryRepository(ABC):

    @abstractmethod
    def create(self, title: str, content: str, tags: List[str]) -> Memory:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Memory]:
        pass

    @abstractmethod
    def search(self, text: str, limit: int = 10, offset: int = 0) -> List[Memory]:
        pass

    @abstractmethod
    def update(
        self,
        id: UUID,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[Memory]:
        pass

    @abstractmethod
    def delete(self, id: UUID) -> bool:
        pass

    @abstractmethod
    def get_all(self, limit: int = 10, offset: int = 0) -> List[Memory]:
        pass
