# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./omnisage.db")
SQL_ECHO = os.getenv("SQL_ECHO", "false").strip().lower() in {"1", "true", "yes", "on"}
CONNECT_ARGS = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
    future=True,
    connect_args=CONNECT_ARGS,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
