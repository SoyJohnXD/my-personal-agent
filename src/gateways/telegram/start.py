from uuid import UUID, uuid4

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelResponse
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from src.agent.assistant import DEFAULT_TOOLS
from src.agent.prompts import build_who_you_are
from src.config.settings import (
    AGENT_NAME_ENV,
    API_BASE_URL_ENV,
    API_KEY_ENV,
    MODEL_NAME_ENV,
    TELEGRAM_CHAT_HISTORY_LIMIT,
    TELEGRAM_TOKEN_ENV,
    USER_NAME_ENV,
    get_env,
)
from src.db.core import create_database_engine, initialize_database
from src.db.token_usage.repository import TokenUsageRepository
from src.gateways.shared.utils import control_history, track_token_usage_by_response
from src.utils.logger import get_logger

logger = get_logger("telegram_gateway")

HISTORY_KEY = "chat_history"
SESSION_KEY = "session_id"
ASSISTANT_KEY = "assistant"
MODEL_NAME_KEY = "model_name"
TOKEN_REPOSITORY_KEY = "token_usage_repo"


def get_session_id(context: ContextTypes.DEFAULT_TYPE) -> UUID:
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

    runtime_assistant = context.application.bot_data[ASSISTANT_KEY]
    token_usage_repo = context.application.bot_data[TOKEN_REPOSITORY_KEY]
    model_name = context.application.bot_data[MODEL_NAME_KEY]
    session_id = get_session_id(context)

    try:
        response = await runtime_assistant.run(user_message, message_history=get_chat_history(context))
        track_token_usage_by_response(response, session_id, user_message, token_usage_repo=token_usage_repo, model_name=model_name)
        update_chat_history(context, response)
        await update.message.reply_text(response.output)
    except Exception as error:
        logger.error(f"Error inesperado: {error}")
        await update.message.reply_text("Algo salio mal, intenta de nuevo.")


def main() -> None:
    load_dotenv()
    agent_name = get_env(AGENT_NAME_ENV)
    model_name = get_env(MODEL_NAME_ENV)
    model_config = OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=get_env(API_BASE_URL_ENV), api_key=get_env(API_KEY_ENV)))
    runtime_assistant = Agent(model=model_config, system_prompt=build_who_you_are(agent_name, get_env(USER_NAME_ENV)), tools=DEFAULT_TOOLS)
    database_engine = initialize_database(create_database_engine(agent_name))
    token_usage_repo = TokenUsageRepository(database_engine)
    logger.info(f"Starting gateway with model {model_name}")
    app: Application = Application.builder().token(get_env(TELEGRAM_TOKEN_ENV)).build()
    app.bot_data[MODEL_NAME_KEY] = model_name
    app.bot_data[ASSISTANT_KEY] = runtime_assistant
    app.bot_data[TOKEN_REPOSITORY_KEY] = token_usage_repo
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
