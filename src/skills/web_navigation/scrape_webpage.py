# === Imports ===

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, field_validator
from pydantic_ai.tools import Tool

from src.skills.directive import SkillDirective
from src.utils.logger import get_logger

# === Constants ===

skill_name = "scrape_webpage"
logger = get_logger(f"skill:web_navigation:{skill_name}")

BROWSER_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
MAX_CHARS = 2000

# === Validation ===


class ScrapeWebpageArgs(BaseModel):
    """Valida que la URL sea absoluta y tenga protocolo."""

    url: str = Field(..., min_length=1)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL debe empezar con http:// o https://")
        return v


# === Helpers ===


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=BROWSER_HEADERS, timeout=10)
    response.raise_for_status()
    return response.content


def extract_readable_text(html: bytes) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for noise in soup(NOISE_TAGS):
        noise.decompose()
    return soup.get_text(separator="\n", strip=True)


def truncate_result(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    return text[:MAX_CHARS] + "\n\n... [CONTENIDO TRUNCADO POR LONGITUD]"


# === Directive ===

directive = SkillDirective(
    objective=(
        "Visita una URL específica y extrae todo su texto limpio (Scraping). "
        "REGLA: Esta tool NO es un buscador; requiere obligatoriamente una "
        "URL exacta y absoluta (ej. 'https://www.dominio.com/...')."
    ),
    use_cases=[
        "El usuario te pasa explícitamente un link en el chat para que lo leas o lo resumas",
        "Obtuviste resultados breves usando web_search y necesitas profundizar leyendo la URL completa",
    ],
    avoid_when=[
        "No conoces una URL exacta",
        "Intentas usar esto como motor de búsqueda",
        "Ya leíste esta URL recientemente y ya adquiriste el contexto suficiente",
        "Ya tienes suficiente contexto de web_search para responder sin necesidad de leer la página completa",
    ],
)


# === Skill ===


def skill(url: str) -> str:
    parsed = ScrapeWebpageArgs(url=url)
    logger.info(f"Scraping: '{parsed.url}'")

    try:
        html = fetch_html(parsed.url)
        text = extract_readable_text(html)
        return truncate_result(text)

    except requests.Timeout:
        logger.error(f"Timeout al intentar leer: {url}")
        return f"Error: La página tardó demasiado en responder — {url}"
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return f"Error al leer la página: {e}"


# === Tool Registration ===

scrape_webpage = Tool(skill, name=skill_name, description=directive.compile_instructions())
