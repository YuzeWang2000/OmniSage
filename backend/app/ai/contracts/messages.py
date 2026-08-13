from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field


class TextPart(BaseModel):
    type: Literal["text"] = "text"
    text: str = Field(min_length=1)


class ImagePart(BaseModel):
    type: Literal["image"] = "image"
    asset_id: str
    detail: Literal["auto", "low", "high"] = "auto"


class AudioPart(BaseModel):
    type: Literal["audio"] = "audio"
    asset_id: str


class VideoPart(BaseModel):
    type: Literal["video"] = "video"
    asset_id: str


class DocumentPart(BaseModel):
    type: Literal["document"] = "document"
    asset_id: str


class ToolResultPart(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_call_id: str
    content: str


ContentPart = Annotated[
    Union[TextPart, ImagePart, AudioPart, VideoPart, DocumentPart, ToolResultPart],
    Field(discriminator="type"),
]


class NormalizedMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: list[ContentPart]
    name: str | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def text(self) -> str:
        return "\n".join(part.text for part in self.content if isinstance(part, TextPart))

