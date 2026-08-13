# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    conversations = relationship("Conversation", back_populates="user")
    provider_connections = relationship("ProviderConnection", back_populates="user", cascade="all, delete-orphan")
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
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    model_key = Column(String(500))
    content_json = Column(JSON, nullable=False)
    reasoning_summary_json = Column(JSON)
    tool_calls_json = Column(JSON)
    metadata_json = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), index=True)
    conversation = relationship("Conversation", back_populates="messages")

class ProviderConnection(Base):
    __tablename__ = 'provider_connections'
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    provider = Column(String(32), nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    protocol = Column(String(32), nullable=False)
    region = Column(String(50))
    base_url = Column(String(500), nullable=False)
    workspace_id = Column(String(100))
    encrypted_api_key = Column(Text)
    credential_version = Column(Integer, nullable=False, default=1)
    config_json = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    last_tested_at = Column(DateTime)
    last_test_status = Column(String(20))
    last_test_message = Column(String(240))
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    user = relationship("User", back_populates="provider_connections")
    models = relationship("AIModelCache", back_populates="connection", cascade="all, delete-orphan")

class AIModelCache(Base):
    __tablename__ = 'ai_model_cache'
    __table_args__ = (UniqueConstraint('connection_id', 'model_id'),)
    id = Column(Integer, primary_key=True)
    connection_id = Column(String(36), ForeignKey('provider_connections.id', ondelete='CASCADE'), nullable=False, index=True)
    model_id = Column(String(300), nullable=False)
    display_name = Column(String(300), nullable=False)
    task_types_json = Column(JSON, nullable=False)
    input_modalities_json = Column(JSON, nullable=False)
    output_modalities_json = Column(JSON, nullable=False)
    capabilities_json = Column(JSON, nullable=False)
    limits_json = Column(JSON, nullable=False)
    metadata_json = Column(JSON, nullable=False, default=dict)
    source = Column(String(32), nullable=False)
    available = Column(Boolean, nullable=False, default=True)
    fetched_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    connection = relationship("ProviderConnection", back_populates="models")

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
