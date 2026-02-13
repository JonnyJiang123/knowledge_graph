from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """用户注册请求"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class Token(BaseModel):
    """JWT令牌响应"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True
