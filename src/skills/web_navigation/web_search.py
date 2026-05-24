# === Imports ===

from ddgs import DDGS
from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool

from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

# === Constants ===

skill_name = "web_search"
logger = get_logger(f"skill:web_navigation:{skill_name}")

MAX_RESULTS = 2
MAX_BODY_CHARS = 300

# === Validation ===


class WebSearchArgs(BaseModel):
    """Valida que el LLM pase un query de búsqueda no vacío."""

    query: str = Field(..., min_length=1, max_length=500)


# === Helpers ===


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


# === Directive ===

directive = SkillDirective(
    objective=(
        "Busca en internet información externa. "
        "REGLA PARA QUERY: Optimiza con términos clave potentes "
        "(ej: 'clima Bogotá D.C. lluvia'), NUNCA uses preguntas naturales completas."
    ),
    use_cases=[
        "El usuario pide información externa, actual, noticias o precios",
        "La pregunta requiere hechos recientes fuera de tu conocimiento base",
    ],
    avoid_when=[
        "Puedes responder con tu conocimiento base sin riesgo de alucinar",
        "El usuario pregunta por sus propios datos personales (usa search_memories)",
    ],
)


# === Skill ===


def skill(query: str) -> str:
    parsed = WebSearchArgs(query=query)
    logger.info(f"Buscando: '{parsed.query}'")
    try:
        search_results = execute_web_search(parsed.query)

        if not search_results:
            return "No se encontraron resultados."

        return format_all_results(search_results)

    except Exception as error:
        logger.error(f"Error en web_search: {error}")
        return f"Error al buscar en internet: {error}"


# === Tool Registration ===

web_search = Tool(skill, name=skill_name, description=directive.compile_instructions())
