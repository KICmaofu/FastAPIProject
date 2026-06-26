import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TEST_REPORTS = []

def log_test(test_name, status, message, response=None):
    report = {
        "test_name": test_name,
        "status": status,
        "message": message,
        "response": response
    }
    TEST_REPORTS.append(report)
    status_mark = "PASS" if status == "PASS" else ("FAIL" if status == "FAIL" else "SKIP")
    print(f"[{status_mark}] {test_name}: {message}")
    if response:
        print(f"   Response: {json.dumps(response, ensure_ascii=False)[:200]}...")
    print()

def test_auth_register():
    """测试注册接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": "testuser_new", "phone": "13999999999", "password": "Test123456", "confirmPassword": "Test123456"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("注册接口 /api/auth/register", "PASS", "注册成功")
                return True
            else:
                log_test("注册接口 /api/auth/register", "FAIL", "响应数据格式不正确")
        elif response.status_code == 409:
            log_test("注册接口 /api/auth/register", "SKIP", "用户已存在，跳过注册")
            return True
        else:
            log_test("注册接口 /api/auth/register", "FAIL", f"HTTP状态码: {response.status_code}, 响应: {response.text[:100]}")
    except Exception as e:
        log_test("注册接口 /api/auth/register", "FAIL", f"请求异常: {str(e)}")
    return False

def test_auth_logout(token):
    """测试登出接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            log_test("登出接口 /api/auth/logout", "PASS", "登出成功")
        elif response.status_code == 404:
            log_test("登出接口 /api/auth/logout", "SKIP", "接口未实现")
        else:
            log_test("登出接口 /api/auth/logout", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("登出接口 /api/auth/logout", "FAIL", f"请求异常: {str(e)}")

def test_auth_login(username="testuser_new", password="Test123456"):
    """测试登录接口"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": username, "password": password, "captcha": "1234"}
        )
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                log_test("登录接口 /api/auth/login", "PASS", "登录成功")
                return data["token"]
            else:
                log_test("登录接口 /api/auth/login", "FAIL", "响应数据格式不正确")
        else:
            log_test("登录接口 /api/auth/login", "FAIL", f"HTTP状态码: {response.status_code}, 响应: {response.text[:100]}")
    except Exception as e:
        log_test("登录接口 /api/auth/login", "FAIL", f"请求异常: {str(e)}")
    return None

def test_users_list(token):
    """测试用户列表接口（需要管理员权限）"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("用户列表接口 /api/users", "PASS", "获取用户列表成功")
            else:
                log_test("用户列表接口 /api/users", "FAIL", "响应数据格式不正确")
        elif response.status_code == 403:
            log_test("用户列表接口 /api/users", "SKIP", "需要管理员权限，当前用户无权限")
        else:
            log_test("用户列表接口 /api/users", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("用户列表接口 /api/users", "FAIL", f"请求异常: {str(e)}")

def test_users_me(token):
    """测试获取当前用户接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200 and "data" in data:
                log_test("当前用户接口 /api/users/me", "PASS", "获取当前用户成功")
            else:
                log_test("当前用户接口 /api/users/me", "FAIL", "响应数据格式不正确")
        else:
            log_test("当前用户接口 /api/users/me", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("当前用户接口 /api/users/me", "FAIL", f"请求异常: {str(e)}")

def test_robots_list(token):
    """测试机器人列表接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/robot",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("机器人列表接口 /api/robot", "PASS", "获取机器人列表成功")
            else:
                log_test("机器人列表接口 /api/robot", "FAIL", "响应数据格式不正确")
        else:
            log_test("机器人列表接口 /api/robot", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("机器人列表接口 /api/robot", "FAIL", f"请求异常: {str(e)}")

def test_environment_data(token=None):
    """测试环境数据接口"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.get(f"{BASE_URL}/api/environment/latest", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("环境数据接口 /api/environment/latest", "PASS", "获取环境数据成功")
            else:
                log_test("环境数据接口 /api/environment/latest", "FAIL", "响应数据格式不正确")
        elif response.status_code == 401:
            log_test("环境数据接口 /api/environment/latest", "SKIP", "需要认证，跳过")
        else:
            log_test("环境数据接口 /api/environment/latest", "FAIL", f"HTTP状态码: {response.status_code}, 响应: {response.text[:100]}")
    except Exception as e:
        log_test("环境数据接口 /api/environment/latest", "FAIL", f"请求异常: {str(e)}")

def test_thermal_data(token):
    """测试热成像数据接口"""
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
            f"{BASE_URL}/api/thermal-imaging/history",
            headers={"Authorization": f"Bearer {token}"},
            params=params
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("热成像数据接口 /api/thermal-imaging/history", "PASS", "获取热成像数据成功")
            else:
                log_test("热成像数据接口 /api/thermal-imaging/history", "FAIL", "响应数据格式不正确")
        else:
            log_test("热成像数据接口 /api/thermal-imaging/history", "FAIL", f"HTTP状态码: {response.status_code}, 响应: {response.text[:100]}")
    except Exception as e:
        log_test("热成像数据接口 /api/thermal-imaging/history", "FAIL", f"请求异常: {str(e)}")

def test_alerts_list(token):
    """测试告警列表接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/alerts",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("告警列表接口 /api/alerts", "PASS", "获取告警列表成功")
            else:
                log_test("告警列表接口 /api/alerts", "FAIL", "响应数据格式不正确")
        else:
            log_test("告警列表接口 /api/alerts", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("告警列表接口 /api/alerts", "FAIL", f"请求异常: {str(e)}")

def test_messages_list(token):
    """测试消息列表接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/messages",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) or ("code" in data and data["code"] == 200):
                log_test("消息列表接口 /api/messages", "PASS", "获取消息列表成功")
            else:
                log_test("消息列表接口 /api/messages", "FAIL", "响应数据格式不正确")
        else:
            log_test("消息列表接口 /api/messages", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("消息列表接口 /api/messages", "FAIL", f"请求异常: {str(e)}")

def test_robot_add(token):
    """测试添加机器人接口（需要管理员权限）"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/robot",
            json={
                "name": "测试机器人",
                "model": "TestModel",
                "location": "测试位置",
                "password": "Test123456"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("添加机器人接口 POST /api/robot", "PASS", "添加机器人成功")
                return data["data"].get("id") if data.get("data") else None
            else:
                log_test("添加机器人接口 POST /api/robot", "FAIL", f"响应数据格式不正确: {response.text[:100]}")
        elif response.status_code == 403:
            log_test("添加机器人接口 POST /api/robot", "SKIP", "需要管理员权限，当前用户无权限")
        else:
            log_test("添加机器人接口 POST /api/robot", "FAIL", f"HTTP状态码: {response.status_code}, 响应: {response.text[:100]}")
    except Exception as e:
        log_test("添加机器人接口 POST /api/robot", "FAIL", f"请求异常: {str(e)}")
    return None

def test_robot_update(token, robot_id):
    """测试更新机器人接口"""
    if not robot_id:
        log_test("更新机器人接口 PUT /api/robot/{id}", "SKIP", "需要先添加机器人")
        return
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/robot/{robot_id}",
            json={
                "name": "测试机器人_更新",
                "model": "TestModel_Updated",
                "password": "Test123456"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("更新机器人接口 PUT /api/robot/{id}", "PASS", "更新机器人成功")
            else:
                log_test("更新机器人接口 PUT /api/robot/{id}", "FAIL", "响应数据格式不正确")
        elif response.status_code == 403:
            log_test("更新机器人接口 PUT /api/robot/{id}", "SKIP", "需要管理员权限")
        else:
            log_test("更新机器人接口 PUT /api/robot/{id}", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("更新机器人接口 PUT /api/robot/{id}", "FAIL", f"请求异常: {str(e)}")

def test_robot_delete(token, robot_id):
    """测试删除机器人接口"""
    if not robot_id:
        log_test("删除机器人接口 DELETE /api/robot/{id}", "SKIP", "需要先添加机器人")
        return
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/robot/{robot_id}",
            json={"password": "Test123456"},
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("删除机器人接口 DELETE /api/robot/{id}", "PASS", "删除机器人成功")
            else:
                log_test("删除机器人接口 DELETE /api/robot/{id}", "FAIL", "响应数据格式不正确")
        elif response.status_code == 403:
            log_test("删除机器人接口 DELETE /api/robot/{id}", "SKIP", "需要管理员权限")
        else:
            log_test("删除机器人接口 DELETE /api/robot/{id}", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("删除机器人接口 DELETE /api/robot/{id}", "FAIL", f"请求异常: {str(e)}")

def test_unauthorized_access():
    """测试未授权访问受保护接口"""
    try:
        response = requests.get(f"{BASE_URL}/api/users/me")
        if response.status_code == 401:
            log_test("未授权访问测试", "PASS", "成功拒绝未授权访问，返回401")
        else:
            log_test("未授权访问测试", "FAIL", f"期望401，实际返回: {response.status_code}")
    except Exception as e:
        log_test("未授权访问测试", "FAIL", f"请求异常: {str(e)}")

def test_device_list(token):
    """测试设备列表接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/devices",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("设备列表接口 /api/devices", "PASS", "获取设备列表成功")
            else:
                log_test("设备列表接口 /api/devices", "FAIL", "响应数据格式不正确")
        else:
            log_test("设备列表接口 /api/devices", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("设备列表接口 /api/devices", "FAIL", f"请求异常: {str(e)}")

def test_sensor_data(token):
    """测试传感器温度数据接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/sensors/temperature",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("传感器温度接口 /api/sensors/temperature", "PASS", "获取温度数据成功")
            else:
                log_test("传感器温度接口 /api/sensors/temperature", "FAIL", "响应数据格式不正确")
        else:
            log_test("传感器温度接口 /api/sensors/temperature", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("传感器温度接口 /api/sensors/temperature", "FAIL", f"请求异常: {str(e)}")

def test_system_status(token):
    """测试系统状态接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/system/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("系统状态接口 /api/system/status", "PASS", "获取系统状态成功")
            else:
                log_test("系统状态接口 /api/system/status", "FAIL", "响应数据格式不正确")
        else:
            log_test("系统状态接口 /api/system/status", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("系统状态接口 /api/system/status", "FAIL", f"请求异常: {str(e)}")

def test_report_list(token):
    """测试报告列表接口"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/reports",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if "code" in data and data["code"] == 200:
                log_test("报告列表接口 /api/reports", "PASS", "获取报告列表成功")
            else:
                log_test("报告列表接口 /api/reports", "FAIL", "响应数据格式不正确")
        else:
            log_test("报告列表接口 /api/reports", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("报告列表接口 /api/reports", "FAIL", f"请求异常: {str(e)}")

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                log_test("健康检查接口 /", "PASS", "服务正常运行")
            else:
                log_test("健康检查接口 /", "FAIL", "响应数据格式不正确")
        else:
            log_test("健康检查接口 /", "FAIL", f"HTTP状态码: {response.status_code}")
    except Exception as e:
        log_test("健康检查接口 /", "FAIL", f"请求异常: {str(e)}")

def test_negative_login():
    """测试错误登录（无效凭证）"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "wronguser", "password": "wrongpass", "captcha": "1234"}
        )
        if response.status_code == 400:
            log_test("登录接口（错误凭证）", "PASS", "正确拒绝无效登录")
        else:
            log_test("登录接口（错误凭证）", "FAIL", f"期望400，实际返回: {response.status_code}")
    except Exception as e:
        log_test("登录接口（错误凭证）", "FAIL", f"请求异常: {str(e)}")

def test_negative_register():
    """测试错误注册（密码不匹配）"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": "test", "phone": "13900139000", "password": "Test123456", "confirmPassword": "Different123"}
        )
        if response.status_code == 400:
            log_test("注册接口（密码不匹配）", "PASS", "正确拒绝密码不匹配")
        else:
            log_test("注册接口（密码不匹配）", "FAIL", f"期望400，实际返回: {response.status_code}")
    except Exception as e:
        log_test("注册接口（密码不匹配）", "FAIL", f"请求异常: {str(e)}")

def generate_report():
    """生成测试报告"""
    print("="*60)
    print("API接口测试报告")
    print("="*60)
    
    passed = sum(1 for r in TEST_REPORTS if r["status"] == "PASS")
    failed = sum(1 for r in TEST_REPORTS if r["status"] == "FAIL")
    skipped = sum(1 for r in TEST_REPORTS if r["status"] == "SKIP")
    
    print()
    print("测试结果统计:")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  跳过: {skipped}")
    if passed + failed > 0:
        print(f"  通过率: {passed / (passed + failed) * 100:.1f}%")
    
    if failed > 0:
        print()
        print("失败的测试用例:")
        for report in TEST_REPORTS:
            if report["status"] == "FAIL":
                print(f"  - {report['test_name']}: {report['message']}")
    
    print()
    print("="*60)

if __name__ == "__main__":
    print("开始执行后端API接口测试...")
    print("="*60)
    
    test_health_check()
    
    test_auth_register()
    
    token = test_auth_login()
    
    if token:
        test_users_list(token)
        test_users_me(token)
        test_alerts_list(token)
        test_messages_list(token)
        test_robots_list(token)
        test_environment_data(token)
        test_thermal_data(token)
        test_device_list(token)
        test_sensor_data(token)
        test_system_status(token)
        test_report_list(token)
        
        robot_id = test_robot_add(token)
        test_robot_update(token, robot_id)
        test_robot_delete(token, robot_id)
    
    test_environment_data()
    test_unauthorized_access()
    test_negative_login()
    test_negative_register()
    
    if token:
        test_auth_logout(token)
    
    generate_report()