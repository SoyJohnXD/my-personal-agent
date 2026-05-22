from src.db.memory.repository import MemoryRepository
from src.utils.logger import get_logger

logger = get_logger("skill:user_memories:save_memory")
repo = MemoryRepository()


def save_memory(title: str, content: str, tags: list[str]) -> str:
    """
    Guarda algo que el usuario menciona explícitamente querer recordar.

    ÚSALA cuando:
    - El usuario diga explícitamente que quiere guardar o recordar algo.
    - Sea un gusto, lugar, plan, película, idea o pendiente personal.

    NO la uses cuando:
    - El usuario no pidió explícitamente guardar algo.
    - La conversación es técnica, de código o de consulta general.
    - La memoria ya existe, usa update_memory.
    - NUNCA ofrezcas recordatorios ni prometas avisar fechas, no tienes esa capacidad.
    """
    logger.info(f"Guardando memoria: '{title}'")
    try:
        memory = repo.create(title=title, content=content, tags=tags)
        return f"Memoria '{memory.title}' guardada con id {memory.id}."
    except Exception as error:
        logger.error(f"Error en save_memory: {error}")
        return f"Error al guardar la memoria: {error}"
