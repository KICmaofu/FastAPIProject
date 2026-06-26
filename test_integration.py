import requests
import json
from datetime import datetime, timedelta

# 测试前后端集成
def test_integration():
    print("="*60)
    print("前后端集成测试")
    print("="*60)
    print()
    
    base_url = "http://localhost:8000"
    frontend_url = "http://localhost:5173"
    
    # 1. 测试后端服务状态
    print("1. 测试后端服务状态...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   [PASS] 后端服务正常运行")
        else:
            print(f"   [FAIL] 后端服务异常: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] 后端服务连接失败: {str(e)}")
    
    # 2. 测试前端服务状态
    print("\n2. 测试前端服务状态...")
    try:
        response = requests.get(f"{frontend_url}/")
        if response.status_code == 200:
            print("   [PASS] 前端服务正常运行")
        else:
            print(f"   [FAIL] 前端服务异常: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] 前端服务连接失败: {str(e)}")
    
    # 3. 测试注册新用户
    print("\n3. 测试用户注册接口...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json={"username": "integration_test", "phone": "13888888888", "password": "Test123456", "confirmPassword": "Test123456"}
        )
        if response.status_code == 200 or response.status_code == 409:
            print("   [PASS] 用户注册接口正常")
        else:
            print(f"   [FAIL] 用户注册失败: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   [FAIL] 用户注册接口调用失败: {str(e)}")
    
    # 4. 测试登录接口
    print("\n4. 测试用户登录接口...")
    token = None
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": "integration_test", "password": "Test123456", "captcha": "1234"}
        )
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                token = data["token"]
                print("   [PASS] 用户登录接口正常")
            else:
                print("   [FAIL] 登录响应格式不正确")
        else:
            # 尝试使用已存在的用户登录
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={"username": "testuser_new", "password": "Test123456", "captcha": "1234"}
            )
            if response.status_code == 200:
                data = response.json()
                token = data["token"]
                print("   [PASS] 用户登录接口正常（使用备用用户）")
            else:
                print(f"   [FAIL] 用户登录失败: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   [FAIL] 用户登录接口调用失败: {str(e)}")
    
    # 5. 测试带认证的接口调用
    print("\n5. 测试带认证的接口调用...")
    if token:
        try:
            response = requests.get(
                f"{base_url}/api/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                print("   [PASS] 带认证的用户信息接口正常")
            else:
                print(f"   [FAIL] 用户信息接口失败: {response.status_code}")
        except Exception as e:
            print(f"   [FAIL] 用户信息接口调用失败: {str(e)}")
    
    # 6. 测试机器人列表接口
    print("\n6. 测试机器人列表接口...")
    if token:
        try:
            response = requests.get(
                f"{base_url}/api/robot",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                print("   [PASS] 机器人列表接口正常")
            else:
                print(f"   [FAIL] 机器人列表接口失败: {response.status_code}")
        except Exception as e:
            print(f"   [FAIL] 机器人列表接口调用失败: {str(e)}")
    
    # 7. 测试环境数据接口
    print("\n7. 测试环境数据接口...")
    if token:
        try:
            response = requests.get(
                f"{base_url}/api/environment/latest",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                print("   [PASS] 环境数据接口正常")
            else:
                print(f"   [FAIL] 环境数据接口失败: {response.status_code}")
        except Exception as e:
            print(f"   [FAIL] 环境数据接口调用失败: {str(e)}")
    
    # 8. 测试告警列表接口
    print("\n8. 测试告警列表接口...")
    if token:
        try:
            response = requests.get(
                f"{base_url}/api/alerts",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                print("   [PASS] 告警列表接口正常")
            else:
                print(f"   [FAIL] 告警列表接口失败: {response.status_code}")
        except Exception as e:
            print(f"   [FAIL] 告警列表接口调用失败: {str(e)}")
    
    # 9. 测试热成像数据接口
    print("\n9. 测试热成像数据接口...")
    if token:
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            params = {
                "startTime": start_time.isoformat(),
                "endTime": end_time.isoformat(),
                "page": 1,
                "size": 10
            }
            response = requests.get(
                f"{base_url}/api/thermal-imaging/history",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            if response.status_code == 200:
                print("   [PASS] 热成像数据接口正常")
            else:
                print(f"   [FAIL] 热成像数据接口失败: {response.status_code}")
        except Exception as e:
            print(f"   [FAIL] 热成像数据接口调用失败: {str(e)}")
    
    print("\n" + "="*60)
    print("前后端集成测试完成")
    print("="*60)

if __name__ == "__main__":
    test_integration()