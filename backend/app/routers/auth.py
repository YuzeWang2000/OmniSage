# backend/app/routers/auth.py
"""
register, login, me
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt
from .. import schemas
from ..database import SessionLocal
from ..services.database_service import DatabaseService
from ..security import AuthenticatedUser, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    """
    验证密码是否正确
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (TypeError, ValueError):
        return False

def get_password_hash(password):
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度不能超过 72 个 UTF-8 字节",
        )
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    try:
        # 检查用户是否已存在
        existing_user = DatabaseService.get_user_by_username(user.username, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user.password)
        new_user = DatabaseService.create_user(user.username, hashed_password, db)
        
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户创建失败"
            )
        
        return {"user_id": new_user.id, "username": new_user.username}
        
    except HTTPException:
        raise
    except Exception:
        logger.error("注册失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败"
        )

@router.post("/login", response_model=schemas.AuthResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口
    """
    try:
        # 获取用户
        db_user = DatabaseService.get_user_by_username(user.username, db)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": db_user.id,
            "username": db_user.username,
            "access_token": create_access_token(db_user.id, db_user.username),
            "token_type": "bearer",
        }
        
    except HTTPException:
        raise
    except Exception:
        logger.error("登录失败")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.get("/me", response_model=schemas.UserResponse)
def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """返回 Bearer Token 对应的当前用户，用于客户端恢复登录状态。"""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
    }
