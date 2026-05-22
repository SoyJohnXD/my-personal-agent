from pathlib import Path

from sqlmodel import SQLModel, create_engine

from src.config.settings import AGENT_NAME
from src.db.memory.schema import Memory

DB_DIR = Path("storage/db")
DB_DIR.mkdir(parents=True, exist_ok=True)

SQLITE_FILE_NAME = DB_DIR / f"{AGENT_NAME}.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=False)

SQLModel.metadata.create_all(engine, tables=[Memory.__table__])
