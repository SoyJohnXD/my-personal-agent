import requests
from bs4 import BeautifulSoup
from src.utils.logger import get_logger

logger = get_logger("skill:web_navigation:scrape_webpage")


def fetch_html(url: str) -> str:
    BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=BROWSER_HEADERS, timeout=10)
    response.raise_for_status()
    return response.content


def extract_readable_text(html: bytes) -> str:
    NOISE_TAGS = [
        "script",
        "style",
        "noscript",
        "iframe",
        "nav",
        "header",
        "footer",
        "aside",
        "menu",
        "ins",
        "dialog",
        "svg",
        "canvas",
        "form",
    ]
    soup = BeautifulSoup(html, "html.parser")
    for noise in soup(NOISE_TAGS):
        noise.decompose()
    return soup.get_text(separator="\n", strip=True)


def truncate_result(text: str) -> str:
    MAX_CHARS = 4000
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + "\n\n... [CONTENIDO TRUNCADO POR LONGITUD]"


def scrape_webpage(url: str) -> str:
    """
    Visita una URL y extrae su contenido de texto limpio.
    Úsala para leer artículos, documentación o expandir un resultado de búsqueda.
    No la uses si ya tienes el contenido suficiente del contexto actual.
    """
    logger.info(f"Scraping: '{url}'")

    try:
        html = fetch_html(url)
        text = extract_readable_text(html)
        return truncate_result(text)

    except requests.Timeout:
        logger.error(f"Timeout al intentar leer: {url}")
        return f"Error: La página tardó demasiado en responder — {url}"
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return f"Error al leer la página: {e}"
