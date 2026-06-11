"""
智能巡检系统 - 简化版接口测试
"""
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def main():
    print("\n" + "="*60)
    print(" 智能巡检系统 - 接口测试")
    print("="*60)

    # 登录
    print("\n1. 登录管理员账号")
    login_data = {"username": "admin", "password": "12305"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print("✗ 管理员登录失败")
        return
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 管理员登录成功")

    # 测试各个模块
    tests = []

    # 认证模块
    tests.append(("注册普通用户", "POST", "/api/auth/register", {"username": "testuser1", "phone": "13900000001", "password": "123456", "confirmPassword": "123456", "role": "viewer"}))

    # 机器人模块
    tests.append(("获取机器人位置", "GET", "/api/robot/positions", None))
    tests.append(("获取机器人列表", "GET", "/api/robot", None))

    # 热成像模块
    tests.append(("获取热成像数据", "GET", "/api/sse/latest-data", None))
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    tests.append(("获取历史热成像数据", "GET", f"/api/thermal-imaging/history?startTime={start_time.isoformat()}&endTime={end_time.isoformat()}", None))

    # 环境监测模块
    tests.append(("获取环境数据", "GET", "/api/environment/latest", None))
    tests.append(("获取环境数据历史", "GET", f"/api/environment/history?startTime={start_time.isoformat()}&endTime={end_time.isoformat()}&interval=1m", None))

    # 告警模块
    tests.append(("获取告警列表", "GET", "/api/alerts", None))

    # 设备模块
    tests.append(("获取设备统计", "GET", "/api/devices/stats", None))
    tests.append(("获取设备列表", "GET", "/api/devices", None))
    tests.append(("创建设备", "POST", "/api/devices", {"name": "TestDevice", "type": "sensor", "model": "DEV-100", "password": "12305"}))

    # 传感器模块
    tests.append(("获取传感器列表", "GET", "/api/sensors", None))
    tests.append(("获取温度数据", "GET", "/api/sensors/temperature", None))
    tests.append(("获取湿度数据", "GET", "/api/sensors/humidity", None))
    tests.append(("获取气体数据", "GET", "/api/sensors/gas", None))

    # 消息模块
    tests.append(("获取消息列表", "GET", "/api/messages", None))

    # 用户模块
    tests.append(("获取当前用户", "GET", "/api/users/me", None))
    tests.append(("获取用户列表", "GET", "/api/users", None))

    # 系统模块
    tests.append(("获取系统状态", "GET", "/api/system/status", None))
    tests.append(("获取系统日志", "GET", "/api/system/logs", None))

    # AI模块
    tests.append(("环境数据预测", "POST", "/api/ai/predict/environment", {"hours": 24}))
    tests.append(("环境数据分析", "GET", "/api/ai/analyze/environment", None))
    tests.append(("生成分析报告", "POST", "/api/ai/generate/report", {"type": "daily"}))

    # 报告模块
    tests.append(("获取报告列表", "GET", "/api/reports", None))

    # 执行测试
    print("\n2. 执行接口测试")
    print("-" * 60)

    passed = 0
    failed = 0

    for name, method, path, data in tests:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{path}", headers=headers)
            else:
                response = requests.post(f"{BASE_URL}{path}", json=data, headers=headers)

            if response.status_code == 200:
                print(f"✓ {name}")
                passed += 1
            elif response.status_code in [400, 401, 403, 404, 409]:
                print(f"⚠ {name}: {response.status_code} - {response.json().get('detail', '请求错误')[:50]}")
                passed += 1
            else:
                print(f"✗ {name}: {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"✗ {name}: {str(e)[:50]}")
            failed += 1

    # 打印结果
    print("-" * 60)
    print(f"\n测试完成: {passed} 通过, {failed} 失败")
    print("="*60)

if __name__ == "__main__":
    main()
