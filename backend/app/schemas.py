# backend/app/schemas.py
from pydantic import BaseModel, Field, field_validator
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

class AuthResponse(UserResponse):
    access_token: str
    token_type: str = "bearer"

from .ai.contracts.requests import NormalizedChatRequest as ChatRequest

class ChatResponse(BaseModel):
    response: str

class FileUploadResponse(BaseModel):
    message: str
    chunks: Optional[int] = 0

class ConversationCreate(BaseModel):
    user_id: Optional[int] = None
    title: str

class ConversationUpdate(BaseModel):
    user_id: Optional[int] = None
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
    content: List[Dict[str, Any]]
    model_key: Optional[str] = None

class ConversationMessagesResponse(BaseModel):
    conversation_id: int
    messages: List[ChatMessageResponse]

# 知识库相关schemas
class KnowledgeBaseCreate(BaseModel):
    user_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    embedding_model: str = Field(default="nomic-embed-text", min_length=1, max_length=200)

    @field_validator("name", "embedding_model", mode="before")
    @classmethod
    def normalize_required_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_text(cls, value):
        if not isinstance(value, str):
            return value
        value = value.strip()
        return value or None

class KnowledgeBaseUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        if not isinstance(value, str):
            return value
        value = value.strip()
        return value or None

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

class KnowledgeBaseSearchResult(BaseModel):
    content: str
    score: float
    source: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None

class KnowledgeBaseSearchResponse(BaseModel):
    query: str
    knowledge_base_id: int
    knowledge_base_name: str
    threshold: Optional[float] = None
    results: List[KnowledgeBaseSearchResult]


class WikiSearchResult(BaseModel):
    title: str
    content: str
    url: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    score: float = 0
    source: str


class WikiSearchResponse(BaseModel):
    query: str
    mode: str
    results: List[WikiSearchResult]


