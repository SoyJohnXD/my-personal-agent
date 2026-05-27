# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
import importlib
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlmodel import Session

RUNTIME_MODULES = [
    "src.config.settings",
    "src.db.core",
    "src.db.memory.repository",
    "src.db.token_usage.repository",
    "src.agent.assistant",
    "src.gateways.cli.start",
    "src.gateways.telegram.start",
]


def test_runtime_modules_import_without_env_or_db_side_effects(monkeypatch, tmp_path):
    for key in ["AGENT_NAME", "USER_NAME", "API_KEY", "API_BASE_URL", "MODEL_NAME", "TELEGRAM_TOKEN"]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)

    for module_name in RUNTIME_MODULES:
        importlib.import_module(module_name)

    assert not Path("storage/db").exists()


def _token_usage_columns(sqlite_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with Session(engine) as session:
        return {row[1] for row in session.connection().exec_driver_sql("PRAGMA table_info(tokenusage)")}


def _create_legacy_token_usage_database(sqlite_path: Path) -> None:
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE tokenusage (id CHAR(32) PRIMARY KEY, session_id CHAR(32), input_tokens INTEGER, output_tokens INTEGER, total_tokens INTEGER, model VARCHAR, created_at DATETIME)"
            )
        )


def test_db_core_import_does_not_migrate_legacy_schema_until_initialized(monkeypatch, tmp_path):
    for key in ["AGENT_NAME", "USER_NAME", "API_KEY", "API_BASE_URL", "MODEL_NAME", "TELEGRAM_TOKEN"]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)
    sqlite_path = tmp_path / "storage" / "db" / "Hermenecio.db"
    sqlite_path.parent.mkdir(parents=True)
    _create_legacy_token_usage_database(sqlite_path)

    sys.modules.pop("src.db.core", None)
    db_core = importlib.import_module("src.db.core")

    assert _token_usage_columns(sqlite_path) == {"id", "session_id", "input_tokens", "output_tokens", "total_tokens", "model", "created_at"}

    settings = importlib.import_module("src.config.settings").Settings(
        agent_name="Hermenecio",
        user_name="Juan",
        api_key="key",
        api_base_url="url",
        model_name="model",
    )
    db_core.initialize_database(db_core.create_database_engine(settings))
    first_migrated_columns = _token_usage_columns(sqlite_path)
    db_core.initialize_database(db_core.create_database_engine(settings))

    assert {"chat_id", "user_message", "assistant_response", "reasoning"}.issubset(first_migrated_columns)
    assert _token_usage_columns(sqlite_path) == first_migrated_columns
