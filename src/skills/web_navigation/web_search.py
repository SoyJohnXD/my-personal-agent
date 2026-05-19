from ddgs import DDGS


def web_search(query: str) -> str:
    """
    Skill exclusiva para buscar conceptos generales, documentación técnica,
    noticias globales o definiciones estáticas.
    """
    print(f"\n🌐 [Skill]: Buscando en internet -> '{query}'")
    try:
        results = DDGS().text(query, max_results=3)

        if not results:
            return "No se encontraron resultados para esta búsqueda."

        formatted_results = "Resultados de la búsqueda:\n"
        for r in results:
            formatted_results += f"- Título: {r.get('title')}\n  URL: {r.get('href')}\n  Resumen: {r.get('body')}\n\n"

        return formatted_results

    except Exception as e:
        return f"Error al buscar en internet: {str(e)}"
