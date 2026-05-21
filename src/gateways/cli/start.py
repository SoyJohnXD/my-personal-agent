from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule

from src.agent.assistant import assistant
from src.utils.report import save_execution_report
from src.config.settings import AGENT_NAME

consoleInstance = Console()


def chat_cli():
    consoleInstance.clear()
    consoleInstance.print(
        Panel.fit(
            f"🤖 [bold cyan]{AGENT_NAME} CLI[/bold cyan]\n"
            "Escribe [bold red]'salir'[/bold red] para terminar.\n"
            "Escribe [bold yellow]'/clear'[/bold yellow] para borrar la memoria a corto plazo.",
            border_style="cyan",
        )
    )

    history = []
    session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    while True:
        try:
            consoleInstance.print(Rule(style="dim"))
            user_input = consoleInstance.input(
                "\n[bold green]👤 Tú:[/bold green] "
            ).strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() in ["salir", "exit", "quit"]:
            consoleInstance.print(
                "\n👋 [bold yellow]¡Nos vemos, parcero![/bold yellow]\n"
            )
            break

        if user_input.lower() == "/clear":
            history.clear()
            consoleInstance.print(
                "🧹 [bold yellow]Memoria borrada. Empecemos de cero.[/bold yellow]\n"
            )
            continue

        try:
            with consoleInstance.status(
                "[bold magenta]⏳ Echando cabeza...[/bold magenta]", spinner="dots"
            ):
                response = assistant.run_sync(
                    user_input,
                    message_history=history,
                )

            if response:
                history = response.all_messages()
                save_execution_report(response, user_input, session_id)

                formatted_response = Markdown(response.output)

                consoleInstance.print("\n")
                consoleInstance.print(
                    Panel(
                        formatted_response,
                        title="🤖 [bold blue]Asistente[/bold blue]",
                        border_style="blue",
                        expand=False,
                    )
                )
                consoleInstance.print("\n")

        except Exception as e:
            consoleInstance.print(
                f"\n❌ [bold red]Error técnico:[/bold red] {str(e)}\n"
            )


if __name__ == "__main__":
    chat_cli()
