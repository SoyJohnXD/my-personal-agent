import json
import os
from typing import List, Dict

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"
)
PREFERENCES_FILE = os.path.join(DATA_DIR, "preferences.json")
TAGS_FILE = os.path.join(DATA_DIR, "tags.json")


def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _load_json(filepath: str, default_data=None):
    if not os.path.exists(filepath):
        return default_data if default_data is not None else []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default_data if default_data is not None else []


def _save_json(filepath: str, data):
    _ensure_data_dir()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def _update_global_tags(new_tags: List[str]):
    all_tags = _load_json(TAGS_FILE, [])
    updated = False
    for tag in new_tags:
        tag_lower = tag.lower().strip()
        if tag_lower and tag_lower not in all_tags:
            all_tags.append(tag_lower)
            updated = True
    if updated:
        _save_json(TAGS_FILE, all_tags)


def save_preference(content: str, tags: List[str]) -> str:
    """
    Guarda una preferencia o recordatorio con sus tags correspondientes.
    """
    preferences = _load_json(PREFERENCES_FILE, [])

    # Procesar tags
    cleaned_tags = [t.lower().strip() for t in tags if t.strip()]
    _update_global_tags(cleaned_tags)

    new_pref = {"content": content, "tags": cleaned_tags}
    preferences.append(new_pref)
    _save_json(PREFERENCES_FILE, preferences)

    return f"Preferencia guardada exitosamente con los tags: {', '.join(cleaned_tags)}"


def get_preferences_by_tags(search_tags: List[str]) -> List[Dict]:
    """
    Busca preferencias que coincidan con alguno de los tags proporcionados.
    Solo busca entre los tags que ya existen globalmente.
    """
    all_tags = _load_json(TAGS_FILE, [])
    valid_search_tags = [
        t.lower().strip() for t in search_tags if t.lower().strip() in all_tags
    ]

    if not valid_search_tags:
        return []

    preferences = _load_json(PREFERENCES_FILE, [])
    matched_preferences = []

    for pref in preferences:
        pref_tags = pref.get("tags", [])
        # Si hay intersección entre los tags buscados y los tags de la preferencia
        if any(tag in pref_tags for tag in valid_search_tags):
            matched_preferences.append(pref)

    return matched_preferences
