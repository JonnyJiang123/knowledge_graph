from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from src.config import settings


class AuthService:
    """认证服务 - 处理密码哈希和JWT令牌"""

    @staticmethod
    def hash_password(password: str) -> str:
        """对密码进行哈希处理"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码是否匹配"""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT访问令牌"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode = {
            "sub": user_id,
            "exp": expire,
        }
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def decode_access_token(token: str) -> Optional[str]:
        """解码JWT令牌，返回用户ID"""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
