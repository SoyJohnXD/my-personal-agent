from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import Session, select, or_

from src.db.memory.utils import format_tags, merge_tags
from src.db.core import engine
from src.db.memory.schema import Memory
from src.db.memory.interface import IMemoryRepository


class MemoryRepository(IMemoryRepository):

    def create(self, title: str, content: str, tags: List[str]) -> Memory:
        memory = Memory(title=title, content=content, tags=format_tags(tags))
        with Session(engine) as session:
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return memory

    def get_by_id(self, id: UUID) -> Optional[Memory]:
        with Session(engine) as session:
            return session.get(Memory, id)

    def search(self, text: str, limit: int = 10, offset: int = 0) -> List[Memory]:
        with Session(engine) as session:
            return session.exec(
                select(Memory)
                .where(
                    or_(
                        Memory.title.ilike(f"%{text}%"),
                        Memory.content.ilike(f"%{text}%"),
                        Memory.tags.ilike(f"%{text}%"),
                    )
                )
                .offset(offset)
                .limit(limit)
            ).all()

    def update(
        self,
        id: UUID,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[Memory]:
        with Session(engine) as session:
            memory = session.get(Memory, id)
            if not memory:
                return None
            if title is not None:
                memory.title = title
            if content is not None:
                memory.content = content
            if tags is not None:
                memory.tags = merge_tags(memory.tags, tags)
            memory.updated_at = datetime.now(timezone.utc)
            session.add(memory)
            session.commit()
            session.refresh(memory)
            return memory

    def delete(self, id: UUID) -> bool:
        with Session(engine) as session:
            memory = session.get(Memory, id)
            if not memory:
                return False
            session.delete(memory)
            session.commit()
            return True

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Memory]:
        with Session(engine) as session:
            return session.exec(select(Memory).offset(offset).limit(limit)).all()
