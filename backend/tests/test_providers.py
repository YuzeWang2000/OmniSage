from types import SimpleNamespace

import pytest

from app.ai.contracts.messages import NormalizedMessage, TextPart
from app.ai.contracts.models import ModelTaskType
from app.ai.contracts.requests import ChatOptions, NormalizedChatRequest, ReasoningMode
from app.ai.errors import ProviderInvalidResponseError
from app.ai.providers.deepseek import DeepSeekProvider
from app.ai.providers.dashscope import DashScopeProvider
from app.ai.providers.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_deepseek_uses_discovered_ids(monkeypatch):
    provider=DeepSeekProvider()
    async def fake(*_): return {"data":[{"id":"live-model","owned_by":"deepseek"}]}
    monkeypatch.setattr(provider,"_json_get",fake)
    models=await provider.list_models(SimpleNamespace(base_url="https://api.deepseek.com",id="c"),"secret")
    assert [m.id for m in models] == ["live-model"]
    assert models[0].task_types == [ModelTaskType.CHAT]


@pytest.mark.asyncio
async def test_dashscope_explicit_models_are_a_whitelist(monkeypatch):
    provider=DashScopeProvider(); connection=SimpleNamespace(id="c",base_url="https://example.com/v1",region="cn-beijing",config_json={"manual_models":["qwen-custom"]})
    async def fake(*_): return {"data": [{"id": "qwen-plus"}, {"id": "qwen-custom"}]}
    monkeypatch.setattr(provider, "_json_get", fake)
    models=await provider.list_models(connection,"secret")
    assert [(model.id, model.source) for model in models] == [("qwen-custom", "manual")]
    assert models[0].metadata["authorization_unverified"] is False


@pytest.mark.asyncio
async def test_dashscope_without_whitelist_returns_and_classifies_remote_catalog(monkeypatch):
    provider = DashScopeProvider()
    connection = SimpleNamespace(
        id="c", base_url="https://example.com/v1", region="cn-beijing",
        config_json={"manual_models": []},
    )
    async def fake(*_):
        return {"data": [
            {"id": "qwen-plus"}, {"id": "text-embedding-v4"},
            {"id": "qwen-image-plus"}, {"id": "qwen-audio-asr"},
            {"id": "future-model", "task_types": ["rerank"]},
        ]}
    monkeypatch.setattr(provider, "_json_get", fake)
    models = {model.id: model for model in await provider.list_models(connection, "secret")}
    assert models["qwen-plus"].task_types == [ModelTaskType.CHAT, ModelTaskType.TEXT_GENERATION]
    assert models["text-embedding-v4"].task_types == [ModelTaskType.EMBEDDING]
    assert models["qwen-image-plus"].task_types == [ModelTaskType.IMAGE_GENERATION]
    assert models["qwen-audio-asr"].task_types == [ModelTaskType.SPEECH_TO_TEXT]
    assert models["future-model"].task_types == [ModelTaskType.RERANK]
    assert all(model.metadata["authorization_unverified"] is True for model in models.values())


@pytest.mark.asyncio
async def test_dashscope_manual_capability_override_is_explicit(monkeypatch):
    provider = DashScopeProvider()
    connection = SimpleNamespace(
        id="c", base_url="https://example.com/v1",
        region="cn-beijing",
        config_json={
            "manual_models": ["user-confirmed-model"],
            "manual_model_capabilities": {
                "user-confirmed-model": {
                    "reasoning": True,
                    "reasoning_toggle": True,
                    "reasoning_efforts": ["high"],
                }
            },
        },
    )
    async def fake(*_): return {"data": []}
    monkeypatch.setattr(provider, "_json_get", fake)
    model = (await provider.list_models(connection, "secret"))[0]
    assert model.capabilities.reasoning is True
    assert model.capabilities.reasoning_efforts == ["high"]


@pytest.mark.asyncio
async def test_dashscope_connection_test_is_remote_but_does_not_infer(monkeypatch):
    provider = DashScopeProvider()
    calls = []
    async def fake(url, credential):
        calls.append((url, credential))
        return {"data": []}
    monkeypatch.setattr(provider, "_json_get", fake)
    connection = SimpleNamespace(
        id="c", base_url="https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
        region="cn-beijing", config_json={"manual_models": []},
    )
    result = await provider.test_connection(connection, "secret")
    assert result.ok
    assert calls == [(f"{connection.base_url}/models", "secret")]


