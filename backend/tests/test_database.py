from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models


def test_empty_database_initializes_idempotently(tmp_path):
    engine=create_engine(f"sqlite:///{tmp_path/'test.db'}")
    Base.metadata.create_all(engine); Base.metadata.create_all(engine)
    tables=set(inspect(engine).get_table_names())
    assert {"provider_connections","ai_model_cache","chat_messages"} <= tables

