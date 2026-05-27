from uuid import UUID

from pydantic_ai.messages import ModelRequest, ModelResponse, ToolReturnPart
from pydantic_ai.usage import Usage

from src.config.settings import MODEL_NAME
from src.db.token_usage.interface import ITokenUsageRepository
from src.db.token_usage.repository import TokenUsageRepository
from src.utils import logger

logger = logger.get_logger("gateways:shared_utils")


def _response_usage(response: ModelResponse) -> Usage:
    usage = response.usage
    return usage() if callable(usage) else usage


def track_token_usage_by_response(
    response: ModelResponse,
    session_id: UUID,
    user_text: str,
    *,
    token_usage_repo: ITokenUsageRepository | None = None,
    model_name: str | None = None,
) -> None:
    usage = _response_usage(response)
    repository = token_usage_repo or TokenUsageRepository()
    repository.create(
        model=model_name or MODEL_NAME,
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
    while cut_index > 0 and isinstance(messages[cut_index], ModelResponse) and is_tool_return_message(messages[cut_index - 1]):
        cut_index -= 1
    return messages[cut_index:]


def is_tool_return_message(message: object) -> bool:
    return isinstance(message, ModelRequest) and any(isinstance(part, ToolReturnPart) for part in message.parts)
