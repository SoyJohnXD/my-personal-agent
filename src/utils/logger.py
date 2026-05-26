import logging

from rich.console import Console
from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console = Console(force_terminal=True)
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            show_path=True,
            show_time=True,
            markup=True,
            highlighter=None,
        )
        handler.setFormatter(logging.Formatter("[bold cyan]%(name)s[/bold cyan] > %(message)s"))

        logger.addHandler(handler)
        logger.propagate = False

    return logger
