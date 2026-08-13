from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.database_service import DatabaseService
from app.ai.contracts.messages import NormalizedMessage, TextPart


def test_history_limit_returns_latest_messages_in_chronological_order(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'history.db'}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(models.User(id=1, username="user", hashed_password="x"))
    db.add(models.Conversation(id=1, user_id=1, title="chat"))
    start = datetime.now(timezone.utc)
    for index in range(7):
        db.add(models.ChatMessage(
            conversation_id=1,
            role="user" if index % 2 == 0 else "assistant",
            content_json=[{"type": "text", "text": str(index)}],
            metadata_json={},
            created_at=start + timedelta(seconds=index),
        ))
    db.commit()
    history = DatabaseService.get_chat_history(1, db, limit=5)
    assert [message["content"][0]["text"] for message in history] == ["2", "3", "4", "5", "6"]
    db.close()


def test_provider_context_uses_trusted_history_and_appends_new_turn(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'context.db'}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(models.User(id=1, username="user", hashed_password="x"))
    db.add(models.Conversation(id=1, user_id=1, title="chat"))
    db.add_all([
        models.ChatMessage(conversation_id=1, role="user", content_json=[{"type": "text", "text": "remember 731"}], metadata_json={}),
        models.ChatMessage(conversation_id=1, role="assistant", content_json=[{"type": "text", "text": "remembered"}], metadata_json={}),
    ])
    db.commit()
    incoming = [NormalizedMessage(role="user", content=[TextPart(text="what number?")])]
    context = DatabaseService.build_chat_context(1, incoming, False, db)
    assert [(item.role, item.text()) for item in context] == [
        ("user", "remember 731"), ("assistant", "remembered"), ("user", "what number?"),
    ]
    db.close()


def test_regenerate_context_drops_old_answer_and_duplicate_prompt(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'regenerate.db'}")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(models.User(id=1, username="user", hashed_password="x"))
    db.add(models.Conversation(id=1, user_id=1, title="chat"))
    db.add_all([
        models.ChatMessage(conversation_id=1, role="user", content_json=[{"type": "text", "text": "question"}], metadata_json={}),
        models.ChatMessage(conversation_id=1, role="assistant", content_json=[{"type": "text", "text": "old answer"}], metadata_json={}),
    ])
    db.commit()
    incoming = [NormalizedMessage(role="user", content=[TextPart(text="question")])]
    context = DatabaseService.build_chat_context(1, incoming, True, db)
    assert [(item.role, item.text()) for item in context] == [("user", "question")]
    db.close()
