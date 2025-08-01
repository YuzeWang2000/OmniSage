# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    conversations = relationship("Conversation", back_populates="user")
    api_keys = relationship("UserApiKey", back_populates="user")
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)  # 对话标题
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    is_active = Column(Boolean, default=True)  # 是否活跃
    
    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatHistory", back_populates="conversation", cascade="all, delete-orphan")

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)  # 关联到对话
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    message = Column(Text, nullable=False)   # 用户输入
    response = Column(Text, nullable=False)  # 模型回复
    model = Column(String(50))               # 模型标识，如 'gpt-3.5-turbo' 或 'llama3'
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")

class UserApiKey(Base):
    __tablename__ = 'user_api_keys'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    provider = Column(String(50), nullable=False)  # 服务提供商，如 'openai', 'anthropic', 'google'
    api_key = Column(String(500), nullable=False)  # API密钥
    model_name = Column(String(100))               # 模型名称，如 'gpt-4', 'claude-3'
    is_active = Column(Boolean, default=True)      # 是否启用
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    # 关系
    user = relationship("User", back_populates="api_keys")

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_bases'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)  # 知识库名称
    description = Column(Text)  # 知识库描述
    embedding_model = Column(String(50), default="nomic-embed-text")  # 嵌入模型
    vector_db_path = Column(String(255))  # 向量数据库路径
    file_count = Column(Integer, default=0)  # 文件数量
    document_count = Column(Integer, default=0)  # 文档块数量
    is_active = Column(Boolean, default=True)  # 是否活跃
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    # 关系
    user = relationship("User", back_populates="knowledge_bases")
    files = relationship("KnowledgeFile", back_populates="knowledge_base", cascade="all, delete-orphan")

class KnowledgeFile(Base):
    __tablename__ = 'knowledge_files'
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey('knowledge_bases.id'), nullable=False)
    filename = Column(String(255), nullable=False)  # 文件名
    original_filename = Column(String(255), nullable=False)  # 原始文件名
    file_path = Column(String(500), nullable=False)  # 文件路径
    file_size = Column(Integer, default=0)  # 文件大小
    file_type = Column(String(20))  # 文件类型
    document_count = Column(Integer, default=0)  # 文档块数量
    is_processed = Column(Boolean, default=False)  # 是否已处理
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    
    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="files")
