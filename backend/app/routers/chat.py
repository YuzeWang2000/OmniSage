# backend/app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.llm_service import llm_controller
from ..services.database_service import DatabaseService
import json
import asyncio
import time
router = APIRouter(prefix="/chat", tags=["chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/stream")
def chat_stream_endpoint(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    流式聊天接口
    """
    try:
        # 验证对话是否存在且属于该用户
        conversation = DatabaseService.get_conversation_by_id(
            req.conversation_id, 
            req.user_id, 
            db
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话不存在或无权限访问"
            )
        
        # 获取聊天历史
        chat_history = DatabaseService.get_chat_history(req.conversation_id, db)
        
        # 构建LLM控制器需要的payload
        payload = {
            "message": req.message,
            "model": req.model,
            "mode": req.mode,
            "use_rag": req.use_rag,
            "chat_history": chat_history
        }
        stream = req.stream if req.stream is not None else True
        # stream = False
        def generate():
            try:
                # 调用LLM控制器进行流式处理
                full_response = ""
                for chunk in llm_controller.process_message(payload, req.user_id, db):
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
                DatabaseService.save_chat_history(
                    conversation_id=req.conversation_id,
                    message=req.message,
                    response=full_response,
                    model=req.model,
                    db=db
                )
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                error_msg = f"❌ 流式处理失败: {str(e)}"
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        print(f"流式聊天接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"流式聊天处理失败: {str(e)}")
