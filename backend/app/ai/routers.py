from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..security import AuthenticatedUser, get_current_user
from .contracts.models import ModelCapabilities, ModelTaskType, Modality, ProviderType
from .errors import AIError
from .providers import register_builtin_providers
from .services import connection_service, model_catalog_service

router = APIRouter(prefix="/ai", tags=["ai"])


def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()


class ConnectionCreate(BaseModel):
    provider: ProviderType
    display_name: str = Field(min_length=1, max_length=100)
    region: str | None = None
    base_url: str | None = None
    workspace_id: str | None = None
    api_key: str | None = Field(default=None, min_length=8)
    manual_models: list[str] = Field(default_factory=list)
    manual_model_capabilities: dict[str, ModelCapabilities] = Field(default_factory=dict)
    is_active: bool = True

    @field_validator("display_name", "region", "base_url", "workspace_id", "api_key", mode="before")
    @classmethod
    def strip_text_fields(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("manual_models", mode="after")
    @classmethod
    def normalize_manual_models(cls, values):
        return list(dict.fromkeys(value.strip() for value in values if value.strip()))

    @model_validator(mode="after")
    def validate_provider_fields(self):
        if self.provider == ProviderType.DASHSCOPE and not self.region:
            raise ValueError("region is required for DashScope")
        return self


class ConnectionUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    region: str | None = None
    base_url: str | None = None
    workspace_id: str | None = None
    api_key: str | None = Field(default=None, min_length=8)
    manual_models: list[str] | None = None
    manual_model_capabilities: dict[str, ModelCapabilities] | None = None
    is_active: bool | None = None

    @field_validator("display_name", "region", "base_url", "workspace_id", "api_key", mode="before")
    @classmethod
    def strip_text_fields(cls, value):
        return value.strip() if isinstance(value, str) else value


@router.get("/providers")
def providers():
    return [
        {
            "type": str(p.provider_type),
            "supported_tasks": [task for task in ModelTaskType if p.supports_task(task)],
        }
        for p in register_builtin_providers().all()
    ]


@router.get("/connections")
def connections(db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    from .. import models
    return [connection_service.serialize(x, include_mask=True) for x in db.query(models.ProviderConnection).filter_by(user_id=user.id).all()]


@router.post("/connections", status_code=201)
def create_connection(payload: ConnectionCreate, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return connection_service.serialize(connection_service.create(db, user.id, payload), include_mask=True)


@router.get("/connections/{connection_id}")
def get_connection(connection_id: str, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return connection_service.serialize(connection_service.get_owned(db, user.id, connection_id), include_mask=True)


@router.put("/connections/{connection_id}")
def update_connection(connection_id: str, payload: ConnectionUpdate, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    item = connection_service.get_owned(db, user.id, connection_id)
    return connection_service.serialize(connection_service.update(db, item, payload), include_mask=True)


@router.delete("/connections/{connection_id}", status_code=204)
def delete_connection(connection_id: str, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    item = connection_service.get_owned(db, user.id, connection_id); db.delete(item); db.commit()


@router.post("/connections/{connection_id}/test")
async def test_connection(connection_id: str, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    item = connection_service.require_active(connection_service.get_owned(db, user.id, connection_id))
    provider = register_builtin_providers().get(item.provider)
    try:
        result = await provider.test_connection(item, connection_service.credential(item))
        item.last_test_status, item.last_test_message = "success", result.message
    except AIError as exc:
        item.last_test_status, item.last_test_message = "failed", str(exc)
        raise
    finally:
        item.last_tested_at = datetime.now(timezone.utc); db.commit()
    return result


@router.get("/connections/{connection_id}/models")
def connection_models(connection_id: str, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    connection_service.get_owned(db, user.id, connection_id)
    return model_catalog_service.list_models(db, user.id, connection_id=connection_id, available_only=False)


@router.post("/connections/{connection_id}/models/refresh")
async def refresh_models(connection_id: str, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return await model_catalog_service.refresh(db, user.id, connection_id)


@router.get("/models")
def models(connection_id: str | None = None, provider: ProviderType | None = None, task_type: ModelTaskType | None = None,
    input_modality: Modality | None = None, output_modality: Modality | None = None, available_only: bool = True,
    db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return model_catalog_service.list_models(db, user.id, connection_id=connection_id, provider=provider, task_type=task_type,
        input_modality=input_modality, output_modality=output_modality, available_only=available_only)


@router.get("/models/{model_key:path}")
def model(model_key: str, db: Session = Depends(get_db), user: AuthenticatedUser = Depends(get_current_user)):
    return model_catalog_service.get_model(db, user.id, model_key)
