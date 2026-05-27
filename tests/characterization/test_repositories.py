# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from src.db.memory.repository import MemoryRepository
from src.db.memory.schema import Memory
from src.db.token_usage.repository import TokenUsageRepository
from src.db.token_usage.schema import TokenUsage


def memory_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine, tables=[Memory.__table__, TokenUsage.__table__])
    return engine


def test_default_sqlite_path_uses_agent_name(tmp_path):
    from src.config.settings import Settings
    from src.db.core import get_sqlite_file_name, get_sqlite_url

    settings = Settings(agent_name="Hermenecio", user_name="Juan", api_key="key", api_base_url="url", model_name="model")

    assert get_sqlite_file_name(settings) == Path("storage/db/Hermenecio.db")
    assert get_sqlite_url(settings) == "sqlite:///storage/db/Hermenecio.db"


def test_memory_repository_crud_search_uses_injected_engine(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repo = MemoryRepository(memory_engine())

    memory = repo.create("Cafe", "Le gusta el cafe", [" Food "])

    assert repo.get_by_id(memory.id).title == "Cafe"
    assert repo.search("cafe")[0].id == memory.id
    assert repo.search("#food")[0].id == memory.id
    updated = repo.update(memory.id, content="Le gusta el cafe sin azucar", tags=["drink"])
    assert updated.content == "Le gusta el cafe sin azucar"
    assert updated.tags == "#food#drink"
    assert repo.get_all(limit=1)[0].id == memory.id
    assert repo.delete(memory.id) is True
    assert repo.delete(memory.id) is False
    assert not Path("storage/db").exists()


def test_token_usage_repository_keeps_reasoning_empty_until_extraction_is_defined():
    repo = TokenUsageRepository(memory_engine())
    session_id = uuid4()

    usage = repo.create(
        session_id=session_id,
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        model="model-a",
        user_message="hola",
        assistant_response="sisas",
    )

    assert not hasattr(usage, "chat_id")
    assert usage.reasoning is None
    assert usage.user_message == "hola"

    minimal = repo.create(session_id=session_id, input_tokens=1, output_tokens=2, total_tokens=3)
    assert minimal.model is None
    assert minimal.reasoning is None


def test_token_usage_migration_is_explicit_and_idempotent(tmp_path):
    from src.db.core import migrate_usage_columns

    sqlite_path = tmp_path / "old.db"
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE tokenusage (id CHAR(32) PRIMARY KEY, session_id CHAR(32), input_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER, model VARCHAR, created_at DATETIME)"
            )
        )

    migrate_usage_columns(engine)
    migrate_usage_columns(engine)

    with Session(engine) as session:
        columns = {row[1] for row in session.connection().exec_driver_sql("PRAGMA table_info(tokenusage)")}

    assert {"user_message", "assistant_response", "reasoning"}.issubset(columns)
    assert "chat_id" not in columns
