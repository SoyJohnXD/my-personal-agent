from uuid import UUID

from pydantic import BaseModel
from pydantic_ai.tools import Tool

from src.db.memory.interface import IMemoryRepository
from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "delete_memory"
logger = get_logger(f"skill:user_memories:{skill_name}")


class DeleteMemoryArgs(BaseModel):
    id: UUID


directive = SkillDirective(
    objective="Elimina permanentemente una memoria de la base de datos a largo plazo.",
    use_cases=["El usuario te pide explícitamente borrar u olvidar una memoria y tú YA TIENES el UUID exacto de esa memoria"],
    avoid_when=["El usuario pide borrar algo y no sabes el UUID (usa search_memories primero)", "NUNCA inventes un id"],
)


def _repository(repository: IMemoryRepository | None) -> IMemoryRepository:
    return repository or MemoryRepository()


def skill(id: UUID, repository: IMemoryRepository | None = None) -> str:
    parsed = DeleteMemoryArgs(id=id)
    logger.info(f"Borrando memoria: '{parsed.id}'")
    try:
        deleted = _repository(repository).delete(id=parsed.id)
        if not deleted:
            return "No encontré esa memoria."
        return "Memoria borrada."
    except Exception as error:
        logger.error(f"Error en delete_memory: {error}")
        return f"Error al borrar la memoria: {error}"


def build_delete_memory_tool(repository: IMemoryRepository | None = None) -> Tool:
    def run(id: UUID) -> str:
        return skill(id, repository=repository)

    return Tool(run, name=skill_name, description=directive.compile_instructions())


delete_memory = build_delete_memory_tool()
