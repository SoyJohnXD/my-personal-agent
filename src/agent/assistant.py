from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from src.skills.safe_preferences import get_preferences_by_tags, save_preference
from src.config.settings import MODEL_NAME, API_KEY, API_BASE_URL
from src.agent.prompts import WHO_ARE_YOU
from src.skills.user_profile import user_profile
from src.skills.web_navigation.scrape_webpage import scrape_webpage
from src.skills.web_navigation.web_search import web_search

model_config = OpenAIChatModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    ),
)

assistant = Agent(
    model=model_config,
    system_prompt=WHO_ARE_YOU,
)

assistant.tool_plain(user_profile)
assistant.tool_plain(web_search)
assistant.tool_plain(scrape_webpage)
assistant.tool_plain(save_preference)
assistant.tool_plain(get_preferences_by_tags)
