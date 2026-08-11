# backend/app/config.py
import os
from typing import Optional

class Settings:
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://gpt:1234@localhost:3306/chatdb",
    )
    OLLAMA_BASE_URL: str = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        )
    
    # LLM配置
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemma3n")
    EMBEDDING_MODEL: str = os.getenv(
            "EMBEDDING_MODEL",
            "nomic-embed-text",
        )
    
    # 在线模型配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    
    
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

    # 鉴权配置。生产环境必须通过环境变量覆盖默认密钥。
    JWT_SECRET_KEY: str = (
        os.getenv("JWT_SECRET_KEY")
        or os.getenv("SECRET_KEY")  # 兼容旧版部署变量
        or "omnisage-dev-secret-change-before-production"
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

# 全局配置实例
settings = Settings()
