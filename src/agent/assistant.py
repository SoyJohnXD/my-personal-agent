from src.skills.basic_data.get_current_date import get_current_date
from src.skills.user_memories.delete_memory import delete_memory
from src.skills.user_memories.save_memory import save_memory
from src.skills.user_memories.search_memories import search_memories
from src.skills.user_memories.update_memory import update_memory
from src.skills.web_navigation.scrape_webpage import scrape_webpage
from src.skills.web_navigation.web_search import web_search

DEFAULT_TOOLS = [delete_memory, update_memory, save_memory, search_memories, web_search, scrape_webpage, get_current_date]
