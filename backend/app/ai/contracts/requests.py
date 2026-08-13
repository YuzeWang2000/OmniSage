from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from .messages import NormalizedMessage


class ReasoningMode(StrEnum):
    OFF = "off"
    AUTO = "auto"
    ON = "on"


class WorkflowType(StrEnum):
    DIRECT_CHAT = "direct_chat"
    GROUNDED_CHAT = "grounded_chat"
    AGENT = "agent"


class ChatOptions(BaseModel):
    reasoning: ReasoningMode = ReasoningMode.AUTO
    reasoning_effort: str | None = None
    temperature: float | None = Field(default=None, ge=0, le=2)
    structured_output: bool = False
    tools: list[dict[str, Any]] = Field(default_factory=list)


class RetrievalOptions(BaseModel):
    enabled: bool = False
    wiki: bool = False
    knowledge_base_id: int | None = None
    use_reranker: bool = True
    top_k: int = Field(default=5, ge=1, le=50)
    score_threshold: float = Field(default=0.5, ge=0, le=1)


class ModelSlots(BaseModel):
    generation_model_key: str | None = None
    embedding_model_key: str | None = None
    rerank_model_key: str | None = None
    speech_model_key: str | None = None


class NormalizedChatRequest(BaseModel):
    conversation_id: int
    messages: list[NormalizedMessage] = Field(min_length=1)
    model_key: str
    workflow: WorkflowType = WorkflowType.DIRECT_CHAT
    options: ChatOptions = Field(default_factory=ChatOptions)
    retrieval: RetrievalOptions = Field(default_factory=RetrievalOptions)
    model_slots: ModelSlots = Field(default_factory=ModelSlots)
    regenerate: bool = False

    @model_validator(mode="after")
    def validate_workflow(self):
        if self.workflow == WorkflowType.GROUNDED_CHAT:
            if not self.retrieval.enabled:
                raise ValueError("grounded_chat requires retrieval.enabled=true")
            if not self.retrieval.wiki and self.retrieval.knowledge_base_id is None:
                raise ValueError("grounded_chat requires knowledge_base_id unless Wiki retrieval is enabled")
        return self


class EmbeddingInput(BaseModel):
    id: str
    text: str = Field(min_length=1)


class EmbeddingRequest(BaseModel):
    model_key: str
    inputs: list[EmbeddingInput] = Field(min_length=1)
    dimensions: int | None = Field(default=None, gt=0)
    normalize: bool = True


class EmbeddingVector(BaseModel):
    id: str
    embedding: list[float]


class EmbeddingResponse(BaseModel):
    vectors: list[EmbeddingVector]
    dimensions: int = Field(gt=0)
    usage: dict[str, Any] = Field(default_factory=dict)


class RerankDocument(BaseModel):
    id: str
    text: str = Field(min_length=1)


class RerankRequest(BaseModel):
    model_key: str
    query: str = Field(min_length=1)
    documents: list[RerankDocument] = Field(min_length=1)
    top_n: int = Field(default=5, gt=0)


class RerankResult(BaseModel):
    document_id: str
    index: int = Field(ge=0)
    score: float


class RerankResponse(BaseModel):
    results: list[RerankResult]
    usage: dict[str, Any] = Field(default_factory=dict)


class SpeechSynthesisRequest(BaseModel):
    model_key: str
    text: str = Field(min_length=1)
    voice: str | None = None
    format: Literal["mp3", "wav", "opus"] = "mp3"
    speed: float = Field(default=1.0, ge=0.25, le=4)


class SpeechSynthesisResponse(BaseModel):
    asset_id: str
    mime_type: str
    duration_ms: int | None = None


class AssetTaskRequest(BaseModel):
    model_key: str
    asset_id: str = Field(min_length=1)


class SpeechRecognitionRequest(AssetTaskRequest):
    language: str | None = None


class SpeechRecognitionResponse(BaseModel):
    text: str
    language: str | None = None
    segments: list[dict[str, Any]] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)


class ImageUnderstandingRequest(AssetTaskRequest):
    prompt: str = Field(min_length=1)


class ImageUnderstandingResponse(BaseModel):
    content: list[dict[str, Any]] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)


class ImageGenerationRequest(BaseModel):
    model_key: str
    prompt: str = Field(min_length=1)
    size: str | None = None


class ImageGenerationResponse(BaseModel):
    asset_ids: list[str] = Field(min_length=1)
    usage: dict[str, Any] = Field(default_factory=dict)


class VideoUnderstandingRequest(AssetTaskRequest):
    prompt: str = Field(min_length=1)


class VideoUnderstandingResponse(BaseModel):
    content: list[dict[str, Any]] = Field(default_factory=list)
    usage: dict[str, Any] = Field(default_factory=dict)
