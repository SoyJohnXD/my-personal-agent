import os
from dotenv import load_dotenv

load_dotenv()

# --- Identity ---
AGENT_NAME: str = os.getenv("AGENT_NAME")
USER_NAME: str = os.getenv("USER_NAME")

# --- LLM Provider ---
API_KEY: str = os.getenv("API_KEY")
API_BASE_URL: str = os.getenv("API_BASE_URL")
MODEL_NAME: str = os.getenv("MODEL_NAME")

# --- Telegram Gateway ---
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_MEMORY_WINDOW_SIZE: int = 6

# --- CLI Gateway ---
CLI_MEMORY_WINDOW_SIZE: int = 6

# --- Security ---
RESTRICTED_FILES = {".env", "secrets.json", "credentials"}
RESTRICTED_EXTENSIONS = {".key", ".pem", ".p12", ".sqlite3"}
