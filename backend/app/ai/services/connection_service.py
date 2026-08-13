from __future__ import annotations

import uuid
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ... import models
from ...config import settings
from ..contracts.models import ProviderProtocol, ProviderType
from ..errors import (
    ConnectionNotFoundError,
    ConnectionUnavailableError,
    CredentialMissingError,
    InvalidConnectionConfigError,
)
from ..security.credentials import decrypt_credential, encrypt_credential, mask_credential
from ..security.endpoint_validation import validate_endpoint


DASHSCOPE_BASE_URLS = {
    "cn-beijing": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "ap-southeast-1": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "us-east-1": "https://dashscope-us.aliyuncs.com/compatible-mode/v1",
}
WORKSPACE_REGIONS = {"cn-beijing", "ap-southeast-1", "ap-northeast-1", "eu-central-1"}
WORKSPACE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,62}$")


@dataclass(frozen=True)
class RuntimeConnection:
    """Provider-facing connection data that is safe after the ORM session closes."""

    id: str
    provider: str
    base_url: str
    region: str | None
    workspace_id: str | None
    config_json: dict


def runtime_snapshot(item) -> RuntimeConnection:
    return RuntimeConnection(
        id=item.id,
        provider=item.provider,
        base_url=item.base_url,
        region=item.region,
        workspace_id=item.workspace_id,
        config_json=dict(item.config_json or {}),
    )


def resolve_base_url(provider, region, workspace_id, custom):
    if provider == ProviderType.OLLAMA:
        return validate_endpoint(custom or settings.OLLAMA_BASE_URL, allow_local=True)
    if provider == ProviderType.DEEPSEEK:
        return "https://api.deepseek.com"
    if provider == ProviderType.DASHSCOPE:
        if custom: return validate_endpoint(custom)
        if not region:
            raise InvalidConnectionConfigError("region is required for DashScope")
        if workspace_id:
            if region not in WORKSPACE_REGIONS:
                raise InvalidConnectionConfigError("workspace_id is not supported for this region")
            if not WORKSPACE_ID_RE.fullmatch(workspace_id):
                raise InvalidConnectionConfigError("workspace_id format is invalid")
            return f"https://{workspace_id}.{region}.maas.aliyuncs.com/compatible-mode/v1"
        if region in DASHSCOPE_BASE_URLS:
            return DASHSCOPE_BASE_URLS[region]
        if region in WORKSPACE_REGIONS:
            raise InvalidConnectionConfigError("workspace_id is required for this region")
        raise InvalidConnectionConfigError("unsupported DashScope region")
    raise InvalidConnectionConfigError("unsupported provider")


def serialize(connection, *, include_mask=False):
    masked = None
    if include_mask and connection.encrypted_api_key:
        masked = mask_credential(decrypt_credential(connection.encrypted_api_key, settings.CREDENTIAL_ENCRYPTION_KEY))
    return {
        "id": connection.id, "provider": connection.provider, "display_name": connection.display_name,
        "protocol": connection.protocol, "region": connection.region, "base_url": connection.base_url,
        "workspace_id": connection.workspace_id, "config": connection.config_json or {}, "is_active": connection.is_active,
        "has_credential": bool(connection.encrypted_api_key), "masked_credential": masked,
        "credential_version": connection.credential_version, "last_tested_at": connection.last_tested_at,
        "last_test_status": connection.last_test_status, "last_test_message": connection.last_test_message,
        "created_at": connection.created_at, "updated_at": connection.updated_at,
    }


def get_owned(db: Session, user_id: int, connection_id: str):
    item = db.query(models.ProviderConnection).filter_by(id=connection_id, user_id=user_id).first()
    if not item: raise ConnectionNotFoundError("connection not found")
    return item


def require_active(item):
    if not item.is_active:
        raise ConnectionUnavailableError("connection is inactive")
    return item


def create(db, user_id, payload):
    provider = ProviderType(payload.provider)
    credential = payload.api_key
    if provider != ProviderType.OLLAMA and not credential: raise CredentialMissingError("api_key is required")
    item = models.ProviderConnection(
        id=str(uuid.uuid4()), user_id=user_id, provider=provider.value, display_name=payload.display_name,
        protocol=(ProviderProtocol.OLLAMA if provider == ProviderType.OLLAMA else ProviderProtocol.OPENAI_COMPATIBLE).value,
        region=payload.region, workspace_id=payload.workspace_id,
        base_url=resolve_base_url(provider, payload.region, payload.workspace_id, payload.base_url),
        encrypted_api_key=encrypt_credential(credential, settings.CREDENTIAL_ENCRYPTION_KEY) if credential else None,
        config_json={
            "manual_models": payload.manual_models,
            "manual_model_capabilities": {
                model_id: capabilities.model_dump()
                for model_id, capabilities in payload.manual_model_capabilities.items()
                if model_id in payload.manual_models
            },
        }, is_active=payload.is_active,
    )
    db.add(item); db.commit(); db.refresh(item); return item


def update(db, item, payload):
    data = payload.model_dump(exclude_unset=True)
    for field in ("display_name", "region", "workspace_id", "is_active"):
        if field in data: setattr(item, field, data[field])
    if any(field in data for field in ("region", "workspace_id", "base_url")):
        item.base_url = resolve_base_url(ProviderType(item.provider), item.region, item.workspace_id, data.get("base_url"))
    if "manual_models" in data:
        item.config_json = {**(item.config_json or {}), "manual_models": data["manual_models"]}
    if "manual_model_capabilities" in data:
        allowed = set(data.get("manual_models") or (item.config_json or {}).get("manual_models", []))
        item.config_json = {
            **(item.config_json or {}),
            "manual_model_capabilities": {
                model_id: capabilities.model_dump() if hasattr(capabilities, "model_dump") else capabilities
                for model_id, capabilities in data["manual_model_capabilities"].items()
                if model_id in allowed
            },
        }
    if data.get("api_key"):
        item.encrypted_api_key = encrypt_credential(data["api_key"], settings.CREDENTIAL_ENCRYPTION_KEY)
        item.credential_version += 1
    item.updated_at = datetime.now(timezone.utc); db.commit(); db.refresh(item); return item


def credential(item):
    return decrypt_credential(item.encrypted_api_key, settings.CREDENTIAL_ENCRYPTION_KEY)
