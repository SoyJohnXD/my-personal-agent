from typing import Any
from uuid import UUID, uuid4

from pydantic_ai import ModelResponse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from src.agent.assistant import create_assistant
from src.config.settings import Settings, load_settings
from src.db.core import create_database_engine, initialize_database
from src.db.token_usage.repository import TokenUsageRepository
from src.gateways.shared.utils import control_history, track_token_usage_by_response
from src.utils.logger import get_logger

EXIT_WORDS = {"salir", "exit", "quit"}

logger = get_logger("cli_gateway")
cli_console = Console()

cli_state = {"session_id": None, "history": []}


def initialize_cli_state() -> None:
    cli_state["session_id"] = uuid4()
    cli_state["history"] = []


def get_session_id() -> UUID | None:
    return cli_state.get("session_id")


def get_chat_history() -> list:
    return cli_state.get("history", [])


def update_chat_history(response: ModelResponse, settings: Settings) -> None:
    cli_state["history"] = control_history(response.all_messages(), settings.cli_chat_history_limit)


def build_cli_runtime(settings: Settings | None = None) -> tuple[Settings, Any, TokenUsageRepository]:
    loaded_settings = settings or load_settings()
    database_engine = initialize_database(create_database_engine(loaded_settings))
    return loaded_settings, create_assistant(loaded_settings), TokenUsageRepository(database_engine)


def chat_cli() -> None:
    cli_console.clear()
    settings, runtime_assistant, token_usage_repo = build_cli_runtime()
    initialize_cli_state()

    logger.info(f"Starting gateway with model {settings.model_name}")

    while True:
        try:
            cli_console.print(Rule(style="dim"))
            user_input = cli_console.input("\n[bold green]Tu:[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_WORDS:
            cli_console.print("\n👋 [bold yellow]Nos vemos, parcero![/bold yellow]\n")
            break

        try:
            with cli_console.status("[bold magenta]Echando cabeza...[/bold magenta]", spinner="dots"):
                response = runtime_assistant.run_sync(user_input, message_history=get_chat_history())

            if response:
                update_chat_history(response, settings)
                session_id = get_session_id()
                if session_id is not None:
                    track_token_usage_by_response(response, session_id, user_input, token_usage_repo=token_usage_repo, model_name=settings.model_name)

                cli_console.print("\n")
                cli_console.print(Panel(Markdown(response.output), title="🤖 [bold blue]Asistente[/bold blue]", border_style="blue", expand=False))
                cli_console.print("\n")

        except Exception as error:
            cli_console.print(f"\n❌ [bold red]Error tecnico:[/bold red] {str(error)}\n")


if __name__ == "__main__":
    chat_cli()
