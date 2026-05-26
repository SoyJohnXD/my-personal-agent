from uuid import uuid4

from pydantic_ai import ModelResponse
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from src.agent.assistant import assistant
from src.config.settings import (
    MODEL_NAME,
    TELEGRAM_CHAT_HISTORY_LIMIT,
    TELEGRAM_TOKEN,
)
from src.gateways.shared.utils import control_history, track_token_usage_by_response
from src.utils.logger import get_logger

logger = get_logger("telegram_gateway")

HISTORY_KEY = "chat_history"
SESSION_KEY = "session_id"


def get_session_id(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data[SESSION_KEY]


def get_chat_history(context: ContextTypes.DEFAULT_TYPE) -> list:
    return context.user_data[HISTORY_KEY]


def update_chat_history(context: ContextTypes.DEFAULT_TYPE, response: ModelResponse) -> None:
    context.user_data[HISTORY_KEY] = control_history(response.all_messages(), TELEGRAM_CHAT_HISTORY_LIMIT)


def initialize_gateway_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.setdefault(HISTORY_KEY, [])
    context.user_data.setdefault(SESSION_KEY, uuid4())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message: str = update.message.text
    await update.message.chat.send_action(action="typing")
    initialize_gateway_state(context)
    session_id = get_session_id(context)

    try:
        response = await assistant.run(user_message, message_history=get_chat_history(context))
        track_token_usage_by_response(response, session_id, user_message)
        update_chat_history(context, response)
        await update.message.reply_text(response.output)
    except Exception as error:
        logger.error(f"Error inesperado: {error}")
        await update.message.reply_text("Algo salio mal, intenta de nuevo.")


def main() -> None:
    logger.info(f"Starting gateway with model {MODEL_NAME}")
    app: Application = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
