# backend/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
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

class ChatResponse(BaseModel):
    response: str

class FileUploadResponse(BaseModel):
    message: str

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
