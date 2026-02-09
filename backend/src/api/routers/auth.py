from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.services.auth_service import AuthService
from src.infrastructure.persistence.mysql.database import get_db
from src.infrastructure.persistence.mysql.user_repository import MySQLUserRepository
from src.api.schemas.auth import UserCreate, Token, UserResponse
from src.api.dependencies.auth import get_current_user


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """注册新用户"""
    user_repo = MySQLUserRepository(db)

    # 检查用户名是否已存在
    existing = await user_repo.get_by_username(user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # 检查邮箱是否已存在
    existing = await user_repo.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 创建用户
    user = User(
        id=str(uuid4()),
        username=user_data.username,
        email=user_data.email,
        hashed_password=AuthService.hash_password(user_data.password),
    )
    created = await user_repo.create(user)
    return created


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """用户登录"""
    user_repo = MySQLUserRepository(db)
    user = await user_repo.get_by_username(form_data.username)

    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取当前用户信息"""
    return current_user
