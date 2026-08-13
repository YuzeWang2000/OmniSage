from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.database_service import DatabaseService


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
