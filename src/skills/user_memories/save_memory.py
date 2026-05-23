from pydantic_ai.tools import Tool

from src.db.memory.repository import MemoryRepository
from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

skill_name = "save_memory"
logger = get_logger(f"skill:user_memories:{skill_name}")
repo = MemoryRepository()

directive = SkillDirective(
    objective=(
        "Persiste información, gustos o tareas del usuario en la base de datos a largo plazo. title: Resumen conciso e identificativo de la memoria (max 50 chars). content: El dato exacto a recordar. Sé detallado y preserva el contexto original. tags: Un string separado por #, ejemplo '#comida#alergias'."
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


def skill(title: str, content: str, tags: list[str]) -> str:
    logger.info(f"Guardando memoria: '{title}'")
    try:
        memory = repo.create(title=title, content=content, tags=tags)
        return f"Memoria '{memory.title}' guardada con id {memory.id}."
    except Exception as error:
        logger.error(f"Error en save_memory: {error}")
        return f"Error al guardar la memoria: {error}"


save_memory = Tool(skill, name=skill_name, description=directive.compile_instructions())
