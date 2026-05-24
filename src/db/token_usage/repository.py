from uuid import UUID

from sqlalchemy import Engine
from sqlmodel import Session

from src.db.core import engine as _default_engine
from src.db.token_usage.interface import IUsageRepository
from src.db.token_usage.schema import TokenUsage


class UsageRepository(IUsageRepository):
    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or _default_engine

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
        usage = TokenUsage(
            session_id=session_id,
            chat_id=chat_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            model=model,
            user_message=user_message,
            assistant_response=assistant_response,
            reasoning=reasoning,
        )
        with Session(self._engine) as session:
            session.add(usage)
            session.commit()
            session.refresh(usage)
            return usage
