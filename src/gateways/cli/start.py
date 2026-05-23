from uuid import uuid4

from pydantic_ai.messages import ModelResponse, ThinkingPart
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from src.agent.assistant import assistant
from src.config.settings import AGENT_NAME, MODEL_NAME
from src.db.usage.repository import UsageRepository
from src.utils.logger import get_logger

logger = get_logger("cli_gateway")
cli_console = Console()

usage_repo = UsageRepository()


def _extract_reasoning(messages: list) -> str | None:
    """Extract the thinking/reasoning from the last assistant response."""
    for msg in reversed(messages):
        if isinstance(msg, ModelResponse) and hasattr(msg, "parts"):
            thinking_parts = [p.content for p in msg.parts if isinstance(p, ThinkingPart)]
            if thinking_parts:
                return "\n".join(thinking_parts)
    return None


def chat_cli() -> None:
    cli_console.clear()
    cli_console.print(
        Panel.fit(
            f"🤖 [bold cyan]{AGENT_NAME} CLI[/bold cyan]\nEscribe [bold red]'salir'[/bold red] para terminar.\nEscribe [bold yellow]'/clear'[/bold yellow] para borrar la memoria a corto plazo.",
            border_style="cyan",
        )
    )

    session_id = uuid4()
    history = []

    logger.info(f"CLI session started: {session_id}")

    while True:
        try:
            cli_console.print(Rule(style="dim"))
            user_input = cli_console.input("\n[bold green]👤 Tú:[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() in ["salir", "exit", "quit"]:
            cli_console.print("\n👋 [bold yellow]¡Nos vemos, parcero![/bold yellow]\n")
            break

        if user_input.lower() == "/clear":
            history.clear()
            cli_console.print("🧹 [bold yellow]Memoria borrada. Empecemos de cero.[/bold yellow]\n")
            continue

        try:
            with cli_console.status("[bold magenta]⏳ Echando cabeza...[/bold magenta]", spinner="dots"):
                response = assistant.run_sync(
                    user_input,
                    message_history=history,
                )

            if response:
                usage = response.usage
                all_messages = response.all_messages()
                reasoning = _extract_reasoning(all_messages)

                logger.info(f"Tokens — input: {usage.input_tokens} | output: {usage.output_tokens} | total: {usage.total_tokens} | session: {session_id}" + (f" | reasoning: {len(reasoning)} chars" if reasoning else ""))

                usage_repo.create(
                    session_id=session_id,
                    chat_id=0,
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                    total_tokens=usage.total_tokens,
                    model=MODEL_NAME,
                    user_message=user_input,
                    assistant_response=response.output,
                    reasoning=reasoning,
                )

                history = all_messages

                formatted_response = Markdown(response.output)

                cli_console.print("\n")
                cli_console.print(
                    Panel(
                        formatted_response,
                        title="🤖 [bold blue]Asistente[/bold blue]",
                        border_style="blue",
                        expand=False,
                    )
                )
                cli_console.print("\n")

        except Exception as e:
            cli_console.print(f"\n❌ [bold red]Error técnico:[/bold red] {str(e)}\n")


if __name__ == "__main__":
    chat_cli()
