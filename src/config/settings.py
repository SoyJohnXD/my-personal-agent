import os
from dataclasses import dataclass

from dotenv import load_dotenv

AGENT_NAME_ENV = "AGENT_NAME"
USER_NAME_ENV = "USER_NAME"
API_KEY_ENV = "API_KEY"
API_BASE_URL_ENV = "API_BASE_URL"
MODEL_NAME_ENV = "MODEL_NAME"
TELEGRAM_TOKEN_ENV = "TELEGRAM_TOKEN"

BASE_ENV_KEYS = (AGENT_NAME_ENV, USER_NAME_ENV, API_KEY_ENV, API_BASE_URL_ENV, MODEL_NAME_ENV)

TELEGRAM_CHAT_HISTORY_LIMIT = 6
CLI_CHAT_HISTORY_LIMIT = 6

RESTRICTED_FILES = {".env", "secrets.json", "credentials"}
RESTRICTED_EXTENSIONS = {".key", ".pem", ".p12", ".sqlite3"}

AGENT_NAME = os.getenv(AGENT_NAME_ENV, "")
USER_NAME = os.getenv(USER_NAME_ENV, "")
API_KEY = os.getenv(API_KEY_ENV, "")
API_BASE_URL = os.getenv(API_BASE_URL_ENV, "")
MODEL_NAME = os.getenv(MODEL_NAME_ENV, "")
TELEGRAM_TOKEN = os.getenv(TELEGRAM_TOKEN_ENV)


@dataclass(frozen=True)
class Settings:
    agent_name: str
    user_name: str
    api_key: str
    api_base_url: str
    model_name: str
    telegram_token: str | None = None
    telegram_chat_history_limit: int = TELEGRAM_CHAT_HISTORY_LIMIT
    cli_chat_history_limit: int = CLI_CHAT_HISTORY_LIMIT


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(name)
    return value


def _base_settings(telegram_token: str | None = None) -> Settings:
    return Settings(
        agent_name=_required_env(AGENT_NAME_ENV),
        user_name=_required_env(USER_NAME_ENV),
        api_key=_required_env(API_KEY_ENV),
        api_base_url=_required_env(API_BASE_URL_ENV),
        model_name=_required_env(MODEL_NAME_ENV),
        telegram_token=telegram_token,
    )


def load_cli_settings() -> Settings:
    load_dotenv()
    return _base_settings(telegram_token=os.getenv(TELEGRAM_TOKEN_ENV))


def load_telegram_settings() -> Settings:
    load_dotenv()
    telegram_token = os.getenv(TELEGRAM_TOKEN_ENV)
    if not telegram_token:
        raise ValueError(TELEGRAM_TOKEN_ENV)
    return _base_settings(telegram_token=telegram_token)
