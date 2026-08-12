# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, chat, rag, conversation, api_keys
import ollama
import logging
from app.config import settings
from app.services.llm_service import online_models

ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL)
logger = logging.getLogger(__name__)
# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatSystem", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(conversation.router)
app.include_router(api_keys.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

def is_embedding_model(model_obj):
    # 1. 名称包含 embed
    if "embed" in model_obj.model.lower():
        return True
    # 2. family 或 families 包含 embed
    if hasattr(model_obj.details, "family") and "embed" in model_obj.details.family.lower():
        return True
    if hasattr(model_obj.details, "families"):
        if any("embed" in fam.lower() for fam in model_obj.details.families):
            return True
    # 3. 其他可扩展规则
    return False

@app.get("/models")
def get_models():
    """
    返回可用模型列表，分为本地模型和在线模型
    """
    local_models = []
    ollama_error = None

    try:
        response_list = ollama_client.list()
        for model in response_list.models:
            if not is_embedding_model(model):
                local_models.append(model.model)
    except Exception as exc:
        # 在线模型不依赖 Ollama。Ollama 暂时不可用时仍应返回在线模型，
        # 避免前端把整个模型列表错误地显示为空。
        ollama_error = "Ollama 服务暂不可用"
        logger.warning("获取 Ollama 模型列表失败: %s", type(exc).__name__)
    
    online_models_list = online_models.copy()
    return {
        "local_models": local_models,
        "online_models": online_models_list,
        "all_models": local_models + online_models_list,  # 保持向后兼容
        "ollama_available": ollama_error is None,
        "ollama_error": ollama_error,
    }

