from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol

from ..contracts.events import AIStreamEvent
from ..contracts.models import ConnectionTestResult, ModelDescriptor, ModelTaskType
from ..contracts.requests import (
    EmbeddingRequest, EmbeddingResponse, ImageGenerationRequest,
    ImageGenerationResponse, ImageUnderstandingRequest,
    ImageUnderstandingResponse, NormalizedChatRequest, RerankRequest,
    RerankResponse, SpeechRecognitionRequest, SpeechRecognitionResponse,
    SpeechSynthesisRequest, SpeechSynthesisResponse,
    VideoUnderstandingRequest, VideoUnderstandingResponse,
)


class AIProviderAdapter(Protocol):
    provider_type: str
    async def test_connection(self, connection, credential: str | None) -> ConnectionTestResult: ...
    async def list_models(self, connection, credential: str | None) -> list[ModelDescriptor]: ...
    def supports_task(self, task_type: ModelTaskType) -> bool: ...


class ChatProvider(Protocol):
    async def stream_chat(self, connection, model: ModelDescriptor, request: NormalizedChatRequest, credential: str | None) -> AsyncIterator[AIStreamEvent]: ...


class EmbeddingProvider(Protocol):
    async def embed(self, connection, model: ModelDescriptor, request: EmbeddingRequest, credential: str | None) -> EmbeddingResponse: ...


class RerankProvider(Protocol):
    async def rerank(self, connection, model: ModelDescriptor, request: RerankRequest, credential: str | None) -> RerankResponse: ...


class SpeechSynthesisProvider(Protocol):
    async def synthesize_speech(self, connection, model: ModelDescriptor, request: SpeechSynthesisRequest, credential: str | None) -> SpeechSynthesisResponse: ...


class SpeechRecognitionProvider(Protocol):
    async def recognize_speech(self, connection, model: ModelDescriptor, request: SpeechRecognitionRequest, credential: str | None) -> SpeechRecognitionResponse: ...


class ImageUnderstandingProvider(Protocol):
    async def understand_image(self, connection, model: ModelDescriptor, request: ImageUnderstandingRequest, credential: str | None) -> ImageUnderstandingResponse: ...


class ImageGenerationProvider(Protocol):
    async def generate_image(self, connection, model: ModelDescriptor, request: ImageGenerationRequest, credential: str | None) -> ImageGenerationResponse: ...


class VideoUnderstandingProvider(Protocol):
    async def understand_video(self, connection, model: ModelDescriptor, request: VideoUnderstandingRequest, credential: str | None) -> VideoUnderstandingResponse: ...
