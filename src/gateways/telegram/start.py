from uuid import uuid4

from pydantic_ai.messages import ModelResponse, ThinkingPart
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.agent.assistant import assistant
from src.config.settings import MODEL_NAME, TELEGRAM_TOKEN
from src.db.token_usage.repository import UsageRepository
from src.utils.logger import get_logger

HISTORY_IDENTIFIER = "chat_history"
SESSION_ID = "session_id"

logger = get_logger("telegram_gateway")

usage_repo = UsageRepository()


def _extract_reasoning(messages: list) -> str | None:
    """Extract the thinking/reasoning from the last assistant response."""
    for msg in reversed(messages):
        if isinstance(msg, ModelResponse) and hasattr(msg, "parts"):
            thinking_parts = [p.content for p in msg.parts if isinstance(p, ThinkingPart)]
            if thinking_parts:
                return "\n".join(thinking_parts)
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None or context.user_data is None:
        return

    user_text: str = update.message.text
    await update.message.chat.send_action(action="typing")

    if HISTORY_IDENTIFIER not in context.user_data:
        context.user_data[HISTORY_IDENTIFIER] = []

    if SESSION_ID not in context.user_data:
        context.user_data[SESSION_ID] = uuid4()

    session_id = context.user_data[SESSION_ID]

    try:
        response = await assistant.run(user_text, message_history=context.user_data[HISTORY_IDENTIFIER])

        usage = response.usage
        all_messages = response.all_messages()
        reasoning = _extract_reasoning(all_messages)

        log_msg = (
            f"Tokens — input: {usage.input_tokens} | output: {usage.output_tokens} "
            f"| total: {usage.total_tokens} | session: {session_id}"
        )
        if reasoning:
            log_msg += f" | reasoning: {len(reasoning)} chars"
        logger.info(log_msg)

        usage_repo.create(
            session_id=session_id,
            chat_id=update.effective_chat.id,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            model=MODEL_NAME,
            user_message=user_text,
            assistant_response=response.output,
            reasoning=reasoning,
        )

        context.user_data[HISTORY_IDENTIFIER] = all_messages

        await update.message.reply_text(response.output)
    except Exception as e:
        if "Invalid assistant message" in str(e):
            logger.warning("Historial corrupto, reiniciando contexto...")
            context.user_data[HISTORY_IDENTIFIER] = []
            response = await assistant.run(user_text)
            await update.message.reply_text(response.output)
        else:
            logger.error(f"Error inesperado: {e}")
            await update.message.reply_text("Algo salió mal, intenta de nuevo.")


def main() -> None:
    logger.info("Iniciando Gateway de Telegram...")

    token: str = TELEGRAM_TOKEN
    if not token:
        logger.fatal("Falta la variable de entorno TELEGRAM_TOKEN")
        raise ValueError("Error crítico: Falta la variable de entorno TELEGRAM_TOKEN")

    app: Application = Application.builder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    logger.info(
        "Bot de Telegram en línea. "
        "Listo para recibir mensajes. Presiona Ctrl+C para detener."
    )
    app.run_polling()


if __name__ == "__main__":
    main()
