from uuid import UUID, uuid4

from pydantic_ai import ModelResponse
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from src.agent.assistant import create_assistant
from src.config.settings import Settings, load_telegram_settings
from src.db.core import create_database_engine, initialize_database
from src.db.token_usage.repository import TokenUsageRepository
from src.gateways.shared.utils import control_history, track_token_usage_by_response
from src.utils.logger import get_logger

logger = get_logger("telegram_gateway")

HISTORY_KEY = "chat_history"
SESSION_KEY = "session_id"
ASSISTANT_KEY = "assistant"
SETTINGS_KEY = "settings"
TOKEN_REPOSITORY_KEY = "token_usage_repo"


def get_session_id(context: ContextTypes.DEFAULT_TYPE) -> UUID:
    return context.user_data[SESSION_KEY]


def get_chat_history(context: ContextTypes.DEFAULT_TYPE) -> list:
    return context.user_data[HISTORY_KEY]


def update_chat_history(context: ContextTypes.DEFAULT_TYPE, response: ModelResponse, settings: Settings) -> None:
    context.user_data[HISTORY_KEY] = control_history(response.all_messages(), settings.telegram_chat_history_limit)


def initialize_gateway_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.setdefault(HISTORY_KEY, [])
    context.user_data.setdefault(SESSION_KEY, uuid4())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message: str = update.message.text
    await update.message.chat.send_action(action="typing")
    initialize_gateway_state(context)

    settings = context.application.bot_data[SETTINGS_KEY]
    runtime_assistant = context.application.bot_data[ASSISTANT_KEY]
    token_usage_repo = context.application.bot_data[TOKEN_REPOSITORY_KEY]
    session_id = get_session_id(context)

    try:
        response = await runtime_assistant.run(user_message, message_history=get_chat_history(context))
        track_token_usage_by_response(response, session_id, user_message, token_usage_repo=token_usage_repo, model_name=settings.model_name)
        update_chat_history(context, response, settings)
        await update.message.reply_text(response.output)
    except Exception as error:
        logger.error(f"Error inesperado: {error}")
        await update.message.reply_text("Algo salio mal, intenta de nuevo.")


def main() -> None:
    settings = load_telegram_settings()
    database_engine = initialize_database(create_database_engine(settings))
    runtime_assistant = create_assistant(settings)
    token_usage_repo = TokenUsageRepository(database_engine)
    logger.info(f"Starting gateway with model {settings.model_name}")
    app: Application = Application.builder().token(settings.telegram_token).build()
    app.bot_data[SETTINGS_KEY] = settings
    app.bot_data[ASSISTANT_KEY] = runtime_assistant
    app.bot_data[TOKEN_REPOSITORY_KEY] = token_usage_repo
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
