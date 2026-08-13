from typing import Any, Literal

from pydantic import BaseModel


class AIStreamEvent(BaseModel):
    type: Literal[
        "content_delta", "reasoning_delta", "tool_call", "tool_result",
        "citation", "media", "usage", "done", "error"
    ]
    content: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    data: dict[str, Any] | None = None
    code: str | None = None
    message: str | None = None

