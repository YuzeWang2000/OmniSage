import pytest
from app.ai.security.credentials import decrypt_credential, encrypt_credential, mask_credential
from app.ai.security.endpoint_validation import validate_endpoint
from app.ai.errors import InvalidConnectionConfigError, UnsafeEndpointError
from app.ai.services.connection_service import resolve_base_url
from app.ai.contracts.models import ProviderType


def test_credentials_encrypt_and_do_not_echo():
    encrypted=encrypt_credential("sk-super-secret","test-key")
    assert "sk-super-secret" not in encrypted
    assert decrypt_credential(encrypted,"test-key") == "sk-super-secret"
    assert mask_credential("sk-super-secret") == "sk-••••ret"
    assert "super" not in mask_credential("sk-super-secret")


def test_endpoint_rejects_unsafe_protocol():
    with pytest.raises(UnsafeEndpointError): validate_endpoint("file:///etc/passwd")


def test_workspace_id_cannot_escape_trusted_template():
    with pytest.raises(InvalidConnectionConfigError):
        resolve_base_url(ProviderType.DASHSCOPE, "cn-beijing", "bad.example/escape", None)


def test_dashscope_public_regions_do_not_require_workspace():
    assert resolve_base_url(ProviderType.DASHSCOPE, "cn-beijing", None, None) == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert resolve_base_url(ProviderType.DASHSCOPE, "ap-southeast-1", None, None) == "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    assert resolve_base_url(ProviderType.DASHSCOPE, "us-east-1", None, None) == "https://dashscope-us.aliyuncs.com/compatible-mode/v1"


def test_dashscope_workspace_regions_and_validation():
    assert resolve_base_url(ProviderType.DASHSCOPE, "cn-beijing", "workspace-1", None) == "https://workspace-1.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    with pytest.raises(InvalidConnectionConfigError) as missing:
        resolve_base_url(ProviderType.DASHSCOPE, "ap-northeast-1", None, None)
    assert getattr(missing.value, "status_code", None) == 422
