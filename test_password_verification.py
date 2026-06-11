import requests
import json

BASE_URL = "http://localhost:8000"

def test_password_verification():
    print("=" * 60)
    print("测试密码验证功能")
    print("=" * 60)
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "12305"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        response.raise_for_status()
        data = response.json()
        # 检查响应结构
        if "token" in data:
            token = data["token"]
        elif "data" in data and "token" in data["data"]:
            token = data["data"]["token"]
        else:
            print(f"✗ 登录失败: 响应格式不正确 - {data}")
            return
        print(f"✓ 登录成功，token: {token[:20]}...")
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"✗ 登录失败: {e}")
        return
    
    # 2. 测试不提供密码创建设备（应该失败）
    print("\n2. 测试不提供密码创建设备...")
    device_data_no_password = {
        "name": "Test Device",
        "type": "sensor",
        "model": "test-001"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices",
            json=device_data_no_password,
            headers=headers
        )
        if response.status_code == 422:
            print("✓ 正确拒绝：缺少密码字段")
            print(f"  响应: {response.json()}")
        else:
            print(f"✗ 意外响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    # 3. 测试提供错误密码创建设备（应该失败）
    print("\n3. 测试提供错误密码创建设备...")
    device_data_wrong_password = {
        "name": "Test Device",
        "type": "sensor",
        "model": "test-001",
        "password": "wrong_password"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices",
            json=device_data_wrong_password,
            headers=headers
        )
        if response.status_code == 401:
            print("✓ 正确拒绝：密码错误")
            print(f"  响应: {response.json()}")
        else:
            print(f"✗ 意外响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    # 4. 测试提供正确密码创建设备（应该成功）
    print("\n4. 测试提供正确密码创建设备...")
    device_data_correct = {
        "name": "Test Device",
        "type": "sensor",
        "model": "test-001",
        "password": "12305"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices",
            json=device_data_correct,
            headers=headers
        )
        if response.status_code == 200:
            print("✓ 设备创建成功")
            print(f"  响应: {response.json()}")
            device_id = response.json()["data"]["id"]
            
            # 5. 测试更新设备（错误密码）
            print(f"\n5. 测试更新设备 {device_id}（错误密码）...")
            update_data_wrong = {
                "name": "更新的设备名",
                "password": "wrong_password"
            }
            
            response = requests.put(
                f"{BASE_URL}/api/devices/{device_id}",
                json=update_data_wrong,
                headers=headers
            )
            if response.status_code == 401:
                print("✓ 正确拒绝：密码错误")
                print(f"  响应: {response.json()}")
            else:
                print(f"✗ 意外响应: {response.status_code} - {response.text}")
            
            # 6. 测试更新设备（正确密码）
            print(f"\n6. 测试更新设备 {device_id}（正确密码）...")
            update_data_correct = {
                "name": "更新的设备名",
                "password": "12305"
            }
            
            response = requests.put(
                f"{BASE_URL}/api/devices/{device_id}",
                json=update_data_correct,
                headers=headers
            )
            if response.status_code == 200:
                print("✓ 设备更新成功")
                print(f"  响应: {response.json()}")
                
                # 7. 测试删除设备（错误密码）
                print(f"\n7. 测试删除设备 {device_id}（错误密码）...")
                response = requests.delete(
                    f"{BASE_URL}/api/devices/{device_id}?password=wrong_password",
                    headers=headers
                )
                if response.status_code == 401:
                    print("✓ 正确拒绝：密码错误")
                    print(f"  响应: {response.json()}")
                else:
                    print(f"✗ 意外响应: {response.status_code} - {response.text}")
                
                # 8. 测试删除设备（正确密码）
                print(f"\n8. 测试删除设备 {device_id}（正确密码）...")
                response = requests.delete(
                    f"{BASE_URL}/api/devices/{device_id}?password=12305",
                    headers=headers
                )
                if response.status_code == 200:
                    print("✓ 设备删除成功")
                    print(f"  响应: {response.json()}")
                else:
                    print(f"✗ 意外响应: {response.status_code} - {response.text}")
            else:
                print(f"✗ 意外响应: {response.status_code} - {response.text}")
        else:
            print(f"✗ 意外响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_password_verification()
