from __future__ import annotations

import json

import httpx

from ...contracts.events import AIStreamEvent
from ...contracts.models import ConnectionTestResult, ModelCapabilities, ModelDescriptor, ModelTaskType, Modality, ProviderType, make_model_key
from ...contracts.requests import ReasoningMode
from ...errors import ProviderInvalidResponseError, ProviderTimeoutError, ProviderUnavailableError, UnsupportedModalityError


class OllamaProvider:
    provider_type = ProviderType.OLLAMA

    def supports_task(self, task_type):
        return task_type in {ModelTaskType.CHAT, ModelTaskType.EMBEDDING}

    async def _get(self, url):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("Ollama request timed out") from exc
        except ValueError as exc:
            raise ProviderInvalidResponseError("Ollama returned invalid JSON") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("Ollama is unavailable") from exc

    async def test_connection(self, connection, credential):
        await self._get(f"{connection.base_url}/api/tags")
        return ConnectionTestResult(ok=True, message="Ollama 可用")

    async def list_models(self, connection, credential):
        payload = await self._get(f"{connection.base_url}/api/tags")
        result = []
        async with httpx.AsyncClient(timeout=30) as client:
            for item in payload.get("models", []):
                model_id = item.get("model") or item.get("name")
                if not model_id: continue
                capabilities = []
                try:
                    shown = await client.post(f"{connection.base_url}/api/show", json={"model": model_id})
                    if shown.is_success: capabilities = shown.json().get("capabilities", [])
                except httpx.HTTPError:
                    pass
                tasks = []
                if "completion" in capabilities or "tools" in capabilities: tasks.append(ModelTaskType.CHAT)
                if "embedding" in capabilities: tasks.append(ModelTaskType.EMBEDDING)
                input_modalities = [Modality.TEXT]
                if "vision" in capabilities:
                    input_modalities.append(Modality.IMAGE)
                result.append(ModelDescriptor(
                    key=make_model_key(self.provider_type, connection.id, model_id), connection_id=connection.id,
                    provider=self.provider_type, id=model_id, display_name=model_id, source="local_runtime", available=True,
                    task_types=tasks, input_modalities=input_modalities, output_modalities=[Modality.TEXT],
                    capabilities=ModelCapabilities(streaming=ModelTaskType.CHAT in tasks, tools="tools" in capabilities,
                        reasoning="thinking" in capabilities, reasoning_toggle=True if "thinking" in capabilities else None),
                    metadata={"digest": item.get("digest"), "size": item.get("size"), "runtime_capabilities": capabilities},
                ))
        return result

    def build_chat_body(self, model, request, messages):
        body = {"model": model.id, "messages": messages, "stream": True}
        if request.options.temperature is not None:
            body["options"] = {"temperature": request.options.temperature}
        if request.options.reasoning != ReasoningMode.AUTO:
            body["think"] = request.options.reasoning == ReasoningMode.ON
        return body

    async def stream_chat(self, connection, model, request, credential):
        messages = []
        for message in request.messages:
            if any(part.type != "text" for part in message.content):
                raise UnsupportedModalityError("Ollama text chat does not accept asset parts yet")
            messages.append({"role": message.role, "content": message.text()})
        body = self.build_chat_body(model, request, messages)
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                async with client.stream("POST", f"{connection.base_url}/api/chat", json=body) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line: continue
                        chunk = json.loads(line)
                        message = chunk.get("message", {})
                        if message.get("thinking"): yield AIStreamEvent(type="reasoning_delta", content=message["thinking"])
                        if message.get("content"): yield AIStreamEvent(type="content_delta", content=message["content"])
                        if chunk.get("done"):
                            yield AIStreamEvent(type="usage", input_tokens=chunk.get("prompt_eval_count"), output_tokens=chunk.get("eval_count"))
            yield AIStreamEvent(type="done")
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("Ollama stream timed out") from exc
        except ValueError as exc:
            raise ProviderInvalidResponseError("Ollama returned invalid stream data") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("Ollama stream failed") from exc
