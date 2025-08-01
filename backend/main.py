# backend/app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, chat, rag, conversation, api_keys
from fastapi import APIRouter
import ollama
from app.services.llm_service import online_models
# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChatSystem", version="0.1")

# 注册路由
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(conversation.router)
app.include_router(api_keys.router)

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
    response_list = ollama.list()
    local_models = []
    for m in response_list.models:
        if is_embedding_model(m):
            pass
        else:
            local_models.append(m.model)
    
    online_models_list = online_models.copy()
    print(local_models)
    print(online_models_list)
    return {
        "local_models": local_models,
        "online_models": online_models_list,
        "all_models": local_models + online_models_list  # 保持向后兼容
    }

