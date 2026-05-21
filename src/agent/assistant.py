from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


from src.agent.prompts import WHO_YOU_ARE
from src.config.settings import MODEL_NAME, API_KEY, API_BASE_URL
from src.skills.user_memories.delete_memory import delete_memory
from src.skills.user_memories.save_memory import save_memory
from src.skills.user_memories.search_memories import search_memories
from src.skills.user_memories.update_memory import update_memory
from src.skills.web_navigation.scrape_webpage import scrape_webpage
from src.skills.web_navigation.web_search import web_search

model_config = OpenAIChatModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    ),
)

assistant = Agent(model=model_config, system_prompt=WHO_YOU_ARE)


assistant.tool_plain(web_search)
assistant.tool_plain(scrape_webpage)

assistant.tool_plain(save_memory)
assistant.tool_plain(search_memories)
assistant.tool_plain(update_memory)
assistant.tool_plain(delete_memory)
