# backend/app/routers/rag.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.knowledgebase_service import knowledge_base_service
from ..services.database_service import DatabaseService
from ..services.wiki_service import WikiService, WikiKnowledgeBase
from ..config import settings
import os

router = APIRouter(prefix="/rag", tags=["rag"])

# 初始化Wiki服务（默认使用自动模式）
try:
    wiki_service = WikiService(mode="auto")  # 使用自动模式
    wiki_kb = WikiKnowledgeBase(wiki_service)
    
    # 检查服务状态
    stats = wiki_service.get_database_stats()
    if stats["service_type"] == "online":
        print("✅ 使用在线维基百科服务")
    elif stats["service_type"] == "offline":
        print("✅ 使用离线维基百科服务")
    elif stats["service_type"] == "offline_unavailable":
        print("⚠️ 离线模式不可用，使用在线模式")
    else:
        print("⚠️ 服务状态异常，将回退到在线模式")
        
except Exception as e:
    print(f"❌ Wiki服务初始化失败: {str(e)}")
    wiki_kb = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 知识库管理接口
@router.post("/knowledge-bases", response_model=schemas.KnowledgeBaseResponse)
def create_knowledge_base(knowledge_base: schemas.KnowledgeBaseCreate, db: Session = Depends(get_db)):
    """
    创建知识库
    """
    try:
        result = knowledge_base_service.create_knowledge_base(
            user_id=knowledge_base.user_id,
            name=knowledge_base.name,
            description=knowledge_base.description,
            embedding_model=knowledge_base.embedding_model,
            db=db
        )
        
        if result["success"]:
            # 获取创建的知识库信息
            kb = DatabaseService.get_knowledge_base_by_id(result["knowledge_base_id"], knowledge_base.user_id, db)
            return schemas.KnowledgeBaseResponse(
                id=kb.id,
                user_id=kb.user_id,
                name=kb.name,
                description=kb.description,
                embedding_model=kb.embedding_model,
                vector_db_path=kb.vector_db_path,
                file_count=kb.file_count,
                document_count=kb.document_count,
                is_active=kb.is_active,
                created_at=kb.created_at,
                updated_at=kb.updated_at
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库失败: {str(e)}"
        )

