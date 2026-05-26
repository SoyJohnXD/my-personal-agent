import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(name)
    return value


# --- Identity ---
AGENT_NAME: str = get_env("AGENT_NAME")
USER_NAME: str = get_env("USER_NAME")

# --- LLM Provider ---
API_KEY: str = get_env("API_KEY")
API_BASE_URL: str = get_env("API_BASE_URL")
MODEL_NAME: str = get_env("MODEL_NAME")

# --- Telegram Gateway ---
TELEGRAM_TOKEN: str = get_env("TELEGRAM_TOKEN")
TELEGRAM_CHAT_HISTORY_LIMIT: int = 6

# --- CLI Gateway ---
CLI_CHAT_HISTORY_LIMIT: int = 6

# --- Security ---
RESTRICTED_FILES = {".env", "secrets.json", "credentials"}
RESTRICTED_EXTENSIONS = {".key", ".pem", ".p12", ".sqlite3"}
