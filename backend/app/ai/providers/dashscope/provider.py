from ...contracts.models import ModelCapabilities, ModelDescriptor, ModelTaskType, Modality, ProviderType, make_model_key
from ...contracts.requests import ReasoningMode
from ...errors import InvalidModelOptionError, ProviderInvalidResponseError
from ..openai_compatible.provider import OpenAICompatibleProvider


class DashScopeProvider(OpenAICompatibleProvider):
    provider_type = ProviderType.DASHSCOPE

    @staticmethod
    def _model_profile(model_id: str, item: dict) -> tuple[list[ModelTaskType], list[Modality], list[Modality]]:
        """Classify catalog entries conservatively from provider metadata and documented model families."""
        raw_tasks = item.get("task_types") or item.get("tasks") or item.get("capabilities") or []
        if isinstance(raw_tasks, str):
            raw_tasks = [raw_tasks]
        aliases = {
            "chat": ModelTaskType.CHAT, "text-generation": ModelTaskType.TEXT_GENERATION,
            "text_generation": ModelTaskType.TEXT_GENERATION, "embedding": ModelTaskType.EMBEDDING,
            "rerank": ModelTaskType.RERANK, "text-to-speech": ModelTaskType.TEXT_TO_SPEECH,
            "text_to_speech": ModelTaskType.TEXT_TO_SPEECH, "speech-to-text": ModelTaskType.SPEECH_TO_TEXT,
            "speech_to_text": ModelTaskType.SPEECH_TO_TEXT, "image-generation": ModelTaskType.IMAGE_GENERATION,
            "image_generation": ModelTaskType.IMAGE_GENERATION, "image-understanding": ModelTaskType.IMAGE_UNDERSTANDING,
            "image_understanding": ModelTaskType.IMAGE_UNDERSTANDING, "video-generation": ModelTaskType.VIDEO_GENERATION,
            "video_generation": ModelTaskType.VIDEO_GENERATION, "video-understanding": ModelTaskType.VIDEO_UNDERSTANDING,
            "video_understanding": ModelTaskType.VIDEO_UNDERSTANDING,
        }
        tasks = list(dict.fromkeys(aliases[str(value).lower()] for value in raw_tasks if str(value).lower() in aliases))
        name = model_id.lower()
        if not tasks:
            if "embedding" in name:
                tasks = [ModelTaskType.EMBEDDING]
            elif "rerank" in name:
                tasks = [ModelTaskType.RERANK]
            elif any(token in name for token in ("paraformer", "sensevoice", "-asr", "_asr")):
                tasks = [ModelTaskType.SPEECH_TO_TEXT]
            elif any(token in name for token in ("cosyvoice", "sambert", "-tts", "_tts")):
                tasks = [ModelTaskType.TEXT_TO_SPEECH]
            elif any(token in name for token in ("qwen-image", "z-image", "wanx", "-t2i", "_t2i", "-i2i", "_i2i")) or (name.startswith("wan") and "image" in name):
                tasks = [ModelTaskType.IMAGE_GENERATION]
            elif any(token in name for token in ("-video", "_video", "text2video", "image2video", "reference2video", "-t2v", "_t2v", "-i2v", "_i2v")) and not any(token in name for token in ("qwen-vl", "qvq", "omni")):
                tasks = [ModelTaskType.VIDEO_GENERATION]
            elif any(token in name for token in ("qwen-vl", "qvq", "omni", "vision")):
                tasks = [ModelTaskType.CHAT, ModelTaskType.TEXT_GENERATION, ModelTaskType.IMAGE_UNDERSTANDING]
                if any(token in name for token in ("qwen-vl", "qvq", "omni")):
                    tasks.append(ModelTaskType.VIDEO_UNDERSTANDING)
            elif any(token in name for token in ("qwen", "deepseek", "kimi", "glm", "minimax", "llama", "mimo")):
                tasks = [ModelTaskType.CHAT, ModelTaskType.TEXT_GENERATION]

        if not tasks:
            return [], [], []
        inputs = [Modality.TEXT]
        outputs = [Modality.TEXT]
        if ModelTaskType.EMBEDDING in tasks and any(token in name for token in ("vl-embedding", "vision", "multimodal")):
            inputs = [Modality.TEXT, Modality.IMAGE, Modality.VIDEO]
        elif ModelTaskType.IMAGE_UNDERSTANDING in tasks:
            inputs = [Modality.TEXT, Modality.IMAGE]
            if ModelTaskType.VIDEO_UNDERSTANDING in tasks: inputs.append(Modality.VIDEO)
            if "omni" in name: inputs.append(Modality.AUDIO)
        elif ModelTaskType.IMAGE_GENERATION in tasks:
            outputs = [Modality.IMAGE]
        elif ModelTaskType.VIDEO_GENERATION in tasks:
            inputs = [Modality.TEXT, Modality.IMAGE]
            outputs = [Modality.VIDEO]
        elif ModelTaskType.SPEECH_TO_TEXT in tasks:
            inputs = [Modality.AUDIO]
        elif ModelTaskType.TEXT_TO_SPEECH in tasks:
            outputs = [Modality.AUDIO]
        return tasks, inputs, outputs

    async def list_models(self, connection, credential):
        payload = await self._json_get(f"{connection.base_url}/models", credential)
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise ProviderInvalidResponseError("DashScope returned an invalid model catalog")
        remote_items = {
            item["id"]: item for item in payload["data"]
            if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
        }
        remote_ids = list(remote_items)
        manual_ids = connection.config_json.get("manual_models", [])
        overrides = connection.config_json.get("manual_model_capabilities", {})
        # Explicit IDs are a whitelist. Without them, expose every remote candidate.
        ids = list(dict.fromkeys(manual_ids)) if manual_ids else remote_ids
        models = []
        for model_id in ids:
            item = remote_items.get(model_id, {})
            tasks, inputs, outputs = self._model_profile(model_id, item)
            models.append(ModelDescriptor(
                key=make_model_key(self.provider_type, connection.id, model_id), connection_id=connection.id,
                provider=self.provider_type, id=model_id, display_name=item.get("name") or model_id,
                source="manual" if manual_ids else "provider_api", available=True,
                task_types=tasks, input_modalities=inputs, output_modalities=outputs,
                capabilities=ModelCapabilities(
                    **{"streaming": True if ModelTaskType.CHAT in tasks else None, **(overrides.get(model_id) or {})}
                ), metadata={
                    "region": connection.region,
                    "authorization_unverified": not bool(manual_ids),
                    "owned_by": item.get("owned_by"),
                    "catalog_object": item.get("object"),
                    "classification_source": "provider_metadata" if item.get("task_types") or item.get("tasks") or item.get("capabilities") else "documented_family_rule",
                },
            ))
        return models

    async def test_connection(self, connection, credential):
        # Authenticate against the OpenAI-compatible endpoint without invoking a
        # paid inference task. This response is connectivity evidence only; it
        # is not treated as the user's callable model catalog.
        payload = await self._json_get(f"{connection.base_url}/models", credential)
        remote_models = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(remote_models, list):
            raise ProviderInvalidResponseError("DashScope returned an invalid model catalog")
        from ...contracts.models import ConnectionTestResult
        if not remote_models and not connection.config_json.get("manual_models"):
            return ConnectionTestResult(ok=True, message="连接配置有效；供应商未返回模型候选")
        return ConnectionTestResult(ok=True, message="连接配置有效")

    def build_chat_body(self, model, request):
        body = super().build_chat_body(model, request)
        if request.options.reasoning != ReasoningMode.AUTO:
            if model.capabilities.reasoning is not True:
                raise InvalidModelOptionError("model reasoning support is not confirmed")
            body["enable_thinking"] = request.options.reasoning == ReasoningMode.ON
        if request.options.reasoning_effort:
            if request.options.reasoning_effort not in model.capabilities.reasoning_efforts:
                raise InvalidModelOptionError("unsupported reasoning effort")
            body["reasoning_effort"] = request.options.reasoning_effort
        return body
