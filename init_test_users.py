#!/usr/bin/env python3
"""
初始化测试用户脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.database import SessionLocal, engine, Base
from app.models.user import User
from app.utils.security import get_password_hash

def init_test_users():
    """初始化测试用户"""
    # 创建表（如果不存在）
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已有用户
        existing_users = db.query(User).all()
        if existing_users:
            print(f"数据库中已有 {len(existing_users)} 个用户，跳过初始化")
            for user in existing_users:
                print(f"  - {user.username} ({user.role})")
            return
        
        # 创建测试用户
        test_users = [
            {
                "username": "admin",
                "phone": "13800138000",
                "password": "Admin123",
                "role": "admin"
            },
            {
                "username": "operator",
                "phone": "13800138001",
                "password": "Operator123",
                "role": "operator"
            },
            {
                "username": "viewer",
                "phone": "13800138002",
                "password": "Viewer123",
                "role": "viewer"
            }
        ]
        
        for user_data in test_users:
            user = User(
                username=user_data["username"],
                phone=user_data["phone"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"]
            )
            db.add(user)
            print(f"创建用户: {user_data['username']} ({user_data['role']})")
        
        db.commit()
        print("\n✅ 测试用户初始化完成！")
        print("\n测试账户：")
        print("-" * 50)
        for user_data in test_users:
            print(f"用户名: {user_data['username']}")
            print(f"密码:   {user_data['password']}")
            print(f"角色:   {user_data['role']}")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("开始初始化测试用户...")
    print("=" * 50)
    init_test_users()
