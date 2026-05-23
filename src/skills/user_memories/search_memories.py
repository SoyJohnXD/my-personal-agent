from pydantic_ai.tools import Tool

from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "search_memories"
logger = get_logger(f"skill:user_memories:{skill_name}")
repo = MemoryRepository()

directive = SkillDirective(
    objective=("Busca memorias previamente guardadas. text: palabra clave, frase o fecha en formato ISO (2026-05-22). NO pases oraciones largas."),
    use_cases=[
        f"El usuario pregunta '¿Qué guardamos sobre {skill_name}?', '¿Te acuerdas de {skill_name}?', o '¿Cuáles eran mis preferencias de {skill_name}?'",
        "ES OBLIGATORIO usarla ANTES de llamar a update_memory o delete_memory si no conoces el UUID exacto de la memoria",
    ],
    avoid_when=[
        "No la uses para buscar información en internet",
        "No la uses si buscas un UUID específico que ya tienes en contexto",
    ],
)


def skill(text: str) -> str:
    logger.info(f"Buscando memorias: '{text}'")
    try:
        memories = repo.search(text=text)
        if not memories:
            return "Sin resultados."
        return "\n".join(f"ID:{m.id} | {m.title} | {m.tags} | {m.content[:120]}" for m in memories)
    except Exception as error:
        logger.error(f"Error en {skill_name}: {error}")
        return f"Error: {error}"


search_memories = Tool(skill, name=skill_name, description=directive.compile_instructions())
