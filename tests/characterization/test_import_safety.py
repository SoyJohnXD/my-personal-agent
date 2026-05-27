# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
import importlib
from pathlib import Path

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
