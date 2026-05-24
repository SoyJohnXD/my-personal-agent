# === Imports ===

from datetime import datetime

import pytz
from pydantic_ai.tools import Tool

from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

# === Constants ===

skill_name = "get_current_date"
logger = get_logger(f"skill:basic_data:{skill_name}")

# === Directive ===

directive = SkillDirective(
    objective="Retorna la fecha y hora actual en Colombia en formato ISO.",
    use_cases=[
        "El usuario pregunta qué día o qué hora es.",
        "Necesitas saber la fecha exacta antes de buscar memorias por fecha.",
    ],
    avoid_when=[
        "No la uses si el usuario no preguntó por la fecha y no la necesitas para ejecutar otra tarea.",
    ],
)


# === Skill ===


def skill() -> str:
    logger.info("Obteniendo fecha actual")
    tz = pytz.timezone("America/Bogota")
    return datetime.now(tz).strftime("%Y-%m-%dT%H:%M")


# === Tool Registration ===

get_current_date = Tool(skill, name=skill_name, description=directive.compile_instructions())
