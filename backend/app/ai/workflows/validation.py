from ..contracts.models import ModelTaskType, Modality
from ..contracts.requests import ReasoningMode
from ..errors import InvalidModelOptionError, ModelUnavailableError, UnsupportedCapabilityError, UnsupportedModalityError, UnsupportedTaskError
from .contracts import WORKFLOWS


def validate_chat(model, request):
    if not model.available: raise ModelUnavailableError("model is unavailable")
    if ModelTaskType.CHAT not in model.task_types: raise UnsupportedTaskError("model does not support chat")
    for message in request.messages:
        for part in message.content:
            modality = Modality.TEXT if part.type in {"text", "tool_result"} else Modality(part.type)
            if modality not in model.input_modalities: raise UnsupportedModalityError(f"model does not support {modality}")
    workflow = WORKFLOWS[request.workflow.value]
    for capability in workflow.required_capabilities:
        if getattr(model.capabilities, capability, None) is not True: raise UnsupportedCapabilityError(f"workflow requires {capability}")
    if request.options.reasoning != ReasoningMode.AUTO and model.capabilities.reasoning is not True:
        raise UnsupportedCapabilityError("model reasoning support is not confirmed")
    if request.options.reasoning_effort and request.options.reasoning_effort not in model.capabilities.reasoning_efforts:
        raise InvalidModelOptionError("reasoning effort is not supported")
    if request.options.tools and model.capabilities.tools is not True: raise UnsupportedCapabilityError("model does not support tools")
    if request.options.structured_output and model.capabilities.structured_output is not True: raise UnsupportedCapabilityError("model does not support structured output")

