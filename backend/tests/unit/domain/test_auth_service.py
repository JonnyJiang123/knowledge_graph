import pytest
from datetime import timedelta
from src.domain.services.auth_service import AuthService


def test_hash_and_verify_password():
    """测试密码哈希和验证"""
    password = "mysecretpassword"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    """测试创建和解码JWT令牌"""
    user_id = "user-123"
    token = AuthService.create_access_token(user_id)

    decoded_id = AuthService.decode_access_token(token)
    assert decoded_id == user_id


def test_decode_invalid_token():
    """测试解码无效令牌"""
    decoded = AuthService.decode_access_token("invalid.token.here")
    assert decoded is None


def test_token_expiration():
    """测试令牌过期"""
    user_id = "user-123"
    # 创建立即过期的令牌（负数时间差）
    token = AuthService.create_access_token(user_id, expires_delta=timedelta(seconds=-1))

    decoded = AuthService.decode_access_token(token)
    assert decoded is None  # 过期令牌应返回 None
