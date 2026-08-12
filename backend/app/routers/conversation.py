# backend/app/routers/conversation.py
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.database_service import DatabaseService
from ..security import (
    AuthenticatedUser,
    ensure_legacy_user_matches,
    get_current_user,
)
from datetime import datetime

router = APIRouter(prefix="/conversations", tags=["conversations"])
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ConversationResponse)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """创建新对话"""
    try:
        ensure_legacy_user_matches(conversation.user_id, current_user)
        
        # 创建对话
        new_conversation = DatabaseService.create_conversation(
            current_user.id,
            conversation.title, 
            db
        )
        
        if not new_conversation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建对话失败"
            )
        
        return schemas.ConversationResponse(
            id=new_conversation.id,
            user_id=new_conversation.user_id,
            title=new_conversation.title,
            created_at=new_conversation.created_at,
            updated_at=new_conversation.updated_at,
            is_active=new_conversation.is_active,
            message_count=0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("创建对话失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话失败"
        )

@router.get("/user/{user_id}", response_model=schemas.ConversationListResponse)
def get_user_conversations(
    user_id: int,
    limit: int | None = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """获取用户的所有对话"""
    try:
        ensure_legacy_user_matches(user_id, current_user)
        conversations = DatabaseService.get_user_conversations(current_user.id, db)
        if limit is not None:
            conversations = conversations[:limit]
        
        conversation_responses = []
        for conv in conversations:
            # 计算消息数量
            message_count = len(conv.messages)
            
            conversation_responses.append(schemas.ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                is_active=conv.is_active,
                message_count=message_count
            ))
        
        return schemas.ConversationListResponse(conversations=conversation_responses)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取用户对话失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取对话列表失败"
        )

@router.get("/{conversation_id}/messages", response_model=schemas.ChatHistoryResponse)
def get_conversation_messages(
    conversation_id: int,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """获取指定对话的聊天历史"""
    try:
        # 验证对话是否存在且属于该用户
        ensure_legacy_user_matches(user_id, current_user)
        conversation = DatabaseService.get_conversation_by_id(
            conversation_id, current_user.id, db
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在或无权限访问"
            )
        
        # 获取聊天历史
        messages = DatabaseService.get_chat_history(conversation_id, db)
        message_responses = []
        for msg in messages:
            message_responses.append(schemas.ChatMessageResponse(
                role=msg['role'],
                content=msg['content'],
            ))
        
        return schemas.ChatHistoryResponse(
            conversation_id=conversation_id,
            messages=message_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取聊天历史失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取聊天历史失败"
        )


@router.patch("/{conversation_id}")
def rename_conversation(
    conversation_id: int,
    conversation: schemas.ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """重命名属于当前用户的对话。"""
    title = conversation.title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="对话标题不能为空",
        )
    ensure_legacy_user_matches(conversation.user_id, current_user)
    success = DatabaseService.update_conversation_title(
        conversation_id, current_user.id, title[:100], db
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话不存在或无权限修改",
        )
    return {"message": "对话重命名成功", "title": title[:100]}

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """删除对话"""
    try:
        ensure_legacy_user_matches(user_id, current_user)
        success = DatabaseService.delete_conversation(
            conversation_id, current_user.id, db
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在或无权限删除"
            )
        
        return {"message": "对话删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("删除对话失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除对话失败"
        )

