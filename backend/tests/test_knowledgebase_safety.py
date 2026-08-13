from io import BytesIO
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.knowledgebase_service import KnowledgeBaseService
from langchain_core.documents import Document


class Upload:
    filename = "note.txt"
    size = 5
    file = BytesIO(b"hello")


def make_db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'knowledge.db'}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(models.User(id=1, username="user", hashed_password="x"))
    db.commit()
    return db


def service_at(tmp_path):
    service = KnowledgeBaseService.__new__(KnowledgeBaseService)
    service.base_upload_dir = str((tmp_path / "uploads").resolve())
    service.base_vector_dir = str((tmp_path / "vectors").resolve())
    Path(service.base_upload_dir).mkdir()
    Path(service.base_vector_dir).mkdir()
    service.rag_chain_service = None
    return service


def test_malicious_display_name_never_controls_storage_path(tmp_path):
    db = make_db(tmp_path)
    service = service_at(tmp_path)
    result = service.create_knowledge_base(1, "../../../../escape", db=db)
    assert result["success"] is True
    kb = db.get(models.KnowledgeBase, result["knowledge_base_id"])
    vector_path = Path(kb.vector_db_path).resolve()
    assert vector_path.is_relative_to(Path(service.base_vector_dir))
    assert vector_path.name == f"kb_{kb.id}"
    assert "escape" not in str(vector_path)
    db.close()


def test_upload_vector_failure_rolls_back_sql_and_file(tmp_path, monkeypatch):
    db = make_db(tmp_path)
    service = service_at(tmp_path)
    created = service.create_knowledge_base(1, "safe", db=db)
    kb_id = created["knowledge_base_id"]
    monkeypatch.setattr(service, "_process_document", lambda *_: [type("Doc", (), {"metadata": {}})()])
    monkeypatch.setattr(service, "_add_documents_to_vectorstore", lambda *_: False)
    result = service.upload_file_to_knowledge_base(kb_id, 1, Upload(), db)
    assert result["success"] is False
    assert db.query(models.KnowledgeFile).count() == 0
    assert list(service._upload_dir(1, kb_id).iterdir()) == []
    db.close()


def test_stored_path_outside_root_is_rejected(tmp_path):
    service = service_at(tmp_path)
    outside = tmp_path.parent / "outside"
    try:
        service._validated_stored_path(service.base_upload_dir, str(outside))
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe stored path was accepted")


def test_rename_updates_metadata_without_moving_vector_path(tmp_path):
    db = make_db(tmp_path)
    service = service_at(tmp_path)
    created = service.create_knowledge_base(1, "old name", description="old", db=db)
    kb_id = created["knowledge_base_id"]
    original_path = db.get(models.KnowledgeBase, kb_id).vector_db_path
    result = service.update_knowledge_base(kb_id, 1, "new name", "new", db)
    assert result["success"] is True
    updated = db.get(models.KnowledgeBase, kb_id)
    assert (updated.name, updated.description) == ("new name", "new")
    assert updated.vector_db_path == original_path
    db.close()


def test_rename_rejects_another_active_knowledge_base_name(tmp_path):
    db = make_db(tmp_path)
    service = service_at(tmp_path)
    first = service.create_knowledge_base(1, "first", db=db)["knowledge_base_id"]
    service.create_knowledge_base(1, "second", db=db)
    result = service.update_knowledge_base(first, 1, "second", None, db)
    assert result == {"success": False, "status": 409, "message": "知识库名称 'second' 已存在"}
    assert db.get(models.KnowledgeBase, first).name == "first"
    db.close()


def test_vector_writes_are_batched_and_metadata_is_sanitized(tmp_path, monkeypatch):
    service = service_at(tmp_path)
    calls = []

    class FakeChroma:
        def __init__(self, **_kwargs):
            pass

        def add_documents(self, documents, ids):
            calls.append((documents, ids))

    monkeypatch.setattr("app.services.knowledgebase_service.Chroma", FakeChroma)
    monkeypatch.setattr("app.services.knowledgebase_service.settings.VECTOR_WRITE_BATCH_SIZE", 2)
    documents = [
        Document(page_content=str(index), metadata={"page": index, "nested": {"bad": True}, "empty": None})
        for index in range(5)
    ]
    assert service._add_documents_to_vectorstore(documents, str(tmp_path / "vectors"), "model", 7)
    assert [len(batch) for batch, _ids in calls] == [2, 2, 1]
    assert calls[-1][1] == ["file-7-chunk-4"]
    assert all(document.metadata == {"page": index} for index, document in enumerate(documents))