@router.get("/knowledge-bases/{user_id}", response_model=schemas.KnowledgeBaseListResponse)
def get_user_knowledge_bases(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的知识库列表
    """
    try:
        print(f"正在获取用户 {user_id} 的知识库列表...")
        knowledge_bases = knowledge_base_service.get_user_knowledge_bases(user_id, db)
        print(f"获取到 {len(knowledge_bases)} 个知识库")
        
        kb_responses = []
        for kb in knowledge_bases:
            try:
                kb_response = schemas.KnowledgeBaseResponse(
                    id=kb["id"],
                    user_id=kb["user_id"],
                    name=kb["name"],
                    description=kb["description"],
                    embedding_model=kb["embedding_model"],
                    vector_db_path=kb["vector_db_path"],
                    file_count=kb["file_count"],
                    document_count=kb["document_count"],
                    is_active=kb["is_active"],
                    created_at=kb["created_at"],
                    updated_at=kb["updated_at"]
                )
                kb_responses.append(kb_response)
            except Exception as kb_error:
                print(f"处理知识库数据时出错: {kb_error}")
                print(f"知识库数据: {kb}")
                continue
        
        return schemas.KnowledgeBaseListResponse(knowledge_bases=kb_responses)
    except Exception as e:
        print(f"获取知识库列表时出现异常: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取知识库列表失败: {str(e)}"
        )

@router.delete("/knowledge-bases/{knowledge_base_id}")
def delete_knowledge_base(knowledge_base_id: int, user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """
    删除知识库
    """
    try:
        result = knowledge_base_service.delete_knowledge_base(knowledge_base_id, user_id, db)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识库失败: {str(e)}"
        )

# 文件管理接口
@router.post("/knowledge-bases/{knowledge_base_id}/files", response_model=schemas.FileUploadResponse)
def upload_file_to_knowledge_base(knowledge_base_id: int, user_id: int = Query(..., description="用户ID"), file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    上传文件到指定知识库
    """
    try:
        result = knowledge_base_service.upload_file_to_knowledge_base(knowledge_base_id, user_id, file, db)
        
        if result["success"]:
            return schemas.FileUploadResponse(
                message=result["message"],
                chunks=result["chunks"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.get("/knowledge-bases/{knowledge_base_id}/files", response_model=schemas.KnowledgeFileListResponse)
def get_knowledge_base_files(knowledge_base_id: int, user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """
    获取知识库的文件列表
    """
    try:
        files = knowledge_base_service.get_knowledge_base_files(knowledge_base_id, user_id, db)
        file_responses = []
        for file_info in files:
            file_responses.append(schemas.KnowledgeFileResponse(
                id=file_info["id"],
                knowledge_base_id=knowledge_base_id,
                filename=file_info["filename"],
                original_filename=file_info["original_filename"],
                file_path=file_info["file_path"],
                file_size=file_info["file_size"],
                file_type=file_info["file_type"],
                document_count=file_info["document_count"],
                is_processed=file_info["is_processed"],
                created_at=file_info["created_at"],
                updated_at=file_info["updated_at"]
            ))
        
        return schemas.KnowledgeFileListResponse(files=file_responses, total=len(file_responses))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件列表失败: {str(e)}"
        )

@router.delete("/knowledge-bases/{knowledge_base_id}/files/{file_id}")
def delete_file_from_knowledge_base(knowledge_base_id: int, file_id: int, user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """
    从知识库中删除文件
    """
    try:
        result = knowledge_base_service.delete_file_from_knowledge_base(file_id, knowledge_base_id, user_id, db)
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        )

# 统计信息接口
@router.get("/stats/{user_id}", response_model=schemas.KnowledgeBaseStats)
def get_user_knowledge_base_stats(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的知识库统计信息
    """
    try:
        knowledge_bases = knowledge_base_service.get_user_knowledge_bases(user_id, db)
        
        total_knowledge_bases = len(knowledge_bases)
        total_files = sum(kb["file_count"] for kb in knowledge_bases)
        total_documents = sum(kb["document_count"] for kb in knowledge_bases)
        active_knowledge_bases = sum(1 for kb in knowledge_bases if kb["is_active"])
        
        return schemas.KnowledgeBaseStats(
            total_knowledge_bases=total_knowledge_bases,
            total_files=total_files,
            total_documents=total_documents,
            active_knowledge_bases=active_knowledge_bases
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )

# Wiki知识搜索接口

@router.get("/enhance-context-with-wiki")
def enhance_context_with_wiki(
    query: str = Query(..., description="查询内容"),
    existing_context: str = Query("", description="现有上下文"),
    db: Session = Depends(get_db)
):
    """
    使用Wiki知识增强上下文
    """
    try:
        enhanced_context = wiki_kb.get_enhanced_context(query, existing_context)
        return {
            "success": True,
            "query": query,
            "enhanced_context": enhanced_context,
            "has_wiki_content": "=== 维基百科补充信息 ===" in enhanced_context
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"增强上下文失败: {str(e)}"
        )

# Wiki数据管理接口
@router.get("/wiki/status")
def get_wiki_status(db: Session = Depends(get_db)):
    """
    获取Wiki数据状态
    """
    try:
        if wiki_kb and hasattr(wiki_kb, 'wiki_service'):
            stats = wiki_kb.wiki_service.get_database_stats()
            return {
                "success": True,
                "mode": wiki_kb.wiki_service.mode,
                "stats": stats["stats"]
            }
        else:
            return {
                "success": False,
                "mode": "unavailable",
                "stats": {}
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取Wiki状态失败: {str(e)}"
        )

@router.post("/wiki/switch-mode")
def switch_wiki_mode(mode: str = Query(..., description="目标模式: online 或 offline"), db: Session = Depends(get_db)):
    """
    切换Wiki服务模式
    """
    try:
        if not wiki_kb or not hasattr(wiki_kb, 'wiki_service'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Wiki服务不可用"
            )
        
        success = wiki_kb.wiki_service.switch_mode(mode)
        if success:
            stats = wiki_kb.wiki_service.get_database_stats()
            return {
                "success": True,
                "message": f"成功切换到{mode}模式",
                "mode": wiki_kb.wiki_service.mode,
                "stats": stats["stats"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"切换到{mode}模式失败"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换Wiki模式失败: {str(e)}"
        )


def process_wiki_data(db: Session = Depends(get_db)):
    """
    处理维基百科数据
    """
    try:
        if wiki_kb and hasattr(wiki_kb, 'wiki_service'):
            # 提取文章
            if not wiki_kb.wiki_service.extract_wiki_articles():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="维基百科文章提取失败"
                )
            
            # 处理文章
            if not wiki_kb.wiki_service.process_extracted_articles():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="维基百科文章处理失败"
                )
            
            # 获取统计信息
            stats = wiki_kb.wiki_service.get_database_stats()
            
            return {
                "success": True,
                "message": "维基百科数据处理完成",
                "stats": stats["stats"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Wiki服务不可用"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理维基百科数据失败: {str(e)}"
        )

