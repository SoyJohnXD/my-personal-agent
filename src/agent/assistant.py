from collections.abc import Sequence
from typing import Any

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.tools import Tool

from src.agent.prompts import build_who_you_are
from src.config.settings import Settings, load_settings
from src.skills.basic_data.get_current_date import get_current_date
from src.skills.user_memories.delete_memory import delete_memory
from src.skills.user_memories.save_memory import save_memory
from src.skills.user_memories.search_memories import search_memories
from src.skills.user_memories.update_memory import update_memory
from src.skills.web_navigation.scrape_webpage import scrape_webpage
from src.skills.web_navigation.web_search import web_search

TOOL_ORDER = ["delete_memory", "update_memory", "save_memory", "search_memories", "web_search", "scrape_webpage", "get_current_date"]
DEFAULT_TOOLS = [delete_memory, update_memory, save_memory, search_memories, web_search, scrape_webpage, get_current_date]


def create_model(settings: Settings) -> OpenAIChatModel:
    return OpenAIChatModel(settings.model_name, provider=OpenAIProvider(base_url=settings.api_base_url, api_key=settings.api_key))


def create_assistant(settings: Settings, tools: Sequence[Tool] | None = None, model: Any | None = None) -> Agent:
    return Agent(model=model or create_model(settings), system_prompt=build_who_you_are(settings), tools=list(tools or DEFAULT_TOOLS))


class LazyAssistant:
    _assistant: Agent | None = None

    def _get_assistant(self) -> Agent:
        if self._assistant is None:
            self._assistant = create_assistant(load_settings())
        return self._assistant

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get_assistant(), name)


assistant = LazyAssistant()
