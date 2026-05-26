from uuid import UUID

from pydantic_ai.messages import ModelRequest, ModelResponse, ToolReturnPart

from src.config.settings import MODEL_NAME
from src.db.token_usage.repository import TokenUsageRepository
from src.utils import logger

logger = logger.get_logger("gateways:shared_utils")

token_usage_repo = TokenUsageRepository()


def track_token_usage_by_response(response: ModelResponse, session_id: UUID, user_text: str) -> None:
    usage = response.usage
    token_usage_repo.create(
        model=MODEL_NAME,
        session_id=session_id,
        user_message=user_text,
        assistant_response=response.output,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        total_tokens=usage.total_tokens,
    )
    logger.info(f"Token usage | input: {usage.input_tokens} | output: {usage.output_tokens} | total: {usage.total_tokens}")


def control_history(messages: list, limit: int) -> list:
    if len(messages) <= limit:
        return messages

    cut_index = len(messages) - limit

    while cut_index > 0:
        msg = messages[cut_index]
        is_tool = False

        if isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, ToolReturnPart):
                    is_tool = True
                    break

        if is_tool:
            cut_index -= 1
        else:
            break

    return messages[cut_index:]
