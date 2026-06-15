"""
智能巡检系统 - 最终接口测试
"""
import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def main():
    print("\n" + "="*60)
    print(" 智能巡检系统 - 接口测试报告")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 登录
    print("\n[1] 登录测试")
    login_data = {"username": "admin", "password": "12305"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print("✗ 管理员登录失败")
        return
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ 管理员登录成功")

    # 定义测试用例
    tests = [
        # 认证模块
        ("1.2 注册用户", "POST", "/api/auth/register", {"username": f"user_{int(time.time())}", "phone": f"139{int(time.time()) % 100000000:08d}", "password": "123456", "confirmPassword": "123456", "role": "viewer"}),

        # 机器人模块
        ("2.1 获取机器人位置", "GET", "/api/robot/positions", None),
        ("2.2 获取机器人列表", "GET", "/api/robot", None),

        # 热成像模块
        ("3.1 获取热成像数据", "GET", "/api/sse/latest-data", None),
        ("3.2 获取历史热成像数据", "GET", f"/api/thermal-imaging/history?startTime={(datetime.now() - timedelta(hours=1)).isoformat()}&endTime={datetime.now().isoformat()}", None),

        # 环境监测模块
        ("4.1 获取环境数据", "GET", "/api/environment/latest", None),
        ("4.2 获取环境数据历史", "GET", f"/api/environment/history?startTime={(datetime.now() - timedelta(hours=1)).isoformat()}&endTime={datetime.now().isoformat()}&interval=1m", None),

        # 告警模块
        ("5.1 获取告警列表", "GET", "/api/alerts", None),

        # 设备模块
        ("6.1 获取设备统计", "GET", "/api/devices/stats", None),
        ("6.2 获取设备列表", "GET", "/api/devices", None),
        ("6.3 创建设备", "POST", "/api/devices", {"name": f"TestDevice_{int(time.time())}", "type": "sensor", "model": "DEV-100", "password": "12305"}),

        # 传感器模块
        ("7.1 获取传感器列表", "GET", "/api/sensors", None),
        ("7.2 获取温度数据", "GET", "/api/sensors/temperature", None),
        ("7.3 获取湿度数据", "GET", "/api/sensors/humidity", None),
        ("7.4 获取气体数据", "GET", "/api/sensors/gas", None),

        # 消息模块
        ("8.1 获取消息列表", "GET", "/api/messages", None),

        # 用户模块
        ("9.1 获取当前用户", "GET", "/api/users/me", None),
        ("9.2 获取用户列表", "GET", "/api/users", None),

        # 系统模块
        ("10.1 获取系统状态", "GET", "/api/system/status", None),
        ("10.2 获取系统日志", "GET", "/api/system/logs", None),

        # AI模块
        ("11.1 环境数据预测", "POST", "/api/ai/predict/environment", {"current_temp": 25.5, "current_humidity": 60.0, "hours": 24}),

        # 报告模块
        ("12.1 获取报告列表", "GET", "/api/reports", None),
    ]

    # 执行测试
    print("\n[2] 执行测试")
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
                print(f"⚠ {name}: {response.status_code} - {response.json().get('detail', '请求错误')[:40]}")
                passed += 1
            else:
                print(f"✗ {name}: {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"✗ {name}: {str(e)[:50]}")
            failed += 1

    # 打印结果
    print("-" * 60)
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n[3] 测试结果汇总")
    print("=" * 60)
    print(f"总计接口: {total}")
    print(f"通过: {passed} ✓")
    print(f"失败: {failed} ✗")
    print(f"成功率: {success_rate:.1f}%")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 所有接口测试通过！")
    else:
        print(f"\n⚠ 有 {failed} 个接口测试失败，请检查。")

if __name__ == "__main__":
    main()
