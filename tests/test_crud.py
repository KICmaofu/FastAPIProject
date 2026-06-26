"""CRUD基础操作单元测试"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base
from app.crud.base import CRUDBase
from app.models.user import User

# 创建测试数据库
TEST_DATABASE_URL = "sqlite:///./test_db.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_crud():
    """创建用户CRUD实例"""
    return CRUDBase(User)

def test_create_user(db, user_crud):
    """测试创建用户"""
    user_data = {
        "username": "testuser",
        "phone": "13800138000",
        "password_hash": "hashed_password",
        "role": "viewer",
        "status": True
    }
    
    user = user_crud.create(db, obj_in=user_data)
    
    assert user is not None
    assert user.username == "testuser"
    assert user.phone == "13800138000"
    assert user.role == "viewer"
    assert user.id is not None

def test_get_user(db, user_crud):
    """测试获取用户"""
    user_data = {
        "username": "gettest",
        "phone": "13800138001",
        "password_hash": "hashed_password",
        "role": "viewer",
        "status": True
    }
    
    created_user = user_crud.create(db, obj_in=user_data)
    fetched_user = user_crud.get(db, id=created_user.id)
    
    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.username == "gettest"

def test_get_multi_users(db, user_crud):
    """测试获取多个用户"""
    # 创建多个用户
    for i in range(5):
        user_data = {
            "username": f"multitest{i}",
            "phone": f"138001380{i+10}",
            "password_hash": "hashed_password",
            "role": "viewer",
            "status": True
        }
        user_crud.create(db, obj_in=user_data)
    
    users = user_crud.get_multi(db, skip=0, limit=10)
    
    assert len(users) >= 5

def test_update_user(db, user_crud):
    """测试更新用户"""
    user_data = {
        "username": "updatetest",
        "phone": "13800138020",
        "password_hash": "hashed_password",
        "role": "viewer",
        "status": True
    }
    
    user = user_crud.create(db, obj_in=user_data)
    updated_user = user_crud.update(db, db_obj=user, obj_in={"username": "updatedname"})
    
    assert updated_user.username == "updatedname"
    assert updated_user.phone == "13800138020"

def test_delete_user(db, user_crud):
    """测试删除用户"""
    user_data = {
        "username": "deletetest",
        "phone": "13800138030",
        "password_hash": "hashed_password",
        "role": "viewer",
        "status": True
    }
    
    user = user_crud.create(db, obj_in=user_data)
    user_id = user.id
    
    deleted_user = user_crud.remove(db, id=user_id)
    
    assert deleted_user.id == user_id
    
    # 验证用户已删除
    fetched_user = user_crud.get(db, id=user_id)
    assert fetched_user is None

def test_user_exists(db, user_crud):
    """测试检查用户是否存在"""
    user_data = {
        "username": "existtest",
        "phone": "13800138040",
        "password_hash": "hashed_password",
        "role": "viewer",
        "status": True
    }
    
    user_crud.create(db, obj_in=user_data)
    
    exists = user_crud.exists(db, username="existtest")
    assert exists is True
    
    not_exists = user_crud.exists(db, username="nonexistent")
    assert not_exists is False

def test_user_count(db, user_crud):
    """测试统计用户数量"""
    count = user_crud.count(db)
    assert count >= 0