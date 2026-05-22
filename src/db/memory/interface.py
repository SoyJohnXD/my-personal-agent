from abc import ABC, abstractmethod
from uuid import UUID

from src.db.memory.schema import Memory


class IMemoryRepository(ABC):
    @abstractmethod
    def create(self, title: str, content: str, tags: list[str]) -> Memory:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Memory | None:
        pass

    @abstractmethod
    def search(self, text: str, limit: int = 10, offset: int = 0) -> list[Memory]:
        pass

    @abstractmethod
    def update(
        self,
        id: UUID,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> Memory | None:
        pass

    @abstractmethod
    def delete(self, id: UUID) -> bool:
        pass

    @abstractmethod
    def get_all(self, limit: int = 10, offset: int = 0) -> list[Memory]:
        pass
