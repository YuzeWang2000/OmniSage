# backend/app/routers/api_keys.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import SessionLocal
from ..services.database_service import DatabaseService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ApiKeyResponse)
def create_api_key(api_key: schemas.ApiKeyCreate, db: Session = Depends(get_db)):
    """
    创建API key
    """
    try:
        # 检查用户是否存在
        user = DatabaseService.get_user_by_id(api_key.user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查是否已存在相同provider的API key
        existing_key = DatabaseService.get_user_api_key_by_provider(
            api_key.user_id, api_key.provider, db
        )
        if existing_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"已存在 {api_key.provider} 的API key"
            )
        
        # 创建新的API key
        new_api_key = DatabaseService.create_api_key(
            user_id=api_key.user_id,
            provider=api_key.provider,
            api_key=api_key.api_key,
            model_name=api_key.model_name,
            db=db
        )
        
        return new_api_key
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"创建API key失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建API key失败: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=schemas.ApiKeyListResponse)
def get_user_api_keys(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的所有API key
    """
    try:
        # 检查用户是否存在
        user = DatabaseService.get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 获取用户的API keys
        api_keys = DatabaseService.get_user_api_keys(user_id, db)
        
        return {"api_keys": api_keys}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取API keys失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取API keys失败: {str(e)}"
        )

@router.put("/{api_key_id}", response_model=schemas.ApiKeyResponse)
def update_api_key(
    api_key_id: int, 
    api_key_update: schemas.ApiKeyUpdate, 
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    更新API key
    """
    try:
        # 检查API key是否存在且属于该用户
        api_key = DatabaseService.get_api_key_by_id(api_key_id, user_id, db)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key不存在或无权限访问"
            )
        
        # 更新API key
        updated_api_key = DatabaseService.update_api_key(
            api_key_id=api_key_id,
            api_key=api_key_update.api_key,
            model_name=api_key_update.model_name,
            is_active=api_key_update.is_active,
            db=db
        )
        
        return updated_api_key
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新API key失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新API key失败: {str(e)}"
        )

@router.delete("/{api_key_id}")
def delete_api_key(api_key_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    删除API key
    """
    try:
        # 检查API key是否存在且属于该用户
        api_key = DatabaseService.get_api_key_by_id(api_key_id, user_id, db)
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key不存在或无权限访问"
            )
        
        # 删除API key
        DatabaseService.delete_api_key(api_key_id, db)
        
        return {"message": "API key删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除API key失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除API key失败: {str(e)}"
        ) 