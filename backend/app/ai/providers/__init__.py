from .registry import provider_registry
from .deepseek import DeepSeekProvider
from .dashscope import DashScopeProvider
from .ollama import OllamaProvider


def register_builtin_providers():
    if provider_registry.all(): return provider_registry
    for provider in (OllamaProvider(), DeepSeekProvider(), DashScopeProvider()):
        provider_registry.register(provider)
    return provider_registry

