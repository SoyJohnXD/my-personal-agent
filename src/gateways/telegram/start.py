from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
)
from src.agent.assistant import assistant
from src.utils.report import save_execution_report
from src.config.settings import TELEGRAM_TOKEN
from src.utils.logger import get_logger

HISTORY_IDENTIFIER = "chat_history"

logger = get_logger("telegram_gateway")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if (
        update.message is None
        or update.message.text is None
        or context.user_data is None
    ):
        return

    user_text: str = update.message.text
    await update.message.chat.send_action(action="typing")

    if HISTORY_IDENTIFIER not in context.user_data:
        context.user_data[HISTORY_IDENTIFIER] = []

    try:
        response = await assistant.run(
            user_text, message_history=context.user_data[HISTORY_IDENTIFIER]
        )

        context.user_data[HISTORY_IDENTIFIER] = response.all_messages()

        save_execution_report(response, user_text, f"telegram_{update.message.chat_id}")

        await update.message.reply_text(response.output)
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}", exc_info=True)
        await update.message.reply_text("Oops, error técnico.")


def main() -> None:
    logger.info("Iniciando Gateway de Telegram...")

    token: str = TELEGRAM_TOKEN
    if not token:
        logger.fatal("Falta la variable de entorno TELEGRAM_TOKEN")
        raise ValueError("Error crítico: Falta la variable de entorno TELEGRAM_TOKEN")

    app: Application = Application.builder().token(token).build()

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    logger.info(
        "Bot de Telegram en línea. Listo para recibir mensajes. Presiona Ctrl+C para detener."
    )
    app.run_polling()


if __name__ == "__main__":
    main()
