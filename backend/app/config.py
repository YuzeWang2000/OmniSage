# backend/app/config.py
import os
from typing import Optional

class Settings:
    """应用配置类"""
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://gpt:gpt@localhost/chatdb"
    
    # LLM配置
    DEFAULT_MODEL: str = "gemma3n"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # 在线模型配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "your-api-key")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY", "your-api-key")
    
    # 向量数据库配置
    VECTOR_DB_PATH: str = "./chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploaded_files"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 聊天历史配置
    MAX_HISTORY_LENGTH: int = 10
    
    # 模型温度配置
    DEFAULT_TEMPERATURE: float = 0.7

# 全局配置实例
settings = Settings() 