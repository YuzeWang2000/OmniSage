from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from ...contracts.events import AIStreamEvent
from ...contracts.messages import TextPart
from ...contracts.models import ConnectionTestResult, ModelTaskType
from ...errors import (
    CredentialInvalidError, ProviderInvalidResponseError,
    ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError,
    UnsupportedModalityError,
)


class OpenAICompatibleProvider:
    provider_type = "openai_compatible"
    timeout = 60.0

    def supports_task(self, task_type: ModelTaskType) -> bool:
        return task_type == ModelTaskType.CHAT

    def headers(self, credential: str | None) -> dict[str, str]:
        return {"Authorization": f"Bearer {credential}", "Content-Type": "application/json"}

    def map_messages(self, messages):
        mapped = []
        for message in messages:
            if not all(isinstance(part, TextPart) for part in message.content):
                raise UnsupportedModalityError("this provider currently supports text parts only")
            item: dict[str, Any] = {"role": message.role, "content": message.text()}
            if message.name: item["name"] = message.name
            if message.tool_call_id: item["tool_call_id"] = message.tool_call_id
            mapped.append(item)
        return mapped

    def build_chat_body(self, model, request):
        body: dict[str, Any] = {
            "model": model.id, "messages": self.map_messages(request.messages),
            "stream": True, "stream_options": {"include_usage": True},
        }
        if request.options.temperature is not None: body["temperature"] = request.options.temperature
        if request.options.tools: body["tools"] = request.options.tools
        if request.options.structured_output: body["response_format"] = {"type": "json_object"}
        return body

    async def test_connection(self, connection, credential):
        await self._json_get(f"{connection.base_url}/models", credential)
        return ConnectionTestResult(ok=True, message="连接成功")

    async def _json_get(self, url, credential):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers(credential))
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc: raise ProviderTimeoutError("provider request timed out") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 403}: raise CredentialInvalidError("provider rejected the credential") from exc
            if exc.response.status_code == 429: raise ProviderRateLimitError("provider rate limit reached") from exc
            raise ProviderUnavailableError("provider rejected the request") from exc
        except ValueError as exc: raise ProviderInvalidResponseError("provider returned invalid JSON") from exc
        except httpx.HTTPError as exc: raise ProviderUnavailableError("provider response is unavailable") from exc

    async def stream_chat(self, connection, model, request, credential) -> AsyncIterator[AIStreamEvent]:
        body = self.build_chat_body(model, request)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", f"{connection.base_url}/chat/completions", headers=self.headers(credential), json=body) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"): continue
                        data = line[5:].strip()
                        if data == "[DONE]": break
                        try: chunk = json.loads(data)
                        except ValueError as exc:
                            raise ProviderInvalidResponseError("provider returned invalid SSE data") from exc
                        if not isinstance(chunk, dict):
                            raise ProviderInvalidResponseError("provider returned invalid SSE event")
                        usage = chunk.get("usage")
                        if usage:
                            yield AIStreamEvent(type="usage", input_tokens=usage.get("prompt_tokens"), output_tokens=usage.get("completion_tokens"))
                        for choice in chunk.get("choices", []):
                            delta = choice.get("delta", {})
                            if delta.get("reasoning_content"): yield AIStreamEvent(type="reasoning_delta", content=delta["reasoning_content"])
                            if delta.get("content"): yield AIStreamEvent(type="content_delta", content=delta["content"])
                            for call in delta.get("tool_calls") or []: yield AIStreamEvent(type="tool_call", data=call)
            yield AIStreamEvent(type="done")
        except httpx.TimeoutException as exc: raise ProviderTimeoutError("provider stream timed out") from exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {401, 403}: raise CredentialInvalidError("provider rejected the credential") from exc
            if exc.response.status_code == 429: raise ProviderRateLimitError("provider rate limit reached") from exc
            raise ProviderUnavailableError("provider stream failed") from exc
        except httpx.HTTPError as exc: raise ProviderUnavailableError("provider stream failed") from exc
