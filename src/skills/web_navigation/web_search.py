from ddgs import DDGS

from src.utils.logger import get_logger

logger = get_logger("skill:web_navigation:web_search")

MAX_RESULTS = 2
MAX_BODY_CHARS = 300


def execute_web_search(query: str) -> list[dict]:
    return DDGS().text(query, max_results=MAX_RESULTS)


def format_search_result(search_result: dict) -> str:
    title = search_result.get("title", "Sin título")
    url = search_result.get("href", "Sin URL")
    body = (search_result.get("body") or "")[:MAX_BODY_CHARS]
    return f"- {title}\n  {url}\n  {body}\n"


def format_all_results(search_results: list[dict]) -> str:
    formatted_results = [format_search_result(result) for result in search_results]
    return "Resultados de la búsqueda:\n\n" + "\n".join(formatted_results)


def web_search(query: str) -> str:
    """
    Busca en internet información general, documentación técnica o noticias.

    ÚSALA cuando:
    - El usuario pide explícitamente buscar en internet.
    - La respuesta requiere información actualizada que puede haber cambiado.
    - No tienes certeza suficiente sobre el tema con tu conocimiento propio.

    NO la uses cuando:
    - Puedes responder con conocimiento propio con alta certeza.
    - La tarea es de código, razonamiento o conversación general.
    - Ya tienes el contexto suficiente del turno anterior.
    """
    logger.info(f"Buscando: '{query}'")

    try:
        search_results = execute_web_search(query)

        if not search_results:
            return "No se encontraron resultados."

        return format_all_results(search_results)

    except Exception as error:
        logger.error(f"Error en web_search: {error}")
        return f"Error al buscar en internet: {error}"
