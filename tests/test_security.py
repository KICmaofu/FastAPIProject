"""安全工具单元测试"""
import pytest
from app.utils.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.config.settings import settings

def test_password_hashing():
    """测试密码哈希和验证"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed is not None
    assert len(hashed) > 0
    
    # 验证正确密码
    assert verify_password(password, hashed) is True
    
    # 验证错误密码
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation():
    """测试JWT令牌创建"""
    user_id = "12345"
    token = create_access_token(data={"sub": user_id})
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_jwt_token_decoding():
    """测试JWT令牌解码"""
    user_id = "12345"
    token = create_access_token(data={"sub": user_id})
    
    decoded_user_id = decode_access_token(token)
    
    assert decoded_user_id == user_id

def test_jwt_token_expiry():
    """测试JWT令牌过期"""
    from datetime import timedelta
    
    user_id = "12345"
    # 创建一个立即过期的令牌
    token = create_access_token(data={"sub": user_id}, expires_delta=timedelta(seconds=-1))
    
    decoded_user_id = decode_access_token(token)
    
    assert decoded_user_id is None

def test_invalid_jwt_token():
    """测试无效JWT令牌"""
    invalid_token = "invalid.token.string"
    result = decode_access_token(invalid_token)
    
    assert result is None