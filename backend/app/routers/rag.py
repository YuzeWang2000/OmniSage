# backend/app/routers/rag.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.llm_service import llm_controller
from ..services.database_service import DatabaseService
from ..config import settings
import os

router = APIRouter(prefix="/rag", tags=["rag"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ChatResponse)
def rag_endpoint(req: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    RAG接口 - 使用向量数据库进行检索增强生成
    """
    try:
        # 获取聊天历史
        chat_history = DatabaseService.get_chat_history(req.user_id, db)
        # 构建LLM控制器需要的payload（强制启用RAG）
        payload = {
            "message": req.message,
            "model": req.model,
            "use_rag": True,  # RAG接口强制启用RAG
            "chat_history": chat_history
        }
        
        # 调用LLM控制器处理消息
        response = llm_controller.process_message(payload)
        
        # 保存聊天历史到数据库
        DatabaseService.save_chat_history(
            user_id=req.user_id,
            message=req.message,
            response=response,
            model=req.model,
            db=db
        )
        
        return {"response": response}
        
    except Exception as e:
        print(f"RAG接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG处理失败: {str(e)}")

@router.post("/upload", response_model=schemas.FileUploadResponse)
def upload_file(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    文件上传接口 - 接收文件并进行向量化处理
    """
    try:
        # 检查文件大小
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024}MB)"
            )
        
        # 保存文件
        save_dir = settings.UPLOAD_DIR
        os.makedirs(save_dir, exist_ok=True)
        
        # 提取实际的文件名（去除路径）
        original_filename = file.filename
        if original_filename and '/' in original_filename:
            actual_filename = os.path.basename(original_filename)
        else:
            actual_filename = original_filename
        
        file_path = os.path.join(save_dir, actual_filename)
        
        # 保存文件到本地
        try:
            with open(file_path, "wb") as f:
                import shutil
                shutil.copyfileobj(file.file, f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
        
        # 获取文件类型
        file_extension = actual_filename.split('.')[-1].lower() if '.' in actual_filename else 'txt'
        
        # 使用LLM控制器处理文档
        try:
            documents = llm_controller.process_document(file_path, file_extension)
            if not documents:
                raise ValueError("文档处理失败: 未能提取有效内容")
                
            success = llm_controller.add_documents_to_vectorstore(documents)
            if not success:
                raise ValueError("向量化处理失败")
                
            return {
                "message": f"文件 {original_filename} 上传成功并已向量化",
                "chunks": len(documents)
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    finally:
        # 统一在finally块中清理文件
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"文件清理失败: {str(e)}")
