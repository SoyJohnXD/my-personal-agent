from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool

from src.db.memory.interface import IMemoryRepository
from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "save_memory"
logger = get_logger(f"skill:user_memories:{skill_name}")


class SaveMemoryArgs(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(..., min_length=1)


directive = SkillDirective(
    objective=(
        "Persiste información, gustos o tareas del usuario en la base de datos a largo plazo. "
        "title: Resumen conciso e identificativo de la memoria (max 50 chars). "
        "content: El dato exacto a recordar. Sé detallado y preserva el contexto original. "
        "tags: Un string separado por #, ejemplo '#comida#alergias'."
    ),
    use_cases=[
        "El usuario te pide EXPLÍCITAMENTE que 'guardes', 'recuerdes' o 'anotes' algo",
        "El usuario comparte información personal clave (ej: alergias, cumpleaños) y pide que la consideres a futuro",
    ],
    avoid_when=[
        "No la uses por iniciativa propia en medio de una conversación técnica rutinaria",
        "No la uses si la información ya existe en una memoria (en su lugar, usa update_memory)",
    ],
)


def _repository(repository: IMemoryRepository | None) -> IMemoryRepository:
    return repository or MemoryRepository()


def skill(title: str, content: str, tags: list[str], repository: IMemoryRepository | None = None) -> str:
    parsed = SaveMemoryArgs(title=title, content=content, tags=tags)
    logger.info(f"Guardando memoria: '{parsed.title}'")
    try:
        memory = _repository(repository).create(title=parsed.title, content=parsed.content, tags=parsed.tags)
        return f"Memoria '{memory.title}' guardada con id {memory.id}."
    except Exception as error:
        logger.error(f"Error en save_memory: {error}")
        return f"Error al guardar la memoria: {error}"


def build_save_memory_tool(repository: IMemoryRepository | None = None) -> Tool:
    def run(title: str, content: str, tags: list[str]) -> str:
        return skill(title, content, tags, repository=repository)

    return Tool(run, name=skill_name, description=directive.compile_instructions())


save_memory = build_save_memory_tool()
