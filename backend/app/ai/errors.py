class AIError(Exception):
    code = "AIError"
    status_code = 400


class ProviderNotFoundError(AIError): code, status_code = "ProviderNotFound", 404
class ConnectionNotFoundError(AIError): code, status_code = "ConnectionNotFound", 404
class ConnectionUnavailableError(AIError): code, status_code = "ConnectionUnavailable", 503
class CredentialMissingError(AIError): code, status_code = "CredentialMissing", 422
# 401 is reserved for OmniSage authentication. A provider rejecting its own
# credential is an upstream dependency failure and must not log the user out.
class CredentialInvalidError(AIError): code, status_code = "CredentialInvalid", 424
class ModelNotFoundError(AIError): code, status_code = "ModelNotFound", 404
class ModelUnavailableError(AIError): code, status_code = "ModelUnavailable", 409
class UnsupportedTaskError(AIError): code = "UnsupportedTask"
class UnsupportedCapabilityError(AIError): code = "UnsupportedCapability"
class UnsupportedModalityError(AIError): code = "UnsupportedModality"
class InvalidModelOptionError(AIError): code = "InvalidModelOption"
class InvalidConnectionConfigError(AIError): code, status_code = "InvalidConnectionConfig", 422
class InvalidRetrievalConfigError(AIError): code, status_code = "InvalidRetrievalConfig", 422
class KnowledgeBaseNotFoundError(AIError): code, status_code = "KnowledgeBaseNotFound", 404
class ProviderRateLimitError(AIError): code, status_code = "ProviderRateLimit", 429
class ProviderTimeoutError(AIError): code, status_code = "ProviderTimeout", 504
class ProviderUnavailableError(AIError): code, status_code = "ProviderUnavailable", 503
class ProviderInvalidResponseError(AIError): code, status_code = "ProviderInvalidResponse", 502
class UnsafeEndpointError(AIError): code, status_code = "UnsafeEndpoint", 422
