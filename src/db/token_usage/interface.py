from abc import ABC, abstractmethod
from uuid import UUID

from src.db.token_usage.schema import TokenUsage


class ITokenUsageRepository(ABC):
    @abstractmethod
    def create(
        self,
        session_id: UUID,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        model: str | None = None,
        user_message: str | None = None,
        assistant_response: str | None = None,
    ) -> TokenUsage:
        pass
