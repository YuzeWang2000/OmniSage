from dataclasses import dataclass

from ..contracts.models import ModelTaskType


@dataclass(frozen=True)
class WorkflowDescriptor:
    name: str
    required_tasks: tuple[ModelTaskType, ...]
    optional_tasks: tuple[ModelTaskType, ...] = ()
    required_capabilities: tuple[str, ...] = ()


WORKFLOWS = {
    "direct_chat": WorkflowDescriptor("direct_chat", (ModelTaskType.CHAT,)),
    "grounded_chat": WorkflowDescriptor("grounded_chat", (ModelTaskType.CHAT, ModelTaskType.EMBEDDING), (ModelTaskType.RERANK,)),
    "agent": WorkflowDescriptor("agent", (ModelTaskType.CHAT,), required_capabilities=("tools",)),
}

