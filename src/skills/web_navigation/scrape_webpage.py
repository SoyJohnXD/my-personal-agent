import requests
from bs4 import BeautifulSoup


def scrape_webpage(url: str) -> str:
    """
    Usa esta herramienta para visitar una URL específica y extraer su contenido de texto.
    Ideal para leer artículos, documentación o expandir un resultado de búsqueda.
    """
    print(f"\n📄 [Skill]: Extrayendo contenido de -> {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        text_content = soup.get_text(separator="\n", strip=True)

        max_chars = 15000
        if len(text_content) > max_chars:
            text_content = (
                text_content[:max_chars] + "\n\n... [CONTENIDO TRUNCADO POR LONGITUD]"
            )

        return f"Contenido extraído de {url}:\n\n{text_content}"

    except requests.Timeout:
        return f"Error: La página {url} tardó demasiado en responder."
    except Exception as e:
        return f"Error al intentar leer {url}: {str(e)}"
