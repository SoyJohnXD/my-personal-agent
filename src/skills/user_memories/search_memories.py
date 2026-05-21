from src.utils.logger import get_logger
from src.db.memory.repository import MemoryRepository

logger = get_logger("skill:user_memories:search_memories")
repo = MemoryRepository()


def search_memories(text: str) -> str:
    """
    Busca memorias guardadas por texto libre.

    ÚSALA cuando:
    - El usuario pregunte por algo que pudo haber guardado antes.
    - Antes de editar o borrar cualquier memoria, siempre.

    NO la uses cuando:
    - El usuario pida ver todas sus memorias, usa get_all_memories.
    """
    logger.info(f"Buscando memorias: '{text}'")
    try:
        memories = repo.search(text=text)
        if not memories:
            return "No encontré memorias relacionadas."
        return "\n\n".join(
            f"ID: {m.id}\nTítulo: {m.title}\nTags: {m.tags}\nContenido: {m.content}"
            for m in memories
        )
    except Exception as error:
        logger.error(f"Error en search_memories: {error}")
        return f"Error al buscar memorias: {error}"
