"""
智能巡检系统 - 接口测试脚本
测试所有已实现的API接口
"""
import requests
import time

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.token = None
        self.admin_token = None
        self.headers = {}
        self.admin_headers = {}

    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")

    def print_result(self, name, response):
        status = "✓" if response.status_code < 400 else "✗"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code >= 400:
            try:
                print(f"  错误: {response.json()}")
            except:
                print(f"  错误: {response.text[:100]}")
        return response.status_code < 400

    def login_admin(self):
        """登录管理员账号"""
        self.print_section("1. 登录管理员账号")
        login_data = {"username": "admin", "password": "12305"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            self.admin_token = data.get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            print(f"✓ 管理员登录成功")
            return True
        print(f"✗ 管理员登录失败: {response.text}")
        return False

    def login_operator(self):
        """登录操作员账号"""
        self.print_section("1b. 登录操作员账号")
        login_data = {"username": "operator_user", "password": "operator123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.operator_token = data.get("token")
            self.operator_headers = {"Authorization": f"Bearer {self.operator_token}"}
            print(f"✓ 操作员登录成功")
            return True
        print(f"✗ 操作员登录失败: {response.text}")
        return False

    def test_auth_module(self):
        """测试认证模块"""
        self.print_section("认证模块 - 用户注册")

        # 测试注册普通用户
        register_data = {
            "username": f"test_user_{int(time.time())}",
            "phone": f"139{int(time.time()) % 100000000:08d}",
            "password": "test123",
            "confirmPassword": "test123",
            "role": "viewer"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        self.print_result("注册普通用户", response)

        # 测试注册操作员
        register_data["username"] = f"test_operator_{int(time.time())}"
        register_data["phone"] = f"138{int(time.time()) % 100000000:08d}"
        register_data["role"] = "operator"
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        self.print_result("注册操作员", response)

        # 测试无密钥注册管理员（应该失败）
        register_data["username"] = f"test_admin_{int(time.time())}"
        register_data["phone"] = f"137{int(time.time()) % 100000000:08d}"
        register_data["role"] = "admin"
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        self.print_result("无密钥注册管理员（应失败）", response)

        # 测试有密钥注册管理员
        register_data["adminKey"] = "admin-secret-key"
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        self.print_result("有密钥注册管理员", response)

    def test_robot_module(self):
        """测试机器人模块"""
        self.print_section("机器人模块")

        # 获取机器人位置
        response = requests.get(f"{BASE_URL}/api/robot/positions", headers=self.headers)
        self.print_result("获取机器人位置", response)

        # 获取机器人列表
        response = requests.get(f"{BASE_URL}/api/robot", headers=self.headers)
        self.print_result("获取机器人列表", response)

        # 添加机器人（需要管理员权限和密码验证）
        robot_data = {
            "name": f"测试机器人_{int(time.time())}",
            "model": "RBT-2000",
            "location": "A区一楼",
            "password_verify": {"password": "12305"}
        }
        response = requests.post(f"{BASE_URL}/api/robot", json=robot_data, headers=self.admin_headers)
        self.print_result("添加机器人", response)
        robot_id = None
        if response.status_code == 200:
            try:
                robot_id = response.json().get("data", {}).get("id")
            except:
                pass

        if robot_id:
            # 更新机器人
            update_data = {"name": "更新的机器人名称", "password_verify": {"password": "12305"}}
            response = requests.put(f"{BASE_URL}/api/robot/{robot_id}", json=update_data, headers=self.admin_headers)
            self.print_result("更新机器人", response)

            # 控制机器人
            control_data = {"action": "move", "speed": 5}
            response = requests.post(f"{BASE_URL}/api/robot/{robot_id}/control", json=control_data, headers=self.admin_headers)
            self.print_result("控制机器人", response)

            # 删除机器人
            delete_data = {"password_verify": {"password": "12305"}}
            response = requests.delete(f"{BASE_URL}/api/robot/{robot_id}", json=delete_data, headers=self.admin_headers)
            self.print_result("删除机器人", response)

    def test_thermal_module(self):
        """测试热成像模块"""
        self.print_section("热成像模块")

        # 获取最新热成像数据
        response = requests.get(f"{BASE_URL}/api/sse/latest-data", headers=self.headers)
        self.print_result("获取最新热成像数据", response)

        # 获取历史热成像数据
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        params = {
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat()
        }
        response = requests.get(f"{BASE_URL}/api/thermal-imaging/history", params=params, headers=self.headers)
        self.print_result("获取历史热成像数据", response)

    def test_environment_module(self):
        """测试环境监测模块"""
        self.print_section("环境监测模块")

        # 获取最新环境数据
        response = requests.get(f"{BASE_URL}/api/environment/latest", headers=self.headers)
        self.print_result("获取最新环境数据", response)

        # 获取环境数据历史
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        params = {
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat(),
            "interval": "1m"
        }
        response = requests.get(f"{BASE_URL}/api/environment/history", params=params, headers=self.headers)
        self.print_result("获取环境数据历史", response)

    def test_alert_module(self):
        """测试告警模块"""
        self.print_section("告警模块")

        # 获取告警列表
        response = requests.get(f"{BASE_URL}/api/alerts", headers=self.headers)
        self.print_result("获取告警列表", response)

        if response.status_code == 200 and response.json().get("data", {}).get("list"):
            alert_id = response.json()["data"]["list"][0].get("id")
            if alert_id:
                # 处理告警
                process_data = {"action": "confirm", "remark": "测试处理"}
                response = requests.put(f"{BASE_URL}/api/alerts/{alert_id}/process", json=process_data, headers=self.headers)
                self.print_result("处理告警", response)

    def test_device_module(self):
        """测试设备模块"""
        self.print_section("设备模块")

        # 获取设备统计
        response = requests.get(f"{BASE_URL}/api/devices/stats", headers=self.headers)
        self.print_result("获取设备统计", response)

        # 获取设备列表
        response = requests.get(f"{BASE_URL}/api/devices", headers=self.headers)
        self.print_result("获取设备列表", response)

        # 创建设备（需要密码验证）
        device_data = {
            "name": f"测试设备_{int(time.time())}",
            "type": "sensor",
            "model": "DEV-100",
            "password": "12305"
        }
        response = requests.post(f"{BASE_URL}/api/devices", json=device_data, headers=self.headers)
        self.print_result("创建设备", response)
        device_id = None
        if response.status_code == 200:
            try:
                device_id = response.json().get("data", {}).get("id")
            except:
                pass

        if device_id:
            # 更新设备
            update_data = {"name": "更新的设备名称", "password": "12305"}
            response = requests.put(f"{BASE_URL}/api/devices/{device_id}", json=update_data, headers=self.headers)
            self.print_result("更新设备", response)

            # 删除设备
            response = requests.delete(f"{BASE_URL}/api/devices/{device_id}?password=12305", headers=self.headers)
            self.print_result("删除设备", response)

    def test_sensor_module(self):
        """测试传感器模块"""
        self.print_section("传感器模块")

        # 获取传感器列表
        response = requests.get(f"{BASE_URL}/api/sensors", headers=self.headers)
        self.print_result("获取传感器列表", response)

        # 获取最新温度数据
        response = requests.get(f"{BASE_URL}/api/sensors/temperature", headers=self.headers)
        self.print_result("获取最新温度数据", response)

        # 获取最新湿度数据
        response = requests.get(f"{BASE_URL}/api/sensors/humidity", headers=self.headers)
        self.print_result("获取最新湿度数据", response)

        # 获取最新可燃气体数据
        response = requests.get(f"{BASE_URL}/api/sensors/gas", headers=self.headers)
        self.print_result("获取最新可燃气体数据", response)

    def test_message_module(self):
        """测试消息模块"""
        self.print_section("消息模块")

        # 获取消息列表
        response = requests.get(f"{BASE_URL}/api/messages", headers=self.headers)
        self.print_result("获取消息列表", response)

        if response.status_code == 200 and response.json().get("data", {}).get("list"):
            message_id = response.json()["data"]["list"][0].get("id")
            if message_id:
                # 标记消息已读
                response = requests.put(f"{BASE_URL}/api/messages/{message_id}/read", headers=self.headers)
                self.print_result("标记消息已读", response)

        # 标记所有消息已读
        response = requests.put(f"{BASE_URL}/api/messages/read-all", headers=self.headers)
        self.print_result("标记所有消息已读", response)

    def test_user_module(self):
        """测试用户模块"""
        self.print_section("用户模块")

        # 获取当前用户信息
        response = requests.get(f"{BASE_URL}/api/users/me", headers=self.headers)
        self.print_result("获取当前用户信息", response)

        # 获取用户列表（需要管理员权限）
        response = requests.get(f"{BASE_URL}/api/users", headers=self.admin_headers)
        self.print_result("获取用户列表", response)

    def test_system_module(self):
        """测试系统模块"""
        self.print_section("系统模块")

        # 获取系统状态
        response = requests.get(f"{BASE_URL}/api/system/status", headers=self.headers)
        self.print_result("获取系统状态", response)

        # 获取系统日志（需要管理员权限）
        response = requests.get(f"{BASE_URL}/api/system/logs", headers=self.admin_headers)
        self.print_result("获取系统日志", response)

    def test_ai_module(self):
        """测试AI模块"""
        self.print_section("AI模块")

        # 环境数据预测
        predict_data = {"hours": 24}
        response = requests.post(f"{BASE_URL}/api/ai/predict/environment", json=predict_data, headers=self.headers)
        self.print_result("环境数据预测", response)

        # 环境数据分析
        response = requests.get(f"{BASE_URL}/api/ai/analyze/environment", headers=self.headers)
        self.print_result("环境数据分析", response)

        # 智能分析报告
        report_data = {"type": "daily"}
        response = requests.post(f"{BASE_URL}/api/ai/generate/report", json=report_data, headers=self.headers)
        self.print_result("生成分析报告", response)

    def test_report_module(self):
        """测试报告模块"""
        self.print_section("报告模块")

        # 获取报告列表
        response = requests.get(f"{BASE_URL}/api/reports", headers=self.headers)
        self.print_result("获取报告列表", response)

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print(" 智能巡检系统 - 接口测试")
        print("="*60)
        print(f"测试地址: {BASE_URL}")

        # 登录
        if not self.login_admin():
            print("\n✗ 管理员登录失败，测试终止")
            return

        self.login_operator()

        # 测试各个模块
        self.test_auth_module()
        self.test_robot_module()
        self.test_thermal_module()
        self.test_environment_module()
        self.test_alert_module()
        self.test_device_module()
        self.test_sensor_module()
        self.test_message_module()
        self.test_user_module()
        self.test_system_module()
        self.test_ai_module()
        self.test_report_module()

        # 打印测试完成
        self.print_section("测试完成")
        print("\n所有接口测试已完成！")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
