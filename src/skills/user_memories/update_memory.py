from uuid import UUID

from pydantic import BaseModel
from pydantic_ai.tools import Tool

from src.db.memory.interface import IMemoryRepository
from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "update_memory"
logger = get_logger(f"skill:user_memories:{skill_name}")


class UpdateMemoryArgs(BaseModel):
    id: UUID
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


directive = SkillDirective(
    objective="Sobrescribe el contenido de una memoria existente.",
    use_cases=["Tienes un id (UUID) válido en el contexto y el usuario te pide modificar, agregar o cambiar un dato de esa misma memoria"],
    avoid_when=[
        "NO LA USES si no tienes el id exacto. PRIMER paso obligatorio es llamar a search_memories para obtener el UUID. Luego llama a update_memory",
        "No la uses para crear nueva información desde cero (usa save_memory en su lugar)",
    ],
)


def _repository(repository: IMemoryRepository | None) -> IMemoryRepository:
    return repository or MemoryRepository()


def skill(
    id: UUID, title: str | None = None, content: str | None = None, tags: list[str] | None = None, repository: IMemoryRepository | None = None
) -> str:
    parsed = UpdateMemoryArgs(id=id, title=title, content=content, tags=tags)
    logger.info(f"Actualizando memoria: '{parsed.id}'")
    try:
        memory = _repository(repository).update(id=parsed.id, title=parsed.title, content=parsed.content, tags=parsed.tags)
        if not memory:
            return "No encontré esa memoria."
        return f"Memoria '{memory.title}' actualizada."
    except Exception as error:
        logger.error(f"Error en update_memory: {error}")
        return f"Error al actualizar la memoria: {error}"


def build_update_memory_tool(repository: IMemoryRepository | None = None) -> Tool:
    def run(id: UUID, title: str | None = None, content: str | None = None, tags: list[str] | None = None) -> str:
        return skill(id, title=title, content=content, tags=tags, repository=repository)

    return Tool(run, name=skill_name, description=directive.compile_instructions())


update_memory = build_update_memory_tool()
