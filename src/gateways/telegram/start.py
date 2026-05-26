# === Imports ===

from uuid import uuid4

from pydantic_ai.messages import ModelResponse, ThinkingPart
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from src.agent.assistant import assistant
from src.config.settings import MODEL_NAME, TELEGRAM_TOKEN
from src.db.token_usage.repository import UsageRepository
from src.utils.logger import get_logger

# === Constants ===

HISTORY_KEY = "chat_history"
SESSION_KEY = "session_id"

logger = get_logger("telegram_gateway")

usage_repo = UsageRepository()

# === Helpers ===


def extract_reasoning(messages: list) -> str | None:
    """Extrae el razonamiento del ultimo mensaje del asistente."""
    for msg in reversed(messages):
        if isinstance(msg, ModelResponse) and hasattr(msg, "parts"):
            thinking_parts = [
                part.content
                for part in msg.parts
                if isinstance(part, ThinkingPart)
            ]
            if thinking_parts:
                return "\n".join(thinking_parts)
    return None


# === Handlers ===


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None or context.user_data is None:
        return

    user_text: str = update.message.text
    await update.message.chat.send_action(action="typing")

    if HISTORY_KEY not in context.user_data:
        context.user_data[HISTORY_KEY] = []

    if SESSION_KEY not in context.user_data:
        context.user_data[SESSION_KEY] = uuid4()

    session_id = context.user_data[SESSION_KEY]

    try:
        response = await assistant.run(
            user_text, message_history=context.user_data[HISTORY_KEY]
        )

        usage = response.usage
        all_messages = response.all_messages()
        reasoning = extract_reasoning(all_messages)

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

        context.user_data[HISTORY_KEY] = all_messages

        await update.message.reply_text(response.output)

    except Exception as error:
        if "Invalid assistant message" in str(error):
            logger.warning("Historial corrupto, reiniciando contexto...")
            context.user_data[HISTORY_KEY] = []
            response = await assistant.run(user_text)
            await update.message.reply_text(response.output)
        else:
            logger.error(f"Error inesperado: {error}")
            await update.message.reply_text("Algo salio mal, intenta de nuevo.")


# === Main ===


def main() -> None:
    logger.info("Iniciando Gateway de Telegram...")

    token: str = TELEGRAM_TOKEN
    if not token:
        logger.fatal("Falta la variable de entorno TELEGRAM_TOKEN")
        raise ValueError("Error critico: Falta la variable de entorno TELEGRAM_TOKEN")

    app: Application = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    logger.info("Bot de Telegram en linea. Listo para recibir mensajes. Presiona Ctrl+C para detener.")
    app.run_polling()


if __name__ == "__main__":
    main()
