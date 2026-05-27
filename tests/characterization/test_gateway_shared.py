# ruff: noqa: ANN001,ANN002,ANN003,ANN201,ANN204,ARG001,ARG002
from uuid import uuid4

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ToolReturnPart

from src.gateways.shared.utils import control_history, track_token_usage_by_response


class Usage:
    input_tokens = 7
    output_tokens = 3
    total_tokens = 10


class FakeResponse:
    output = "respuesta"
    usage = Usage()


class FakeRepo:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)


def test_control_history_keeps_tool_return_context_at_cut_boundary():
    messages = [
        ModelRequest(parts=[TextPart(content="old")]),
        ModelRequest(parts=[ToolReturnPart(tool_name="search_memories", content="dato", tool_call_id="call-1")]),
        ModelResponse(parts=[TextPart(content="respuesta con dato")]),
        ModelRequest(parts=[TextPart(content="new")]),
    ]

    trimmed = control_history(messages, limit=2)

    assert trimmed == messages[1:]


def test_track_token_usage_accepts_injected_repo_and_model():
    repo = FakeRepo()
    session_id = uuid4()

    track_token_usage_by_response(FakeResponse(), session_id, "hola", token_usage_repo=repo, model_name="model-a")

    assert repo.calls == [
        {
            "model": "model-a",
            "session_id": session_id,
            "user_message": "hola",
            "assistant_response": "respuesta",
            "input_tokens": 7,
            "output_tokens": 3,
            "total_tokens": 10,
        }
    ]
