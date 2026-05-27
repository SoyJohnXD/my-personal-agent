from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine

from src.config.settings import AGENT_NAME_ENV, get_env
from src.db.memory.schema import Memory
from src.db.token_usage.schema import TokenUsage

DB_DIR = Path("storage/db")
TOKEN_USAGE_MIGRATION_COLUMNS = {
    "user_message": "TEXT",
    "assistant_response": "TEXT",
    "reasoning": "TEXT",
}

_default_engine: Engine | None = None


def get_sqlite_file_name(agent_name: str) -> Path:
    return DB_DIR / f"{agent_name}.db"


def get_sqlite_url(agent_name: str) -> str:
    return f"sqlite:///{get_sqlite_file_name(agent_name)}"


def create_database_engine(agent_name: str) -> Engine:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(get_sqlite_url(agent_name), echo=False)


def migrate_usage_columns(database_engine: Engine) -> None:
    with database_engine.connect() as connection:
        existing = {row[1] for row in connection.exec_driver_sql("PRAGMA table_info(tokenusage)")}
        if not existing:
            return
        for column_name, column_type in TOKEN_USAGE_MIGRATION_COLUMNS.items():
            if column_name not in existing:
                connection.exec_driver_sql(f"ALTER TABLE tokenusage ADD COLUMN {column_name} {column_type}")
        connection.commit()


def initialize_database(database_engine: Engine) -> Engine:
    SQLModel.metadata.create_all(database_engine, tables=[Memory.__table__, TokenUsage.__table__])
    migrate_usage_columns(database_engine)
    return database_engine


def get_default_engine(agent_name: str | None = None) -> Engine:
    global _default_engine
    if _default_engine is None:
        load_dotenv()
        _default_engine = create_database_engine(agent_name or get_env(AGENT_NAME_ENV))
        initialize_database(_default_engine)
    return _default_engine
