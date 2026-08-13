from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.ai.contracts.models import ProviderType
from app.ai.errors import ConnectionNotFoundError, ConnectionUnavailableError, ProviderUnavailableError
from app.ai.services import connection_service, model_catalog_service
from app.ai.routers import ConnectionCreate
from app.database import Base


@pytest.fixture
def db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'services.db'}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        models.User(id=1, username="one", hashed_password="x"),
        models.User(id=2, username="two", hashed_password="x"),
    ])
    session.commit()
    try:
        yield session
    finally:
        session.close()


def add_connection(db, connection_id="connection-1", user_id=1, active=True):
    item = models.ProviderConnection(
        id=connection_id,
        user_id=user_id,
        provider=ProviderType.DEEPSEEK.value,
        display_name=connection_id,
        protocol="openai_compatible",
        base_url="https://api.deepseek.com",
        encrypted_api_key="opaque",
        config_json={},
        is_active=active,
    )
    db.add(item)
    db.commit()
    return item


def add_cache(db, connection_id="connection-1", model_id="same", expired=False):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.add(models.AIModelCache(
        connection_id=connection_id,
        model_id=model_id,
        display_name=model_id,
        task_types_json=["chat"],
        input_modalities_json=["text"],
        output_modalities_json=["text"],
        capabilities_json={"streaming": True},
        limits_json={},
        metadata_json={},
        source="provider_api",
        available=True,
        fetched_at=now,
        expires_at=now - timedelta(seconds=1) if expired else now + timedelta(hours=1),
    ))
    db.commit()


def test_connection_and_model_catalog_are_user_isolated(db):
    add_connection(db)
    add_cache(db)
    with pytest.raises(ConnectionNotFoundError):
        connection_service.get_owned(db, 2, "connection-1")
    assert model_catalog_service.list_models(db, 2) == []
    assert [item.id for item in model_catalog_service.list_models(db, 1)] == ["same"]


def test_inactive_connection_is_not_callable_or_available(db):
    connection = add_connection(db, active=False)
    add_cache(db)
    with pytest.raises(ConnectionUnavailableError):
        connection_service.require_active(connection)
    assert model_catalog_service.list_models(db, 1, available_only=True) == []
    assert len(model_catalog_service.list_models(db, 1, available_only=False)) == 1


def test_credential_update_rotates_without_echoing_plaintext(db, monkeypatch):
    connection = add_connection(db)
    connection.encrypted_api_key = None
    connection.credential_version = 1
    monkeypatch.setattr(connection_service.settings, "CREDENTIAL_ENCRYPTION_KEY", "test-root-key")
    payload = SimpleNamespace(
        model_dump=lambda **_: {"api_key": "sk-new-secret"}
    )
    updated = connection_service.update(db, connection, payload)
    assert updated.credential_version == 2
    assert "sk-new-secret" not in updated.encrypted_api_key
    response = connection_service.serialize(updated, include_mask=True)
    assert "api_key" not in response
    assert response["masked_credential"] == "sk-••••ret"


def test_connection_create_schema_trims_deepseek_fields():
    payload = ConnectionCreate.model_validate({
        "provider": "deepseek",
        "display_name": "  DeepSeek  ",
        "api_key": "  sk-valid-deepseek-key  ",
        "manual_models": [" live-model ", "live-model"],
    })
    assert payload.display_name == "DeepSeek"
    assert payload.api_key == "sk-valid-deepseek-key"
    assert payload.manual_models == ["live-model"]


def test_runtime_connection_snapshot_survives_commit_and_detach(db):
    connection = add_connection(db)
    connection.region = "cn-beijing"
    connection.config_json = {"manual_models": ["qwen-plus"]}
    snapshot = connection_service.runtime_snapshot(connection)
    db.commit()
    db.expunge(connection)
    assert snapshot.id == "connection-1"
    assert snapshot.base_url == "https://api.deepseek.com"
    assert snapshot.config_json == {"manual_models": ["qwen-plus"]}


def test_online_connections_can_be_created_and_never_echo_key(db, monkeypatch):
    monkeypatch.setattr(connection_service.settings, "CREDENTIAL_ENCRYPTION_KEY", "local-test-root-key")
    deepseek = ConnectionCreate.model_validate({
        "provider": "deepseek", "display_name": "DeepSeek", "api_key": "sk-deepseek-example",
    })
    dashscope = ConnectionCreate.model_validate({
        "provider": "dashscope", "display_name": "百炼", "region": "cn-beijing",
        "api_key": "sk-dashscope-example",
    })
    for payload in (deepseek, dashscope):
        item = connection_service.create(db, 1, payload)
        response = connection_service.serialize(item, include_mask=True)
        assert response["has_credential"] is True
        assert "api_key" not in response
        assert payload.api_key not in str(response)


@pytest.mark.asyncio
async def test_refresh_failure_returns_only_same_connection_stale_cache(db, monkeypatch):
    first = add_connection(db, "connection-1")
    add_connection(db, "connection-2")
    add_cache(db, "connection-1", "first")
    add_cache(db, "connection-2", "second")

    class FailingProvider:
        async def list_models(self, *_):
            raise ProviderUnavailableError("controlled failure")

    registry = SimpleNamespace(get=lambda _: FailingProvider())
    monkeypatch.setattr(model_catalog_service, "register_builtin_providers", lambda: registry)
    monkeypatch.setattr(model_catalog_service, "credential", lambda _: "secret")
    result = await model_catalog_service.refresh(db, 1, first.id)
    assert [(item.id, item.stale) for item in result] == [("first", True)]
