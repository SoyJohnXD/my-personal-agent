from pathlib import Path

from sqlmodel import SQLModel, create_engine

from src.config.settings import AGENT_NAME
from src.db.memory.schema import Memory
from src.db.usage.schema import TokenUsage

DB_DIR = Path("storage/db")
DB_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_FILE_NAME = DB_DIR / f"{AGENT_NAME}.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=False)

SQLModel.metadata.create_all(engine, tables=[Memory.__table__, TokenUsage.__table__])


def _migrate_usage_columns() -> None:
    """Add new columns to tokenusage table if they don't exist yet."""
    new_columns = [
        "user_message TEXT",
        "assistant_response TEXT",
        "reasoning TEXT",
    ]
    with engine.connect() as conn:
        existing = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(tokenusage)")}
        for col_def in new_columns:
            col_name = col_def.split()[0]
            if col_name not in existing:
                conn.exec_driver_sql(f"ALTER TABLE tokenusage ADD COLUMN {col_def}")
        conn.commit()


_migrate_usage_columns()
