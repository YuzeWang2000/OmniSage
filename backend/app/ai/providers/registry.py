from ..errors import ProviderNotFoundError


class ProviderRegistry:
    def __init__(self): self._providers = {}
    def register(self, provider):
        if provider.provider_type in self._providers:
            raise ValueError(f"provider already registered: {provider.provider_type}")
        self._providers[provider.provider_type] = provider
    def get(self, provider_type: str):
        try: return self._providers[provider_type]
        except KeyError: raise ProviderNotFoundError("provider is not registered") from None
    def all(self): return list(self._providers.values())


provider_registry = ProviderRegistry()

