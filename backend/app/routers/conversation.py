# backend/app/routers/conversation.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.database_service import DatabaseService
from datetime import datetime

router = APIRouter(prefix="/conversations", tags=["conversations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ConversationResponse)
def create_conversation(conversation: schemas.ConversationCreate, db: Session = Depends(get_db)):
    """创建新对话"""
    try:
        # 验证用户是否存在
        user = DatabaseService.get_user_by_id(conversation.user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 创建对话
        new_conversation = DatabaseService.create_conversation(
            conversation.user_id, 
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
        print(f"创建对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话失败"
        )

@router.get("/user/{user_id}", response_model=schemas.ConversationListResponse)
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """获取用户的所有对话"""
    try:
        conversations = DatabaseService.get_user_conversations(user_id, db)
        
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
        
    except Exception as e:
        print(f"获取用户对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取对话列表失败"
        )

@router.get("/{conversation_id}/messages", response_model=schemas.ChatHistoryResponse)
def get_conversation_messages(conversation_id: int, user_id: int, db: Session = Depends(get_db)):
    """获取指定对话的聊天历史"""
    try:
        # 验证对话是否存在且属于该用户
        conversation = DatabaseService.get_conversation_by_id(conversation_id, user_id, db)
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
        print(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取聊天历史失败"
        )

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, user_id: int, db: Session = Depends(get_db)):
    """删除对话"""
    try:
        success = DatabaseService.delete_conversation(conversation_id, user_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在或无权限删除"
            )
        
        return {"message": "对话删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除对话失败"
        )

