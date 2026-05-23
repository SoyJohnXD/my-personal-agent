from uuid import UUID

from sqlmodel import Session, func, select

from src.db.core import engine
from src.db.usage.interface import IUsageRepository
from src.db.usage.schema import TokenUsage


class UsageRepository(IUsageRepository):
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
        with Session(engine) as session:
            session.add(usage)
            session.commit()
            session.refresh(usage)
            return usage

    def get_by_session(self, session_id: UUID, limit: int = 100, offset: int = 0) -> list[TokenUsage]:
        with Session(engine) as session:
            return session.exec(select(TokenUsage).where(TokenUsage.session_id == session_id).order_by(TokenUsage.created_at).offset(offset).limit(limit)).all()

    def get_total_by_session(self, session_id: UUID) -> int:
        with Session(engine) as session:
            result = session.exec(select(func.sum(TokenUsage.total_tokens)).where(TokenUsage.session_id == session_id)).one()
            return result or 0
