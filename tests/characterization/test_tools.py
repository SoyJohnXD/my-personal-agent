# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
from uuid import uuid4

import pytest

from src.db.memory.schema import Memory
from src.skills.user_memories.delete_memory import build_delete_memory_tool
from src.skills.user_memories.delete_memory import skill as delete_skill
from src.skills.user_memories.save_memory import build_save_memory_tool
from src.skills.user_memories.save_memory import skill as save_skill
from src.skills.user_memories.search_memories import build_search_memories_tool
from src.skills.user_memories.search_memories import skill as search_skill
from src.skills.user_memories.update_memory import build_update_memory_tool
from src.skills.user_memories.update_memory import skill as update_skill


class FakeRepo:
    def __init__(self):
        self.memory = Memory(id=uuid4(), title="Cafe", content="Le gusta el cafe", tags="#food")
        self.raise_error = False

    def create(self, **kwargs):
        if self.raise_error:
            raise RuntimeError("db down")
        return self.memory

    def search(self, text):
        if text == "none":
            return []
        return [self.memory]

    def update(self, id, **kwargs):
        if id != self.memory.id:
            return None
        if kwargs.get("title"):
            self.memory.title = kwargs["title"]
        return self.memory

    def delete(self, id):
        return id == self.memory.id


def test_user_memory_skill_strings_with_injected_repo():
    repo = FakeRepo()

    assert save_skill("Cafe", "Le gusta el cafe", ["food"], repository=repo) == f"Memoria 'Cafe' guardada con id {repo.memory.id}."
    assert search_skill("cafe", repository=repo) == f"ID:{repo.memory.id} | Cafe | #food | Le gusta el cafe"
    assert search_skill("none", repository=repo) == "Sin resultados."
    assert update_skill(repo.memory.id, title="Cafe nuevo", repository=repo) == "Memoria 'Cafe nuevo' actualizada."
    assert update_skill(uuid4(), title="Nada", repository=repo) == "No encontré esa memoria."
    assert delete_skill(repo.memory.id, repository=repo) == "Memoria borrada."
    assert delete_skill(uuid4(), repository=repo) == "No encontré esa memoria."


def test_user_memory_skill_error_and_validation_strings():
    repo = FakeRepo()
    repo.raise_error = True

    assert save_skill("Cafe", "Le gusta", ["food"], repository=repo).startswith("Error al guardar la memoria: db down")
    with pytest.raises(ValueError):
        save_skill("", "Le gusta", ["food"], repository=repo)


def test_user_memory_tool_factories_preserve_tool_names():
    repo = FakeRepo()
    assert build_delete_memory_tool(repo).name == "delete_memory"
    assert build_update_memory_tool(repo).name == "update_memory"
    assert build_save_memory_tool(repo).name == "save_memory"
    assert build_search_memories_tool(repo).name == "search_memories"


def test_assistant_factory_preserves_tool_order(monkeypatch):
    from src.agent.assistant import TOOL_ORDER, create_assistant
    from src.config.settings import Settings

    settings = Settings(agent_name="Hermenecio", user_name="Juan", api_key="key", api_base_url="https://example.test/v1", model_name="model-a")
    assistant = create_assistant(settings, model="test")

    assert TOOL_ORDER == ["delete_memory", "update_memory", "save_memory", "search_memories", "web_search", "scrape_webpage", "get_current_date"]
    assert list(assistant._function_toolset.tools.keys()) == TOOL_ORDER
