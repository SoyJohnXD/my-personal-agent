# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
import importlib

import pytest

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
    assert hasattr(module, "get_env")


def test_get_env_names_missing_base_key(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        if key != "MODEL_NAME":
            monkeypatch.setenv(key, value)

    settings = importlib.import_module("src.config.settings")

    with pytest.raises(ValueError, match="MODEL_NAME"):
        settings.get_env("MODEL_NAME")


def test_cli_settings_do_not_require_telegram_token(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    settings = importlib.import_module("src.config.settings")

    assert settings.get_env("MODEL_NAME") == "test-model"
    assert settings.os.getenv("TELEGRAM_TOKEN") is None


def test_telegram_settings_require_token_only_when_requested(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    settings = importlib.import_module("src.config.settings")

    with pytest.raises(ValueError, match="TELEGRAM_TOKEN"):
        settings.get_env("TELEGRAM_TOKEN")


def test_telegram_settings_load_token_when_present(monkeypatch):
    clear_runtime_env(monkeypatch)
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("TELEGRAM_TOKEN", "telegram-token")

    settings = importlib.import_module("src.config.settings")

    assert settings.get_env("TELEGRAM_TOKEN") == "telegram-token"
    assert settings.get_env("MODEL_NAME") == "test-model"
