"""
项目全面测试脚本
测试所有API端点、数据库操作和Socket服务器
"""
import requests
import socket
import json
import sys

BASE_URL = "http://localhost:8000"
SOCKET_HOST = "localhost"
SOCKET_PORT = 8888

test_results = []
token = None

def log_test(name, success, message=""):
    status = "✓ PASS" if success else "✗ FAIL"
    test_results.append({"name": name, "success": success, "message": message})
    print(f"{status}: {name}")
    if message:
        print(f"  {message}")

def test_health_check():
    """测试健康检查端点"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        success = response.status_code == 200 and data.get("code") == 200
        log_test("健康检查 /health", success, str(data))
        return success
    except Exception as e:
        log_test("健康检查 /health", False, str(e))
        return False

def test_root():
    """测试根路由"""
    try:
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        success = response.status_code == 200 and data.get("code") == 200
        log_test("根路由 /", success, str(data))
        return success
    except Exception as e:
        log_test("根路由 /", False, str(e))
        return False

def test_socket_status():
    """测试Socket状态端点"""
    try:
        response = requests.get(f"{BASE_URL}/socket/status")
        data = response.json()
        success = response.status_code == 200 and data.get("code") == 200
        log_test("Socket状态 /socket/status", success, f"Active: {data['data']['active_connections']}, Requests: {data['data']['total_requests']}")
        return success
    except Exception as e:
        log_test("Socket状态 /socket/status", False, str(e))
        return False

def test_user_register():
    """测试用户注册"""
    try:
        payload = {
            "username": "testuser_final",
            "password": "Test@123456",
            "real_name": "最终测试用户",
            "phone": "13800000099"
        }
        response = requests.post(f"{BASE_URL}/api/user/register", json=payload)
        data = response.json()
        success = response.status_code == 200 and data.get("code") == 200
        log_test("用户注册 /api/user/register", success, str(data))
        return success
    except Exception as e:
        log_test("用户注册 /api/user/register", False, str(e))
        return False

def test_user_login():
    """测试用户登录"""
    global token
    try:
        payload = {
            "username": "testuser_final",
            "password": "Test@123456"
        }
        response = requests.post(f"{BASE_URL}/api/user/login", json=payload)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            token = data.get("data", {}).get("token")
            user = data.get("data", {}).get("user", {})
            log_test("用户登录 /api/user/login", True, f"Token: {token[:30]}..., User: {user['username']}")
            return True
        else:
            log_test("用户登录 /api/user/login", False, str(data))
            return False
    except Exception as e:
        log_test("用户登录 /api/user/login", False, str(e))
        return False

def test_user_list():
    """测试用户列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/user/list", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            total = data.get('data', {}).get('total', 0) if isinstance(data.get('data'), dict) else 0
            log_test("用户列表 /api/user/list", True, f"Total: {total}")
            return True
        else:
            log_test("用户列表 /api/user/list", False, str(data))
            return False
    except Exception as e:
        log_test("用户列表 /api/user/list", False, str(e))
        return False

def test_robot_list():
    """测试机器人列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/robot/list", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            result = data.get('data')
            if isinstance(result, dict):
                total = result.get('total', 0)
                items = len(result.get('list', []))
                log_test("机器人列表 /api/robot/list", True, f"Total: {total}, Items: {items}")
                return True
            else:
                log_test("机器人列表 /api/robot/list", False, "返回格式错误")
                return False
        else:
            log_test("机器人列表 /api/robot/list", False, str(data))
            return False
    except Exception as e:
        log_test("机器人列表 /api/robot/list", False, str(e))
        return False

def test_sensor_data_list():
    """测试传感器数据列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/robot/sensor/history", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            result = data.get('data')
            if isinstance(result, dict):
                total = result.get('total', 0)
                items = len(result.get('list', []))
                log_test("传感器数据列表 /api/robot/sensor/history", True, f"Total: {total}, Items: {items}")
                return True
            else:
                log_test("传感器数据列表 /api/robot/sensor/history", False, "返回格式错误")
                return False
        else:
            log_test("传感器数据列表 /api/robot/sensor/history", False, str(data))
            return False
    except Exception as e:
        log_test("传感器数据列表 /api/robot/sensor/history", False, str(e))
        return False

