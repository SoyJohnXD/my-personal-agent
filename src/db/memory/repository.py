from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Engine
from sqlmodel import Session, String, or_, select

from src.db.core import engine as _default_engine
from src.db.memory.interface import IMemoryRepository
from src.db.memory.schema import Memory
from src.db.memory.utils import format_tags, merge_tags


class MemoryRepository(IMemoryRepository):
    def __init__(self, engine: Engine | None = None) -> None:
        self._engine = engine or _default_engine

    def create(self, title: str, content: str, tags: list[str]) -> Memory:
        memory = Memory(title=title, content=content, tags=format_tags(tags))
        with Session(self._engine) as session:
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return memory

    def get_by_id(self, id: UUID) -> Memory | None:
        with Session(self._engine) as session:
            return session.get(Memory, id)

    def search(self, text: str, limit: int = 10, offset: int = 0) -> list[Memory]:
        with Session(self._engine) as session:
            return session.exec(
                select(Memory)
                .where(
                    or_(
                        Memory.title.ilike(f"%{text}%"),
                        Memory.content.ilike(f"%{text}%"),
                        Memory.tags.ilike(f"%{text}%"),
                        Memory.created_at.cast(String).ilike(f"%{text}%"),
                        Memory.updated_at.cast(String).ilike(f"%{text}%"),
                    )
                )
                .offset(offset)
                .limit(limit)
            ).all()

    def update(
        self,
        id: UUID,
        title: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> Memory | None:
        with Session(self._engine) as session:
            memory = session.get(Memory, id)
            if not memory:
                return None
            if title is not None:
                memory.title = title
            if content is not None:
                memory.content = content
            if tags is not None:
                memory.tags = merge_tags(memory.tags, tags)
            memory.updated_at = datetime.now(UTC)
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return memory

    def delete(self, id: UUID) -> bool:
        with Session(self._engine) as session:
            memory = session.get(Memory, id)
            if not memory:
                return False
            session.delete(memory)
            session.commit()
            return True

    def get_all(self, limit: int = 10, offset: int = 0) -> list[Memory]:
        with Session(self._engine) as session:
            return session.exec(select(Memory).offset(offset).limit(limit)).all()
