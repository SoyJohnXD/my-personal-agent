from uuid import UUID

from src.db.memory.repository import MemoryRepository
from src.utils.logger import get_logger

logger = get_logger("skill:user_memories:update_memory")
repo = MemoryRepository()


def update_memory(
    id: UUID,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """
    Edita una memoria existente.

    ÚSALA cuando:
    - El usuario quiera modificar algo que ya guardó.

    NO la uses cuando:
    - No tienes el id, primero usa search_memories para obtenerlo.
    """
    logger.info(f"Actualizando memoria: '{id}'")
    try:
        memory = repo.update(id=id, title=title, content=content, tags=tags)
        if not memory:
            return "No encontré esa memoria."
        return f"Memoria '{memory.title}' actualizada."
    except Exception as error:
        logger.error(f"Error en update_memory: {error}")
        return f"Error al actualizar la memoria: {error}"
