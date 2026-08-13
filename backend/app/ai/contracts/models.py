from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, computed_field


class ProviderType(StrEnum):
    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    DASHSCOPE = "dashscope"


class ProviderProtocol(StrEnum):
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"


class ModelTaskType(StrEnum):
    CHAT = "chat"
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    TEXT_TO_SPEECH = "text_to_speech"
    SPEECH_TO_TEXT = "speech_to_text"
    IMAGE_UNDERSTANDING = "image_understanding"
    IMAGE_GENERATION = "image_generation"
    VIDEO_UNDERSTANDING = "video_understanding"
    VIDEO_GENERATION = "video_generation"


class Modality(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class ModelCapabilities(BaseModel):
    streaming: bool | None = None
    reasoning: bool | None = None
    reasoning_toggle: bool | None = None
    reasoning_efforts: list[str] = Field(default_factory=list)
    tools: bool | None = None
    structured_output: bool | None = None
    json_output: bool | None = None
    function_calling: bool | None = None


class ModelLimits(BaseModel):
    context_window: int | None = None
    max_output_tokens: int | None = None
    max_input_items: int | None = None
    max_images: int | None = None
    max_audio_bytes: int | None = None


class ModelDescriptor(BaseModel):
    key: str
    connection_id: str
    provider: ProviderType
    id: str
    display_name: str
    source: Literal["provider_api", "provider_override", "manual", "local_runtime"]
    available: bool
    task_types: list[ModelTaskType]
    input_modalities: list[Modality]
    output_modalities: list[Modality]
    capabilities: ModelCapabilities = Field(default_factory=ModelCapabilities)
    limits: ModelLimits = Field(default_factory=ModelLimits)
    metadata: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stale: bool = False

    @computed_field
    @property
    def vision(self) -> bool:
        return Modality.IMAGE in self.input_modalities


def make_model_key(provider: ProviderType | str, connection_id: str, model_id: str) -> str:
    if not connection_id or not model_id or "::" in connection_id or "::" in model_id:
        raise ValueError("connection_id and model_id must be non-empty and cannot contain '::'")
    return f"{provider}::{connection_id}::{model_id}"


def parse_model_key(key: str) -> tuple[ProviderType, str, str]:
    parts = key.split("::", 2)
    if len(parts) != 3 or not all(parts):
        raise ValueError("invalid connection-scoped model key")
    return ProviderType(parts[0]), parts[1], parts[2]


class ConnectionTestResult(BaseModel):
    ok: bool
    message: str
    tested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
