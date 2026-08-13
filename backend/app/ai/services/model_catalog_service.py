from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ... import models
from ...config import settings
from ..contracts.models import ModelDescriptor, ProviderType, make_model_key
from ..errors import ModelNotFoundError
from ..providers import register_builtin_providers
from .connection_service import credential, get_owned, require_active


def _descriptor(connection, row, stale=False):
    return ModelDescriptor(
        key=make_model_key(connection.provider, connection.id, row.model_id), connection_id=connection.id,
        provider=ProviderType(connection.provider), id=row.model_id, display_name=row.display_name, source=row.source,
        available=row.available, task_types=row.task_types_json, input_modalities=row.input_modalities_json,
        output_modalities=row.output_modalities_json, capabilities=row.capabilities_json, limits=row.limits_json,
        metadata=row.metadata_json or {}, fetched_at=row.fetched_at.replace(tzinfo=timezone.utc) if row.fetched_at.tzinfo is None else row.fetched_at,
        stale=stale or row.expires_at < datetime.now(timezone.utc).replace(tzinfo=None),
    )


def cached(db, connection, stale=False):
    return [_descriptor(connection, row, stale) for row in db.query(models.AIModelCache).filter_by(connection_id=connection.id).all()]


async def refresh(db: Session, user_id: int, connection_id: str):
    connection = require_active(get_owned(db, user_id, connection_id))
    provider = register_builtin_providers().get(connection.provider)
    try:
        discovered = await provider.list_models(connection, credential(connection))
    except Exception:
        old = cached(db, connection, stale=True)
        if old: return old
        raise
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.query(models.AIModelCache).filter_by(connection_id=connection.id).delete()
    for model in discovered:
        db.add(models.AIModelCache(
            connection_id=connection.id, model_id=model.id, display_name=model.display_name,
            task_types_json=[x.value for x in model.task_types], input_modalities_json=[x.value for x in model.input_modalities],
            output_modalities_json=[x.value for x in model.output_modalities], capabilities_json=model.capabilities.model_dump(),
            limits_json=model.limits.model_dump(), metadata_json=model.metadata, source=model.source, available=model.available,
            fetched_at=now, expires_at=now + timedelta(seconds=settings.MODEL_CACHE_TTL_SECONDS),
        ))
    db.commit(); return cached(db, connection)


def list_models(db, user_id, **filters):
    query = db.query(models.AIModelCache, models.ProviderConnection).join(models.ProviderConnection).filter(models.ProviderConnection.user_id == user_id)
    if filters.get("connection_id"): query = query.filter(models.AIModelCache.connection_id == filters["connection_id"])
    if filters.get("provider"): query = query.filter(models.ProviderConnection.provider == filters["provider"])
    if filters.get("available_only", True): query = query.filter(models.ProviderConnection.is_active.is_(True))
    result = [_descriptor(c, row) for row, c in query.all()]
    if filters.get("task_type"): result = [m for m in result if filters["task_type"] in m.task_types]
    if filters.get("input_modality"): result = [m for m in result if filters["input_modality"] in m.input_modalities]
    if filters.get("output_modality"): result = [m for m in result if filters["output_modality"] in m.output_modalities]
    if filters.get("available_only", True): result = [m for m in result if m.available]
    return result


def get_model(db, user_id, key):
    for item in list_models(db, user_id, available_only=False):
        if item.key == key: return item
    raise ModelNotFoundError("model not found")
