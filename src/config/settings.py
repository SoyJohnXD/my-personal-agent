import os

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


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(name)
    return value
