from abc import ABC, abstractmethod
from uuid import UUID

from src.db.usage.schema import TokenUsage


class IUsageRepository(ABC):
    @abstractmethod
    def create(
        self,
        session_id: UUID,
        chat_id: int,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        model: str | None = None,
        user_message: str | None = None,
        assistant_response: str | None = None,
        reasoning: str | None = None,
    ) -> TokenUsage:
        pass

    @abstractmethod
    def get_by_session(self, session_id: UUID, limit: int = 100, offset: int = 0) -> list[TokenUsage]:
        pass

    @abstractmethod
    def get_total_by_session(self, session_id: UUID) -> int:
        pass
