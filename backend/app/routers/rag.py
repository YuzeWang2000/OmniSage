# backend/app/routers/rag.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.knowledgebase_service import knowledge_base_service
from ..services.database_service import DatabaseService
from ..config import settings
from ..security import (
    AuthenticatedUser,
    ensure_legacy_user_matches,
    get_current_user,
)
import os
import logging

router = APIRouter(prefix="/rag", tags=["rag"])
logger = logging.getLogger(__name__)

def get_wiki_knowledge_base():
    """复用聊天 RAG 链的 Wiki 实例，确保模式切换对问答和搜索同时生效。"""
    return knowledge_base_service.rag_chain_service.get_wiki_knowledge_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 知识库管理接口
@router.post("/knowledge-bases", response_model=schemas.KnowledgeBaseResponse)
def create_knowledge_base(
    knowledge_base: schemas.KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    创建知识库
    """
    try:
        ensure_legacy_user_matches(knowledge_base.user_id, current_user)
        result = knowledge_base_service.create_knowledge_base(
            user_id=current_user.id,
            name=knowledge_base.name,
            description=knowledge_base.description,
            embedding_model=knowledge_base.embedding_model,
            db=db
        )
        
        if result["success"]:
            # 获取创建的知识库信息
            kb = DatabaseService.get_knowledge_base_by_id(
                result["knowledge_base_id"], current_user.id, db
            )
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
    except Exception:
        logger.error("创建知识库失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建知识库失败"
        )

@router.get("/knowledge-bases/{user_id}", response_model=schemas.KnowledgeBaseListResponse)
def get_user_knowledge_bases(
    user_id: int,
    limit: int | None = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    获取用户的知识库列表
    """
    try:
        ensure_legacy_user_matches(user_id, current_user)
        knowledge_bases = knowledge_base_service.get_user_knowledge_bases(
            current_user.id, db
        )
        if limit is not None:
            knowledge_bases = knowledge_bases[:limit]
        
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
            except Exception:
                logger.error("知识库响应序列化失败")
                continue
        
        return schemas.KnowledgeBaseListResponse(knowledge_bases=kb_responses)
    except HTTPException:
        raise
    except Exception:
        logger.error("获取知识库列表失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取知识库列表失败"
        )

@router.delete("/knowledge-bases/{knowledge_base_id}")
def delete_knowledge_base(
    knowledge_base_id: int,
    user_id: int | None = Query(None, description="兼容字段：用户ID"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    删除知识库
    """
    try:
        ensure_legacy_user_matches(user_id, current_user)
        result = knowledge_base_service.delete_knowledge_base(
            knowledge_base_id, current_user.id, db
        )
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception:
        logger.error("删除知识库失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除知识库失败"
        )

# 文件管理接口
@router.post("/knowledge-bases/{knowledge_base_id}/files", response_model=schemas.FileUploadResponse)
def upload_file_to_knowledge_base(
    knowledge_base_id: int,
    file: UploadFile = File(...),
    user_id: int | None = Query(None, description="兼容字段：用户ID"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    上传文件到指定知识库
    """
    try:
        ensure_legacy_user_matches(user_id, current_user)
        result = knowledge_base_service.upload_file_to_knowledge_base(
            knowledge_base_id, current_user.id, file, db
        )
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
    except Exception:
        logger.error("文件上传失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件上传失败"
        )

@router.get("/knowledge-bases/{knowledge_base_id}/files", response_model=schemas.KnowledgeFileListResponse)
def get_knowledge_base_files(
    knowledge_base_id: int,
    user_id: int | None = Query(None, description="兼容字段：用户ID"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    获取知识库的文件列表
    """
    try:
        ensure_legacy_user_matches(user_id, current_user)
        knowledge_base = DatabaseService.get_knowledge_base_by_id(
            knowledge_base_id, current_user.id, db
        )
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识库不存在或无权访问",
            )
        files = knowledge_base_service.get_knowledge_base_files(
            knowledge_base_id, current_user.id, db
        )
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
    except HTTPException:
        raise
    except Exception:
        logger.error("获取文件列表失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取文件列表失败"
        )


@router.get(
    "/knowledge-bases/{knowledge_base_id}/search",
    response_model=schemas.KnowledgeBaseSearchResponse,
)
def search_knowledge_base(
    knowledge_base_id: int,
    user_id: int | None = Query(None, description="兼容字段：用户ID"),
    query: str = Query(..., min_length=1, description="查询内容"),
    top_k: int = Query(5, ge=1, le=20, description="返回结果数量"),
    min_score: float | None = Query(None, ge=0, le=1, description="最低相关度"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """使用已有向量检索能力搜索用户指定的知识库。"""
    ensure_legacy_user_matches(user_id, current_user)
    knowledge_base = DatabaseService.get_knowledge_base_by_id(
        knowledge_base_id, current_user.id, db
    )
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在或无权访问",
        )
    if not knowledge_base.vector_db_path or not os.path.exists(knowledge_base.vector_db_path):
        return {
            "query": query,
            "knowledge_base_id": knowledge_base_id,
            "knowledge_base_name": knowledge_base.name,
            "threshold": None,
            "results": [],
        }

    try:
        search_response = knowledge_base_service.search_knowledge_base(
            query,
            knowledge_base.vector_db_path,
            knowledge_base.embedding_model,
            top_k,
            min_score,
        )
    except RuntimeError:
        logger.warning("知识库检索暂时失败")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="知识库检索暂时失败",
        )
    return {
        "query": query,
        "knowledge_base_id": knowledge_base_id,
        "knowledge_base_name": knowledge_base.name,
        "threshold": search_response["threshold"],
        "results": search_response["results"],
    }

@router.delete("/knowledge-bases/{knowledge_base_id}/files/{file_id}")
def delete_file_from_knowledge_base(
    knowledge_base_id: int,
    file_id: int,
    user_id: int | None = Query(None, description="兼容字段：用户ID"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    从知识库中删除文件
    """
    try:
        ensure_legacy_user_matches(user_id, current_user)
        result = knowledge_base_service.delete_file_from_knowledge_base(
            file_id, knowledge_base_id, current_user.id, db
        )
        if result["success"]:
            return {"message": result["message"]}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except HTTPException:
        raise
    except Exception:
        logger.error("删除文件失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除文件失败"
        )

# 统计信息接口
@router.get("/stats/{user_id}", response_model=schemas.KnowledgeBaseStats)
def get_user_knowledge_base_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    获取用户的知识库统计信息
    """
    try:
        ensure_legacy_user_matches(user_id, current_user)
        knowledge_bases = knowledge_base_service.get_user_knowledge_bases(
            current_user.id, db
        )
        
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
    except HTTPException:
        raise
    except Exception:
        logger.error("获取知识库统计失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )

# Wiki知识搜索接口

@router.get("/enhance-context-with-wiki")
def enhance_context_with_wiki(
    query: str = Query(..., description="查询内容"),
    existing_context: str = Query("", description="现有上下文"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    使用Wiki知识增强上下文
    """
    try:
        current_wiki_kb = get_wiki_knowledge_base()
        if current_wiki_kb is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Wiki 服务暂不可用",
            )
        enhanced_context = current_wiki_kb.get_enhanced_context(
            query, existing_context
        )
        return {
            "success": True,
            "query": query,
            "enhanced_context": enhanced_context,
            "has_wiki_content": "=== 维基百科补充信息 ===" in enhanced_context
        }
    except HTTPException:
        raise
    except Exception:
        logger.error("Wiki 上下文增强失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="增强上下文失败"
        )


@router.get("/wiki/search", response_model=schemas.WikiSearchResponse)
def search_wiki(
    query: str = Query(..., min_length=1, description="查询内容"),
    limit: int = Query(5, ge=1, le=10, description="返回结果数量"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """使用当前 Wiki 模式返回可用于引用展示的结构化结果。"""
    current_wiki_kb = get_wiki_knowledge_base()
    if current_wiki_kb is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Wiki 服务暂不可用",
        )
    try:
        results = current_wiki_kb.search_knowledge(query, limit=limit)
        return {
            "query": query,
            "mode": current_wiki_kb.wiki_service.mode,
            "results": results,
        }
    except Exception:
        logger.error("Wiki 结构化搜索失败")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Wiki 搜索暂时失败",
        )

# Wiki数据管理接口
@router.get("/wiki/status")
def get_wiki_status(
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    获取Wiki数据状态
    """
    try:
        current_wiki_kb = get_wiki_knowledge_base()
        if current_wiki_kb and hasattr(current_wiki_kb, 'wiki_service'):
            stats = current_wiki_kb.wiki_service.get_database_stats()
            return {
                "success": True,
                "mode": current_wiki_kb.wiki_service.mode,
                "stats": stats["stats"]
            }
        else:
            return {
                "success": False,
                "mode": "unavailable",
                "stats": {}
            }
    except Exception:
        logger.error("获取 Wiki 状态失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取 Wiki 状态失败"
        )

@router.post("/wiki/switch-mode")
def switch_wiki_mode(
    mode: str = Query(..., description="目标模式: online 或 offline"),
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    切换Wiki服务模式
    """
    try:
        current_wiki_kb = get_wiki_knowledge_base()
        if not current_wiki_kb or not hasattr(current_wiki_kb, 'wiki_service'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Wiki服务不可用"
            )
        
        success = current_wiki_kb.wiki_service.switch_mode(mode)
        if success:
            stats = current_wiki_kb.wiki_service.get_database_stats()
            return {
                "success": True,
                "message": f"成功切换到{mode}模式",
                "mode": current_wiki_kb.wiki_service.mode,
                "stats": stats["stats"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"切换到{mode}模式失败"
            )
    except HTTPException:
        raise
    except Exception:
        logger.error("切换 Wiki 模式失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="切换 Wiki 模式失败"
        )


def process_wiki_data(db: Session = Depends(get_db)):
    """
    处理维基百科数据
    """
    try:
        current_wiki_kb = get_wiki_knowledge_base()
        if current_wiki_kb and hasattr(current_wiki_kb, 'wiki_service'):
            # 提取文章
            if not current_wiki_kb.wiki_service.extract_wiki_articles():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="维基百科文章提取失败"
                )
            
            # 处理文章
            if not current_wiki_kb.wiki_service.process_extracted_articles():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="维基百科文章处理失败"
                )
            
            # 获取统计信息
            stats = current_wiki_kb.wiki_service.get_database_stats()
            
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
    except Exception:
        logger.error("处理 Wiki 数据失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理 Wiki 数据失败"
        )

