# backend/app/services/database_service.py
from sqlalchemy.orm import Session
from .. import models
from typing import List, Dict, Optional
from datetime import datetime
from ..config import settings

class DatabaseService:
    """数据库服务类，处理所有数据库操作"""
    
    @staticmethod
    def get_chat_history(conversation_id: int, db: Session, limit: int = None) -> List[Dict]:
        """获取指定对话的聊天历史"""
        if limit is None:
            limit = settings.MAX_HISTORY_LENGTH
            
        try:
            history = db.query(models.ChatHistory).filter(
                models.ChatHistory.conversation_id == conversation_id
            ).order_by(models.ChatHistory.timestamp.asc()).limit(limit).all()
            
            # 转换为标准格式
            chat_history = []
            for chat in history:  # 按时间顺序
                chat_history.append({
                    "role": "user",
                    "content": chat.message
                })
                chat_history.append({
                    "role": "assistant", 
                    "content": chat.response
                })
            
            return chat_history
        except Exception as e:
            print(f"获取聊天历史失败: {str(e)}")
            return []
    
    @staticmethod
    def save_chat_history(conversation_id: int, message: str, response: str, model: str, db: Session) -> bool:
        """保存聊天历史"""
        try:
            chat = models.ChatHistory(
                conversation_id=conversation_id,
                message=message,
                response=response,
                model=model,
                timestamp=datetime.now()
            )
            db.add(chat)
            
            # 更新对话的最后更新时间
            conversation = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id
            ).first()
            if conversation:
                conversation.updated_at = datetime.now()
            
            db.commit()
            return True
        except Exception as e:
            print(f"保存聊天历史失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def create_conversation(user_id: int, title: str, db: Session) -> Optional[models.Conversation]:
        """创建新对话"""
        try:
            conversation = models.Conversation(
                user_id=user_id,
                title=title,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except Exception as e:
            print(f"创建对话失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_user_conversations(user_id: int, db: Session) -> List[models.Conversation]:
        """获取用户的所有对话"""
        try:
            conversations = db.query(models.Conversation).filter(
                models.Conversation.user_id == user_id,
                models.Conversation.is_active == True
            ).order_by(models.Conversation.updated_at.desc()).all()
            return conversations
        except Exception as e:
            print(f"获取用户对话失败: {str(e)}")
            return []
    
    @staticmethod
    def get_conversation_by_id(conversation_id: int, user_id: int, db: Session) -> Optional[models.Conversation]:
        """根据ID获取对话（确保属于指定用户）"""
        try:
            return db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user_id,
                models.Conversation.is_active == True
            ).first()
        except Exception as e:
            print(f"获取对话失败: {str(e)}")
            return None
    
    @staticmethod
    def delete_conversation(conversation_id: int, user_id: int, db: Session) -> bool:
        """删除对话（软删除）"""
        try:
            conversation = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user_id
            ).first()
            if conversation:
                conversation.is_active = False
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"删除对话失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def update_conversation_title(conversation_id: int, user_id: int, title: str, db: Session) -> bool:
        """更新对话标题"""
        try:
            conversation = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user_id
            ).first()
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"更新对话标题失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def get_user_by_username(username: str, db: Session) -> Optional[models.User]:
        """根据用户名获取用户"""
        try:
            return db.query(models.User).filter(models.User.username == username).first()
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    
    @staticmethod
    def create_user(username: str, hashed_password: str, db: Session) -> Optional[models.User]:
        """创建新用户"""
        try:
            user = models.User(username=username, hashed_password=hashed_password)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> Optional[models.User]:
        """根据ID获取用户"""
        try:
            return db.query(models.User).filter(models.User.id == user_id).first()
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None

    # API Key相关方法
    @staticmethod
    def create_api_key(user_id: int, provider: str, api_key: str, model_name: str = None, db: Session = None) -> Optional[models.UserApiKey]:
        """创建API key"""
        try:
            api_key_obj = models.UserApiKey(
                user_id=user_id,
                provider=provider,
                api_key=api_key,
                model_name=model_name,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(api_key_obj)
            db.commit()
            db.refresh(api_key_obj)
            return api_key_obj
        except Exception as e:
            print(f"创建API key失败: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def get_user_api_keys(user_id: int, db: Session) -> List[models.UserApiKey]:
        """获取用户的所有API keys"""
        try:
            return db.query(models.UserApiKey).filter(
                models.UserApiKey.user_id == user_id
            ).order_by(models.UserApiKey.created_at.desc()).all()
        except Exception as e:
            print(f"获取用户API keys失败: {str(e)}")
            return []

    @staticmethod
    def get_user_api_key_by_provider(user_id: int, provider: str, db: Session) -> Optional[models.UserApiKey]:
        """根据provider获取用户的API key"""
        try:
            return db.query(models.UserApiKey).filter(
                models.UserApiKey.user_id == user_id,
                models.UserApiKey.provider == provider
            ).first()
        except Exception as e:
            print(f"获取用户API key失败: {str(e)}")
            return None

    @staticmethod
    def get_api_key_by_id(api_key_id: int, user_id: int, db: Session) -> Optional[models.UserApiKey]:
        """根据ID获取API key（确保属于指定用户）"""
        try:
            return db.query(models.UserApiKey).filter(
                models.UserApiKey.id == api_key_id,
                models.UserApiKey.user_id == user_id
            ).first()
        except Exception as e:
            print(f"获取API key失败: {str(e)}")
            return None

    @staticmethod
    def update_api_key(api_key_id: int, api_key: str, model_name: str = None, is_active: bool = True, db: Session = None) -> Optional[models.UserApiKey]:
        """更新API key"""
        try:
            api_key_obj = db.query(models.UserApiKey).filter(
                models.UserApiKey.id == api_key_id
            ).first()
            
            if api_key_obj:
                api_key_obj.api_key = api_key
                if model_name is not None:
                    api_key_obj.model_name = model_name
                api_key_obj.is_active = is_active
                api_key_obj.updated_at = datetime.now()
                
                db.commit()
                db.refresh(api_key_obj)
                return api_key_obj
            return None
        except Exception as e:
            print(f"更新API key失败: {str(e)}")
            db.rollback()
            return None

    @staticmethod
    def delete_api_key(api_key_id: int, db: Session) -> bool:
        """删除API key"""
        try:
            api_key_obj = db.query(models.UserApiKey).filter(
                models.UserApiKey.id == api_key_id
            ).first()
            
            if api_key_obj:
                db.delete(api_key_obj)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"删除API key失败: {str(e)}")
            db.rollback()
            return False 