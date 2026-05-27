from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Text


class TokenUsage(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(index=True)
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str | None = Field(default=None)
    user_message: str | None = Field(default=None, sa_type=Text)
    assistant_response: str | None = Field(default=None, sa_type=Text)
    reasoning: str | None = Field(default=None, sa_type=Text)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
