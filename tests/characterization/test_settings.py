# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
import importlib

import pytest


class FakeTokenUsageRepository:
    def __init__(self, engine):
        self.engine = engine


BASE_ENV = {
    "AGENT_NAME": "Hermenecio",
    "USER_NAME": "Juan",
    "API_KEY": "test-key",
    "API_BASE_URL": "https://example.test/v1",
    "MODEL_NAME": "test-model",
}


def clear_runtime_env(monkeypatch):
    for key in [*BASE_ENV, "TELEGRAM_TOKEN"]:
        monkeypatch.delenv(key, raising=False)


def test_settings_import_is_safe_without_environment(monkeypatch):
    clear_runtime_env(monkeypatch)
    module = importlib.import_module("src.config.settings")
    assert hasattr(module, "load_settings")


def test_load_settings_names_missing_base_key(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        if key != "MODEL_NAME":
            monkeypatch.setenv(key, value)

    settings = importlib.import_module("src.config.settings")

    with pytest.raises(ValueError, match="MODEL_NAME"):
        settings.load_settings()


def test_cli_settings_do_not_require_telegram_token(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    settings_module = importlib.import_module("src.config.settings")
    loaded = settings_module.load_settings()

    assert loaded.telegram_token is None
    assert loaded.model_name == "test-model"


def test_telegram_settings_require_token_only_when_requested(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    settings_module = importlib.import_module("src.config.settings")

    with pytest.raises(ValueError, match="TELEGRAM_TOKEN"):
        settings_module.load_settings(require_telegram_token=True)


def test_build_cli_runtime_initializes_settings_assistant_and_database(monkeypatch):
    from src.config.settings import Settings
    from src.gateways.cli import start as cli_start

    settings = Settings(agent_name="Hermenecio", user_name="Juan", api_key="key", api_base_url="url", model_name="model")
    calls = []

    monkeypatch.setattr(cli_start, "load_settings", lambda: calls.append(("load", False)) or settings)
    monkeypatch.setattr(cli_start, "create_database_engine", lambda loaded_settings: calls.append(("engine", loaded_settings)) or "engine")
    monkeypatch.setattr(cli_start, "initialize_database", lambda engine: calls.append(("init", engine)) or "initialized-engine")
    monkeypatch.setattr(cli_start, "create_assistant", lambda loaded_settings: calls.append(("assistant", loaded_settings)) or "assistant")
    monkeypatch.setattr(cli_start, "TokenUsageRepository", FakeTokenUsageRepository)

    loaded_settings, assistant, token_repo = cli_start.build_cli_runtime()

    assert loaded_settings is settings
    assert assistant == "assistant"
    assert token_repo.engine == "initialized-engine"
    assert calls == [("load", False), ("engine", settings), ("init", "engine"), ("assistant", settings)]


def test_build_cli_runtime_accepts_explicit_settings_without_env_load(monkeypatch):
    from src.config.settings import Settings
    from src.gateways.cli import start as cli_start

    settings = Settings(agent_name="Hermenecio", user_name="Juan", api_key="key", api_base_url="url", model_name="model")
    monkeypatch.setattr(cli_start, "load_settings", lambda: (_ for _ in ()).throw(AssertionError("CLI should use explicit settings")))
    monkeypatch.setattr(cli_start, "create_database_engine", lambda _loaded_settings: "engine")
    monkeypatch.setattr(cli_start, "initialize_database", lambda _engine: "initialized-engine")
    monkeypatch.setattr(cli_start, "create_assistant", lambda _loaded_settings: "assistant")
    monkeypatch.setattr(cli_start, "TokenUsageRepository", FakeTokenUsageRepository)

    loaded_settings, assistant, token_repo = cli_start.build_cli_runtime(settings)

    assert loaded_settings is settings
    assert assistant == "assistant"
    assert token_repo.engine == "initialized-engine"


def test_build_telegram_runtime_requires_token_and_initializes_runtime(monkeypatch):
    from src.config.settings import Settings
    from src.gateways.telegram import start as telegram_start

    settings = Settings(
        agent_name="Hermenecio",
        user_name="Juan",
        api_key="key",
        api_base_url="url",
        model_name="model",
        telegram_token="token",
    )
    calls = []

    monkeypatch.setattr(
        telegram_start,
        "load_settings",
        lambda require_telegram_token=False: calls.append(("load", require_telegram_token)) or settings,
    )
    monkeypatch.setattr(telegram_start, "create_database_engine", lambda loaded_settings: calls.append(("engine", loaded_settings)) or "engine")
    monkeypatch.setattr(telegram_start, "initialize_database", lambda engine: calls.append(("init", engine)) or "initialized-engine")
    monkeypatch.setattr(telegram_start, "create_assistant", lambda loaded_settings: calls.append(("assistant", loaded_settings)) or "assistant")
    monkeypatch.setattr(telegram_start, "TokenUsageRepository", FakeTokenUsageRepository)

    loaded_settings, assistant, token_repo = telegram_start.build_telegram_runtime()

    assert loaded_settings is settings
    assert assistant == "assistant"
    assert token_repo.engine == "initialized-engine"
    assert calls == [("load", True), ("engine", settings), ("init", "engine"), ("assistant", settings)]
