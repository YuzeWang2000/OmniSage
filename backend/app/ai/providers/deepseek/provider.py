from ...contracts.models import ModelCapabilities, ModelDescriptor, ModelTaskType, Modality, ProviderType, make_model_key
from ...contracts.requests import ReasoningMode
from ...errors import InvalidModelOptionError
from ..openai_compatible.provider import OpenAICompatibleProvider


class DeepSeekProvider(OpenAICompatibleProvider):
    provider_type = ProviderType.DEEPSEEK

    async def list_models(self, connection, credential):
        payload = await self._json_get(f"{connection.base_url}/models", credential)
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            from ...errors import ProviderInvalidResponseError
            raise ProviderInvalidResponseError("DeepSeek returned an invalid model catalog")
        return [ModelDescriptor(
            key=make_model_key(self.provider_type, connection.id, item["id"]), connection_id=connection.id,
            provider=self.provider_type, id=item["id"], display_name=item["id"], source="provider_api", available=True,
            task_types=[ModelTaskType.CHAT], input_modalities=[Modality.TEXT], output_modalities=[Modality.TEXT],
            capabilities=ModelCapabilities(streaming=True, reasoning=True, reasoning_toggle=True,
                reasoning_efforts=["high", "max"], tools=True, structured_output=True, json_output=True, function_calling=True),
            metadata={"owned_by": item.get("owned_by")},
        ) for item in payload.get("data", []) if item.get("id")]

    def build_chat_body(self, model, request):
        body = super().build_chat_body(model, request)
        mode = request.options.reasoning
        if mode != ReasoningMode.AUTO: body["thinking"] = {"type": "enabled" if mode == ReasoningMode.ON else "disabled"}
        if request.options.reasoning_effort:
            if request.options.reasoning_effort not in model.capabilities.reasoning_efforts:
                raise InvalidModelOptionError("unsupported reasoning effort")
            body["reasoning_effort"] = request.options.reasoning_effort
        if mode != ReasoningMode.OFF:
            body.pop("temperature", None)
        return body
