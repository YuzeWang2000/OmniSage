# backend/app/config.py
import os
import secrets
from typing import Optional

from . import environment as _environment  # noqa: F401

class Settings:
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./omnisage.db",
    )
    OLLAMA_BASE_URL: str = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        )
    
    # LLM配置
    EMBEDDING_MODEL: str = os.getenv(
            "EMBEDDING_MODEL",
            "nomic-embed-text",
        )
    
    # 在线模型配置
    CREDENTIAL_ENCRYPTION_KEY: Optional[str] = os.getenv("CREDENTIAL_ENCRYPTION_KEY")
    MODEL_CACHE_TTL_SECONDS: int = int(os.getenv("MODEL_CACHE_TTL_SECONDS", "3600"))
    APP_ENV: str = os.getenv("APP_ENV", "development").strip().lower()
    
    
    # 向量数据库配置
    DATA_DIR: str = os.getenv("DATA_DIR", ".")
    VECTOR_DB_PATH: str = os.path.join(DATA_DIR, "chroma_db")
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 128
    
    # 文件上传配置
    UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploaded_files")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 聊天历史配置
    MAX_HISTORY_LENGTH: int = 5
    
    # 模型温度配置
    DEFAULT_TEMPERATURE: float = 0.7

    # 鉴权配置。未配置时生成仅适用于单进程本地开发的临时密钥。
    JWT_SECRET_KEY: str = (
        os.getenv("JWT_SECRET_KEY")
        or os.getenv("SECRET_KEY")  # 兼容旧版部署变量
        or secrets.token_urlsafe(48)
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    # 独立知识库搜索的动态相关性过滤参数。
    SEARCH_MIN_SCORE: float = float(os.getenv("SEARCH_MIN_SCORE", "0.35"))
    SEARCH_SCORE_MARGIN: float = float(os.getenv("SEARCH_SCORE_MARGIN", "0.18"))
    SEARCH_CANDIDATE_MULTIPLIER: int = int(
        os.getenv("SEARCH_CANDIDATE_MULTIPLIER", "3")
    )

    CORS_ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173",
        ).split(",")
        if origin.strip()
    ]

# 全局配置实例
settings = Settings()
