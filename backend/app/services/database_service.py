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
            conversation = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == user_id,
                models.Conversation.is_active == True
            ).first()
            return conversation
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
                conversation.updated_at = datetime.now()
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
            user = db.query(models.User).filter(models.User.username == username).first()
            return user
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    
    @staticmethod
    def create_user(username: str, hashed_password: str, db: Session) -> Optional[models.User]:
        """创建新用户"""
        try:
            user = models.User(
                username=username,
                hashed_password=hashed_password
            )
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
            user = db.query(models.User).filter(models.User.id == user_id).first()
            return user
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    
    @staticmethod
    def create_api_key(user_id: int, provider: str, api_key: str, model_name: str = None, db: Session = None) -> Optional[models.UserApiKey]:
        """创建API密钥"""
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
            print(f"创建API密钥失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_user_api_keys(user_id: int, db: Session) -> List[models.UserApiKey]:
        """获取用户的所有API密钥"""
        try:
            api_keys = db.query(models.UserApiKey).filter(
                models.UserApiKey.user_id == user_id,
                models.UserApiKey.is_active == True
            ).order_by(models.UserApiKey.created_at.desc()).all()
            return api_keys
        except Exception as e:
            print(f"获取用户API密钥失败: {str(e)}")
            return []
    
    @staticmethod
    def get_user_api_key_by_provider(user_id: int, provider: str, db: Session) -> Optional[models.UserApiKey]:
        """根据提供商获取用户的API密钥"""
        try:
            api_key = db.query(models.UserApiKey).filter(
                models.UserApiKey.user_id == user_id,
                models.UserApiKey.provider == provider,
                models.UserApiKey.is_active == True
            ).first()
            return api_key
        except Exception as e:
            print(f"获取用户API密钥失败: {str(e)}")
            return None
    
    @staticmethod
    def get_api_key_by_id(api_key_id: int, user_id: int, db: Session) -> Optional[models.UserApiKey]:
        """根据ID获取API密钥（确保属于指定用户）"""
        try:
            api_key = db.query(models.UserApiKey).filter(
                models.UserApiKey.id == api_key_id,
                models.UserApiKey.user_id == user_id
            ).first()
            return api_key
        except Exception as e:
            print(f"获取API密钥失败: {str(e)}")
            return None
    
    @staticmethod
    def update_api_key(api_key_id: int, api_key: str, model_name: str = None, is_active: bool = True, db: Session = None) -> Optional[models.UserApiKey]:
        """更新API密钥"""
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
            print(f"更新API密钥失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def delete_api_key(api_key_id: int, db: Session) -> bool:
        """删除API密钥"""
        try:
            api_key = db.query(models.UserApiKey).filter(
                models.UserApiKey.id == api_key_id
            ).first()
            
            if api_key:
                db.delete(api_key)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"删除API密钥失败: {str(e)}")
            db.rollback()
            return False

    # 知识库相关方法
    @staticmethod
    def create_knowledge_base(user_id: int, name: str, description: str = None, 
                            embedding_model: str = "nomic-embed-text", vector_db_path: str = None, 
                            db: Session = None) -> Optional[models.KnowledgeBase]:
        """创建知识库"""
        try:
            knowledge_base = models.KnowledgeBase(
                user_id=user_id,
                name=name,
                description=description,
                embedding_model=embedding_model,
                vector_db_path=vector_db_path,
                file_count=0,
                document_count=0,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(knowledge_base)
            db.commit()
            db.refresh(knowledge_base)
            return knowledge_base
        except Exception as e:
            print(f"创建知识库失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_knowledge_base_by_id(knowledge_base_id: int, user_id: int, db: Session) -> Optional[models.KnowledgeBase]:
        """根据ID获取知识库（确保属于指定用户）"""
        try:
            knowledge_base = db.query(models.KnowledgeBase).filter(
                models.KnowledgeBase.id == knowledge_base_id,
                models.KnowledgeBase.user_id == user_id,
                models.KnowledgeBase.is_active == True
            ).first()
            return knowledge_base
        except Exception as e:
            print(f"获取知识库失败: {str(e)}")
            return None
    
    @staticmethod
    def get_knowledge_base_by_name(user_id: int, name: str, db: Session) -> Optional[models.KnowledgeBase]:
        """根据名称获取知识库（确保属于指定用户）"""
        try:
            knowledge_base = db.query(models.KnowledgeBase).filter(
                models.KnowledgeBase.user_id == user_id,
                models.KnowledgeBase.name == name,
                models.KnowledgeBase.is_active == True
            ).first()
            return knowledge_base
        except Exception as e:
            print(f"获取知识库失败: {str(e)}")
            return None
    
    @staticmethod
    def get_user_knowledge_bases(user_id: int, db: Session) -> List[models.KnowledgeBase]:
        """获取用户的所有知识库"""
        try:
            print(f"正在查询用户 {user_id} 的知识库...")
            knowledge_bases = db.query(models.KnowledgeBase).filter(
                models.KnowledgeBase.user_id == user_id,
                models.KnowledgeBase.is_active == True
            ).order_by(models.KnowledgeBase.updated_at.desc()).all()
            print(f"查询到 {len(knowledge_bases)} 个知识库")
            return knowledge_bases
        except Exception as e:
            print(f"获取用户知识库失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def get_user_active_knowledge_bases(user_id: int, db: Session) -> List[models.KnowledgeBase]:
        """获取用户的所有活跃知识库"""
        try:
            knowledge_bases = db.query(models.KnowledgeBase).filter(
                models.KnowledgeBase.user_id == user_id,
                models.KnowledgeBase.is_active == True
            ).all()
            return knowledge_bases
        except Exception as e:
            print(f"获取用户活跃知识库失败: {str(e)}")
            return []
    
    @staticmethod
    def delete_knowledge_base(knowledge_base_id: int, user_id: int, db: Session) -> bool:
        """删除知识库（软删除）"""
        try:
            knowledge_base = db.query(models.KnowledgeBase).filter(
                models.KnowledgeBase.id == knowledge_base_id,
                models.KnowledgeBase.user_id == user_id
            ).first()
            
            if knowledge_base:
                knowledge_base.is_active = False
                knowledge_base.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"删除知识库失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def create_knowledge_file(knowledge_base_id: int, filename: str, original_filename: str,
                            file_path: str, file_size: int, file_type: str, document_count: int,
                            is_processed: bool = True, db: Session = None) -> Optional[models.KnowledgeFile]:
        """创建知识库文件记录"""
        try:
            knowledge_file = models.KnowledgeFile(
                knowledge_base_id=knowledge_base_id,
                filename=filename,
                original_filename=original_filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                document_count=document_count,
                is_processed=is_processed,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(knowledge_file)
            db.commit()
            db.refresh(knowledge_file)
            return knowledge_file
        except Exception as e:
            print(f"创建知识库文件记录失败: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_knowledge_file_by_id(file_id: int, knowledge_base_id: int, user_id: int, db: Session) -> Optional[models.KnowledgeFile]:
        """根据ID获取知识库文件（确保属于指定知识库和用户）"""
        try:
            knowledge_file = db.query(models.KnowledgeFile).join(models.KnowledgeBase).filter(
                models.KnowledgeFile.id == file_id,
                models.KnowledgeFile.knowledge_base_id == knowledge_base_id,
                models.KnowledgeBase.user_id == user_id
            ).first()
            return knowledge_file
        except Exception as e:
            print(f"获取知识库文件失败: {str(e)}")
            return None
    
    @staticmethod
    def get_knowledge_base_files(knowledge_base_id: int, user_id: int, db: Session) -> List[models.KnowledgeFile]:
        """获取知识库的文件列表（确保属于指定用户）"""
        try:
            files = db.query(models.KnowledgeFile).join(models.KnowledgeBase).filter(
                models.KnowledgeFile.knowledge_base_id == knowledge_base_id,
                models.KnowledgeBase.user_id == user_id
            ).order_by(models.KnowledgeFile.created_at.desc()).all()
            return files
        except Exception as e:
            print(f"获取知识库文件列表失败: {str(e)}")
            return []
    
    @staticmethod
    def delete_knowledge_file(file_id: int, knowledge_base_id: int, user_id: int, db: Session) -> bool:
        """删除知识库文件"""
        try:
            knowledge_file = db.query(models.KnowledgeFile).join(models.KnowledgeBase).filter(
                models.KnowledgeFile.id == file_id,
                models.KnowledgeFile.knowledge_base_id == knowledge_base_id,
                models.KnowledgeBase.user_id == user_id
            ).first()
            
            if knowledge_file:
                db.delete(knowledge_file)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"删除知识库文件失败: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def update_knowledge_base_stats(knowledge_base_id: int, db: Session) -> bool:
        """更新知识库统计信息"""
        try:
            # 获取知识库
            knowledge_base = db.query(models.KnowledgeBase).filter(
                models.KnowledgeBase.id == knowledge_base_id
            ).first()
            
            if knowledge_base:
                # 统计文件数量和文档数量
                files = db.query(models.KnowledgeFile).filter(
                    models.KnowledgeFile.knowledge_base_id == knowledge_base_id
                ).all()
                
                file_count = len(files)
                document_count = sum(file.document_count for file in files)
                
                # 更新统计信息
                knowledge_base.file_count = file_count
                knowledge_base.document_count = document_count
                knowledge_base.updated_at = datetime.now()
                
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"更新知识库统计信息失败: {str(e)}")
            db.rollback()
            return False 