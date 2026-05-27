from pydantic import BaseModel, Field
from pydantic_ai.tools import Tool

from src.db.memory.interface import IMemoryRepository
from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "search_memories"
logger = get_logger(f"skill:user_memories:{skill_name}")


class SearchMemoriesArgs(BaseModel):
    text: str = Field(..., min_length=1, max_length=200)


directive = SkillDirective(
    objective="Busca memorias previamente guardadas. text: palabra clave, frase o fecha en formato ISO (2026-05-22). NO pases oraciones largas.",
    use_cases=[
        f"El usuario pregunta '¿Qué guardamos sobre {skill_name}?', '¿Te acuerdas de {skill_name}?', o '¿Cuáles eran mis preferencias de {skill_name}?'",
        "ES OBLIGATORIO usarla ANTES de llamar a update_memory o delete_memory si no conoces el UUID exacto de la memoria",
    ],
    avoid_when=["No la uses para buscar información en internet", "No la uses si buscas un UUID específico que ya tienes en contexto"],
)


def _repository(repository: IMemoryRepository | None) -> IMemoryRepository:
    return repository or MemoryRepository()


def skill(text: str, repository: IMemoryRepository | None = None) -> str:
    parsed = SearchMemoriesArgs(text=text)
    logger.info(f"Buscando memorias: '{parsed.text}'")
    try:
        memories = _repository(repository).search(text=parsed.text)
        if not memories:
            return "Sin resultados."
        return "\n".join(f"ID:{memory.id} | {memory.title} | {memory.tags} | {memory.content[:120]}" for memory in memories)
    except Exception as error:
        logger.error(f"Error en {skill_name}: {error}")
        return f"Error: {error}"


def build_search_memories_tool(repository: IMemoryRepository | None = None) -> Tool:
    def run(text: str) -> str:
        return skill(text, repository=repository)

    return Tool(run, name=skill_name, description=directive.compile_instructions())


search_memories = build_search_memories_tool()