@pytest.mark.asyncio
async def test_dashscope_rejects_malformed_remote_catalog(monkeypatch):
    provider = DashScopeProvider()
    async def fake(*_): return {"unexpected": []}
    monkeypatch.setattr(provider, "_json_get", fake)
    connection = SimpleNamespace(
        id="c", base_url="https://example.com/v1", region="cn-beijing",
        config_json={"manual_models": []},
    )
    with pytest.raises(ProviderInvalidResponseError):
        await provider.list_models(connection, "secret")
    with pytest.raises(ProviderInvalidResponseError):
        await provider.test_connection(connection, "secret")


def test_provider_task_support_is_explicit():
    assert DeepSeekProvider().supports_task(ModelTaskType.CHAT)
    assert not DeepSeekProvider().supports_task(ModelTaskType.EMBEDDING)
    assert OllamaProvider().supports_task(ModelTaskType.EMBEDDING)
    assert not OllamaProvider().supports_task(ModelTaskType.RERANK)


def test_deepseek_reasoning_mapping_filters_temperature():
    provider = DeepSeekProvider()
    descriptor = SimpleNamespace(id="dynamic-model", capabilities=SimpleNamespace(reasoning_efforts=["high", "max"]))
    request = NormalizedChatRequest(
        conversation_id=1,
        model_key="deepseek::c::dynamic-model",
        messages=[NormalizedMessage(role="user", content=[TextPart(text="hello")])],
        options=ChatOptions(reasoning=ReasoningMode.ON, reasoning_effort="max", temperature=0.7),
    )
    body = provider.build_chat_body(descriptor, request)
    assert body["thinking"] == {"type": "enabled"}
    assert body["reasoning_effort"] == "max"
    assert "temperature" not in body


def test_ollama_reasoning_mapping_uses_official_think_field():
    provider = OllamaProvider()
    request = NormalizedChatRequest(
        conversation_id=1,
        model_key="ollama::c::model",
        messages=[NormalizedMessage(role="user", content=[TextPart(text="hello")])],
        options=ChatOptions(reasoning=ReasoningMode.OFF, temperature=0.2),
    )
    body = provider.build_chat_body(SimpleNamespace(id="model"), request, [{"role": "user", "content": "hello"}])
    assert body["think"] is False
    assert body["options"] == {"temperature": 0.2}


@pytest.mark.asyncio
async def test_deepseek_rejects_malformed_catalog(monkeypatch):
    provider = DeepSeekProvider()
    async def fake(*_): return {"unexpected": []}
    monkeypatch.setattr(provider, "_json_get", fake)
    with pytest.raises(ProviderInvalidResponseError):
        await provider.list_models(SimpleNamespace(base_url="https://api.deepseek.com", id="c"), "secret")


@pytest.mark.asyncio
async def test_ollama_discovery_uses_runtime_capabilities(monkeypatch):
    provider = OllamaProvider()
    async def fake_get(_):
        return {"models": [{"model": "chat"}, {"model": "embed"}, {"model": "unknown"}]}
    monkeypatch.setattr(provider, "_get", fake_get)

    class Response:
        def __init__(self, capabilities):
            self.is_success = True
            self._capabilities = capabilities
        def json(self):
            return {"capabilities": self._capabilities}

    class Client:
        async def __aenter__(self): return self
        async def __aexit__(self, *_): return None
        async def post(self, url, json):
            mapping = {"chat": ["completion", "vision", "thinking"], "embed": ["embedding"], "unknown": []}
            return Response(mapping[json["model"]])

    monkeypatch.setattr("app.ai.providers.ollama.provider.httpx.AsyncClient", lambda **_: Client())
    models = await provider.list_models(SimpleNamespace(base_url="http://localhost:11434", id="c"), None)
    by_id = {model.id: model for model in models}
    assert by_id["chat"].task_types == [ModelTaskType.CHAT]
    assert by_id["chat"].vision is True
    assert by_id["chat"].capabilities.reasoning is True
    assert by_id["embed"].task_types == [ModelTaskType.EMBEDDING]
    assert by_id["unknown"].task_types == []
