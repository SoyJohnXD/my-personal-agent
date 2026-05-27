from uuid import UUID, uuid4

from dotenv import load_dotenv
from pydantic_ai import Agent, ModelResponse
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from src.agent.assistant import DEFAULT_TOOLS
from src.agent.prompts import build_who_you_are
from src.config.settings import (
    AGENT_NAME_ENV,
    API_BASE_URL_ENV,
    API_KEY_ENV,
    CLI_CHAT_HISTORY_LIMIT,
    MODEL_NAME_ENV,
    USER_NAME_ENV,
    get_env,
)
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


def update_chat_history(response: ModelResponse) -> None:
    cli_state["history"] = control_history(response.all_messages(), CLI_CHAT_HISTORY_LIMIT)


def chat_cli() -> None:
    cli_console.clear()
    load_dotenv()
    agent_name = get_env(AGENT_NAME_ENV)
    model_name = get_env(MODEL_NAME_ENV)
    model_config = OpenAIChatModel(model_name, provider=OpenAIProvider(base_url=get_env(API_BASE_URL_ENV), api_key=get_env(API_KEY_ENV)))
    runtime_assistant = Agent(model=model_config, system_prompt=build_who_you_are(agent_name, get_env(USER_NAME_ENV)), tools=DEFAULT_TOOLS)
    database_engine = initialize_database(create_database_engine(agent_name))
    token_usage_repo = TokenUsageRepository(database_engine)
    initialize_cli_state()

    logger.info(f"Starting gateway with model {model_name}")

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
                update_chat_history(response)
                session_id = get_session_id()
                if session_id is not None:
                    track_token_usage_by_response(response, session_id, user_input, token_usage_repo=token_usage_repo, model_name=model_name)

                cli_console.print("\n")
                cli_console.print(Panel(Markdown(response.output), title="🤖 [bold blue]Asistente[/bold blue]", border_style="blue", expand=False))
                cli_console.print("\n")

        except Exception as error:
            cli_console.print(f"\n❌ [bold red]Error tecnico:[/bold red] {str(error)}\n")


if __name__ == "__main__":
    chat_cli()
