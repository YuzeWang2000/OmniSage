# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str

class ChatRequest(BaseModel):
    user_id: int
    conversation_id: int
    message: str
    model: str
    mode: str = "chat"
    use_rag: bool = False
    use_wiki: bool = False  # 添加Wiki知识支持
    stream: bool = True
    # Chain相关参数
    chain_type: str = "stuff"
    prompt_name: str = "chat_default"
    use_reranker: bool = True
    top_k: int = 5
    score_threshold: float = 0.5

class ChatResponse(BaseModel):
    response: str

class FileUploadResponse(BaseModel):
    message: str
    chunks: Optional[int] = 0

class ConversationCreate(BaseModel):
    user_id: int
    title: str

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    message_count: int = 0

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]

class ChatMessageResponse(BaseModel):
    role: str
    content: str

class ChatHistoryResponse(BaseModel):
    conversation_id: int
    messages: List[ChatMessageResponse]

# API Key相关schemas
class ApiKeyCreate(BaseModel):
    user_id: int
    provider: str  # 'openai', 'deepseek', 'anthropic', etc.
    api_key: str
    model_name: Optional[str] = None

class ApiKeyResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    model_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ApiKeyListResponse(BaseModel):
    api_keys: List[ApiKeyResponse]

class ApiKeyUpdate(BaseModel):
    api_key: str
    model_name: Optional[str] = None
    is_active: bool = True

# 知识库相关schemas
class KnowledgeBaseCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    embedding_model: str = "nomic-embed-text"

class KnowledgeBaseResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    embedding_model: str
    vector_db_path: Optional[str]
    file_count: int
    document_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class KnowledgeBaseListResponse(BaseModel):
    knowledge_bases: List[KnowledgeBaseResponse]

class KnowledgeFileResponse(BaseModel):
    id: int
    knowledge_base_id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: Optional[str]
    document_count: int
    is_processed: bool
    created_at: datetime
    updated_at: datetime

class KnowledgeFileListResponse(BaseModel):
    files: List[KnowledgeFileResponse]
    total: int

class KnowledgeBaseStats(BaseModel):
    total_knowledge_bases: int
    total_files: int
    total_documents: int
    active_knowledge_bases: int


