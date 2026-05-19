from src.utils.logger import get_logger

logger = get_logger("user_profile")


def user_profile() -> str:
    """
    Skill para obtener el perfil operativo del usuario.
    Úsala ÚNICA Y EXCLUSIVAMENTE si el usuario te pregunta explícitamente
    quién es, o si necesitas tomar una decisión técnica/arquitectónica
    y necesitas conocer su stack. NO la uses para saludos simples.
    """
    logger.info("Executing user_profile skill...")

    return (
        "El usuario es Sebastián. Le apasiona el desarrollo de software y la tecnología. "
        "Su enfoque es estrictamente operativo: no busca conversar sobre sí mismo, "
        "sino orquestar tareas, definir arquitecturas y resolver problemas. "
        "Él es quien dirige las operaciones y tu único trabajo es asistirlo de forma directa."
    )
