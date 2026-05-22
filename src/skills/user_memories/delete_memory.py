from uuid import UUID

from src.db.memory.repository import MemoryRepository
from src.utils.logger import get_logger

logger = get_logger("skill:user_memories:delete_memory")
repo = MemoryRepository()


def delete_memory(id: UUID) -> str:
    """
    Borra una memoria permanentemente.

    ÚSALA cuando:
    - El usuario confirme explícitamente que quiere borrarla.

    NO la uses cuando:
    - No tienes el id, primero usa search_memories.
    - El usuario no ha confirmado el borrado.
    """
    logger.info(f"Borrando memoria: '{id}'")
    try:
        deleted = repo.delete(id=id)
        if not deleted:
            return "No encontré esa memoria."
        return "Memoria borrada."
    except Exception as error:
        logger.error(f"Error en delete_memory: {error}")
        return f"Error al borrar la memoria: {error}"
