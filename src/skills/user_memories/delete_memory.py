from uuid import UUID

from pydantic_ai.tools import Tool

from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "delete_memory"
logger = get_logger(f"skill:user_memories:{skill_name}")
repo = MemoryRepository()

directive = SkillDirective(
    objective="Elimina permanentemente una memoria de la base de datos a largo plazo.",
    use_cases=[
        "El usuario te pide explícitamente borrar u olvidar una memoria y tú YA TIENES el UUID exacto de esa memoria",
    ],
    avoid_when=[
        "El usuario pide borrar algo y no sabes el UUID (usa search_memories primero)",
        "NUNCA inventes un id",
    ],
)


def skill(id: UUID) -> str:
    logger.info(f"Borrando memoria: '{id}'")
    try:
        deleted = repo.delete(id=id)
        if not deleted:
            return "No encontré esa memoria."
        return "Memoria borrada."
    except Exception as error:
        logger.error(f"Error en delete_memory: {error}")
        return f"Error al borrar la memoria: {error}"


delete_memory = Tool(
    skill, name=skill_name, description=directive.compile_instructions()
)
