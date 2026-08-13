import pytest
from pydantic import ValidationError

from app.ai.contracts.messages import ImagePart, NormalizedMessage, TextPart
from app.ai.contracts.models import ModelCapabilities, ModelDescriptor, ModelTaskType, Modality, ProviderType, make_model_key, parse_model_key
from app.ai.contracts.requests import (
    EmbeddingRequest, ImageGenerationRequest, ImageUnderstandingRequest,
    NormalizedChatRequest, RerankRequest, SpeechRecognitionRequest,
    SpeechSynthesisRequest, VideoUnderstandingRequest,
)
from app.ai.errors import CredentialInvalidError, ProviderNotFoundError, UnsupportedCapabilityError, UnsupportedModalityError, UnsupportedTaskError
from app.ai.providers.registry import ProviderRegistry
from app.ai.workflows.validation import validate_chat


def model(connection="c1"):
    return ModelDescriptor(key=make_model_key("deepseek", connection, "same"), connection_id=connection,
        provider=ProviderType.DEEPSEEK,id="same",display_name="same",source="provider_api",available=True,
        task_types=[ModelTaskType.CHAT],input_modalities=[Modality.TEXT],output_modalities=[Modality.TEXT],
        capabilities=ModelCapabilities(streaming=True,reasoning=True,reasoning_toggle=True,reasoning_efforts=["high"],tools=False))


def request(content=None, **options):
    return NormalizedChatRequest(conversation_id=1,model_key=model().key,
        messages=[NormalizedMessage(role="user",content=content or [TextPart(text="hello")])],options=options)


def test_model_keys_are_connection_scoped():
    assert model("a").key != model("b").key
    assert parse_model_key(model("a").key) == (ProviderType.DEEPSEEK,"a","same")


def test_provider_credential_failure_is_not_an_application_auth_401():
    assert CredentialInvalidError.status_code == 424


def test_registry_and_unknown_provider():
    registry=ProviderRegistry(); provider=type("P",(),{"provider_type":"test"})(); registry.register(provider)
    assert registry.get("test") is provider
    with pytest.raises(ProviderNotFoundError): registry.get("missing")


def test_capability_and_modality_fail_closed():
    validate_chat(model(),request())
    with pytest.raises(UnsupportedModalityError): validate_chat(model(),request([ImagePart(asset_id="asset")]))
    with pytest.raises(UnsupportedCapabilityError): validate_chat(model(),request(tools=[{"type":"function"}]))


def test_future_task_contract_validation():
    assert EmbeddingRequest(model_key="x",inputs=[{"id":"1","text":"x"}]).normalize
    assert RerankRequest(model_key="x",query="q",documents=[{"id":"1","text":"x"}]).top_n == 5
    assert SpeechSynthesisRequest(model_key="x",text="hello").format == "mp3"
    assert SpeechRecognitionRequest(model_key="x", asset_id="audio-1").asset_id == "audio-1"
    assert ImageUnderstandingRequest(model_key="x", asset_id="image-1", prompt="describe").prompt == "describe"
    assert ImageGenerationRequest(model_key="x", prompt="draw").prompt == "draw"
    assert VideoUnderstandingRequest(model_key="x", asset_id="video-1", prompt="summarize").asset_id == "video-1"
    with pytest.raises(ValidationError): EmbeddingRequest(model_key="x",inputs=[])


def test_chat_model_cannot_execute_embedding_workflow():
    embedding_only = model().model_copy(update={"task_types": [ModelTaskType.EMBEDDING]})
    with pytest.raises(UnsupportedTaskError):
        validate_chat(embedding_only, request())


def test_unknown_content_part_fails_schema_validation():
    with pytest.raises(ValidationError):
        NormalizedMessage.model_validate({"role": "user", "content": [{"type": "future", "value": "x"}]})
