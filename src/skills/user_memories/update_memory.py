from uuid import UUID

from pydantic_ai.tools import Tool

from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "update_memory"
logger = get_logger(f"skill:user_memories:{skill_name}")
repo = MemoryRepository()

directive = SkillDirective(
    objective="Sobrescribe el contenido de una memoria existente.",
    use_cases=[
        "Tienes un id (UUID) válido en el contexto y el usuario te pide modificar, agregar o cambiar un dato de esa misma memoria",
    ],
    avoid_when=[
        "NO LA USES si no tienes el id exacto. PRIMER paso obligatorio es llamar a search_memories para obtener el UUID. Luego llama a update_memory",
        "No la uses para crear nueva información desde cero (usa save_memory en su lugar)",
    ],
)


def skill(
    id: UUID,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
) -> str:
    logger.info(f"Actualizando memoria: '{id}'")
    try:
        memory = repo.update(id=id, title=title, content=content, tags=tags)
        if not memory:
            return "No encontré esa memoria."
        return f"Memoria '{memory.title}' actualizada."
    except Exception as error:
        logger.error(f"Error en update_memory: {error}")
        return f"Error al actualizar la memoria: {error}"


update_memory = Tool(
    skill, name=skill_name, description=directive.compile_instructions()
)