def test_alarm_list():
    """测试报警列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/alarm/list", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            result = data.get('data')
            if isinstance(result, dict):
                total = result.get('total', 0)
                items = len(result.get('list', []))
                log_test("报警列表 /api/alarm/list", True, f"Total: {total}, Items: {items}")
                return True
            else:
                log_test("报警列表 /api/alarm/list", False, "返回格式错误")
                return False
        else:
            log_test("报警列表 /api/alarm/list", False, str(data))
            return False
    except Exception as e:
        log_test("报警列表 /api/alarm/list", False, str(e))
        return False

def test_patrol_task_list():
    """测试巡检任务列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/patrol/task/list", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            result = data.get('data')
            if isinstance(result, dict):
                total = result.get('total', 0)
                items = len(result.get('list', []))
                log_test("巡检任务列表 /api/patrol/task/list", True, f"Total: {total}, Items: {items}")
                return True
            else:
                log_test("巡检任务列表 /api/patrol/task/list", False, "返回格式错误")
                return False
        else:
            log_test("巡检任务列表 /api/patrol/task/list", False, str(data))
            return False
    except Exception as e:
        log_test("巡检任务列表 /api/patrol/task/list", False, str(e))
        return False

def test_robot_statistics():
    """测试机器人统计"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/robot/statistics", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            stats = data.get('data', {})
            log_test("机器人统计 /api/robot/statistics", True, f"Total: {stats.get('total')}, Online: {stats.get('online')}, Offline: {stats.get('offline')}")
            return True
        else:
            log_test("机器人统计 /api/robot/statistics", False, str(data))
            return False
    except Exception as e:
        log_test("机器人统计 /api/robot/statistics", False, str(e))
        return False

def test_alarm_statistics():
    """测试报警统计"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/alarm/statistics", headers=headers)
        data = response.json()
        if response.status_code == 200 and data.get("code") == 200:
            stats = data.get('data', {})
            log_test("报警统计 /api/alarm/statistics", True, f"Total: {stats.get('total')}, Pending: {stats.get('pending')}, Dealt: {stats.get('dealt')}")
            return True
        else:
            log_test("报警统计 /api/alarm/statistics", False, str(data))
            return False
    except Exception as e:
        log_test("报警统计 /api/alarm/statistics", False, str(e))
        return False

def test_socket_connection():
    """测试Socket服务器连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((SOCKET_HOST, SOCKET_PORT))
        
        # 接收欢迎消息
        welcome = sock.recv(1024).decode('utf-8')
        if "Welcome" in welcome:
            log_test("Socket服务器连接", True, "欢迎消息接收成功")
        else:
            log_test("Socket服务器连接", False, welcome)
            sock.close()
            return False
        
        # 发送正常数据
        normal_data = {
            "robot_sn": "SOCKET_TEST_001",
            "temperature": 28.5,
            "humidity": 55,
            "smoke_level": 25,
            "fire_risk": 0,
            "battery": 90
        }
        sock.sendall((json.dumps(normal_data) + "\n").encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        
        if "successfully" in response:
            log_test("Socket正常数据处理", True, response.strip())
        else:
            log_test("Socket正常数据处理", False, response)
        
        # 发送报警数据
        alarm_data = {
            "robot_sn": "SOCKET_TEST_002",
            "temperature": 95.0,
            "humidity": 25,
            "smoke_level": 90,
            "fire_risk": 3,
            "battery": 60
        }
        sock.sendall((json.dumps(alarm_data) + "\n").encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        
        if "successfully" in response and "Alarms: 1" in response:
            log_test("Socket报警数据自动创建", True, response.strip())
        else:
            log_test("Socket报警数据自动创建", False, response)
        
        sock.close()
        return True
    except Exception as e:
        log_test("Socket服务器连接", False, str(e))
        return False

def test_api_docs():
    """测试API文档"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        success = response.status_code == 200
        log_test("API文档 /docs", success)
        return success
    except Exception as e:
        log_test("API文档 /docs", False, str(e))
        return False

def main():
    print("=" * 60)
    print("智能巡检系统 - 全面测试")
    print("=" * 60)
    print()
    
    # 基础测试
    print("1. 基础端点测试")
    print("-" * 40)
    test_health_check()
    test_root()
    test_socket_status()
    test_api_docs()
    print()
    
    # 用户认证测试
    print("2. 用户认证测试")
    print("-" * 40)
    test_user_register()
    test_user_login()
    print()
    
    # Socket服务器测试（先执行以创建数据）
    print("3. Socket服务器测试")
    print("-" * 40)
    test_socket_connection()
    print()
    
    # API端点测试（需要认证）
    print("4. API端点测试")
    print("-" * 40)
    test_user_list()
    test_robot_list()
    test_robot_statistics()
    test_sensor_data_list()
    test_alarm_list()
    test_alarm_statistics()
    test_patrol_task_list()
    print()
    
    # 统计结果
    print("=" * 60)
    print("测试结果统计")
    print("=" * 60)
    
    passed = sum(1 for r in test_results if r["success"])
    failed = sum(1 for r in test_results if not r["success"])
    total = len(test_results)
    
    print(f"总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if failed > 0:
        print()
        print("失败的测试:")
        for r in test_results:
            if not r["success"]:
                print(f"  - {r['name']}: {r['message']}")
    
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)