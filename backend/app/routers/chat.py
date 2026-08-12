# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.llm_service import llm_controller
from ..services.database_service import DatabaseService
from ..security import (
    AuthenticatedUser,
    ensure_legacy_user_matches,
    get_current_user,
)
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/stream")
def chat_stream_endpoint(
    req: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    流式聊天接口
    """
    try:
        ensure_legacy_user_matches(req.user_id, current_user)
        # 验证对话是否存在且属于令牌对应用户
        conversation = DatabaseService.get_conversation_by_id(
            req.conversation_id,
            current_user.id,
            db
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在或无权限访问"
            )
        if req.use_rag and req.knowledge_base_id is not None and not req.use_wiki:
            knowledge_base = DatabaseService.get_knowledge_base_by_id(
                req.knowledge_base_id,
                current_user.id,
                db,
            )
            if not knowledge_base:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="知识库不存在或无权限访问",
                )
        
        # 获取聊天历史
        chat_history = DatabaseService.get_chat_history(req.conversation_id, db)
        if req.regenerate:
            if (
                len(chat_history) < 2
                or chat_history[-2].get("role") != "user"
                or chat_history[-2].get("content") != req.message
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="只能重新生成最近一轮回答",
                )
            chat_history = chat_history[:-2]
        # 新建对话在首条消息发送时自动使用消息前十个字符命名。
        if not chat_history and conversation.title == "新对话":
            auto_title = req.message.strip()[:10] or "新对话"
            DatabaseService.update_conversation_title(
                req.conversation_id, current_user.id, auto_title, db
            )
        # 构建LLM控制器需要的payload
        payload = {
            "message": req.message,
            "model": req.model,
            "mode": req.mode,
            "use_rag": req.use_rag,
            "use_wiki": req.use_wiki,  # 添加Wiki支持
            "knowledge_base_id": req.knowledge_base_id,
            "chat_history": chat_history,
            # Chain相关参数
            "chain_type": getattr(req, 'chain_type', 'stuff'),
            # "prompt_name": getattr(req, 'prompt_name', 'chat_default'),
            "use_reranker": getattr(req, 'use_reranker', True),
            "top_k": getattr(req, 'top_k', 5),
            "score_threshold": getattr(req, 'score_threshold', 0.5)
        }
        stream = req.stream if req.stream is not None else True
        # stream = False
        def generate():
            try:
                # 调用LLM控制器进行流式处理
                full_response = ""
                for chunk in llm_controller.process_message(payload, current_user.id, db):
                    if chunk.lstrip().startswith("❌"):
                        raise RuntimeError("LLM generation failed")
                    if chunk.startswith('<think>'):
                        chunk = chunk.replace('<think>', '='*20 + ' AI思考中🤔 ' )
                    if chunk.endswith('</think>'):
                        chunk = chunk.replace('</think>', '='*20 + ' AI思考结束')
                    # print(f"经过处理后的LLM返回的chunk: {chunk}")
                    full_response += chunk
                    if stream:
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                if not stream:
                    yield f"data: {json.dumps({'chunk': full_response})}\n\n"
                # 保存聊天历史到数据库
                if req.regenerate:
                    saved = DatabaseService.replace_latest_chat_response(
                        conversation_id=req.conversation_id,
                        message=req.message,
                        response=full_response,
                        model=req.model,
                        db=db,
                    )
                else:
                    saved = DatabaseService.save_chat_history(
                        conversation_id=req.conversation_id,
                        message=req.message,
                        response=full_response,
                        model=req.model,
                        db=db,
                    )
                if not saved:
                    raise RuntimeError("Chat history persistence failed")
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except GeneratorExit:
                raise
            except Exception:
                logger.error("聊天流式处理失败")
                yield f"data: {json.dumps({'error': '回答生成失败，请稍后重试'})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
        
    except HTTPException:
        raise
    except Exception:
        logger.error("聊天接口初始化失败")
        raise HTTPException(status_code=500, detail="流式聊天处理失败")
