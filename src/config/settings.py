import os
from dotenv import load_dotenv

load_dotenv()


def get_env_variable(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise ValueError(f"CRITICAL: Missing environment variable '{key}'")
    return value


AGENT_NAME: str = "Hermenecio"

API_KEY: str = get_env_variable("API_KEY")
API_BASE_URL: str = get_env_variable("API_BASE_URL")
MODEL_NAME: str = get_env_variable("MODEL_NAME")

TELEGRAM_TOKEN: str = get_env_variable("TELEGRAM_TOKEN")
TELEGRAM_MEMORY_WINDOW_SIZE: int = 6

CLI_MEMORY_WINDOW_SIZE: int = 6


RESTRICTED_FILES = {".env", "secrets.json", "credentials"}
RESTRICTED_EXTENSIONS = {".key", ".pem", ".p12", ".sqlite3"}
