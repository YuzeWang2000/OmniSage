# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, chat, rag, conversation
from app.ai.routers import router as ai_router
from app.ai.errors import AIError
from fastapi.responses import JSONResponse
import logging
from app.config import settings
logger = logging.getLogger(__name__)
# 初始化数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OmniSage", version="1.0.0")
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
app.include_router(ai_router)

@app.exception_handler(AIError)
async def ai_error_handler(_, exc: AIError):
    return JSONResponse(status_code=exc.status_code, content={"error":{"code":exc.code,"message":str(exc)}})


@app.get("/health")
def health_check():
    return {"status": "ok"}


