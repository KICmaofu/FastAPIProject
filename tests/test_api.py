import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL) as client:
        yield client

@pytest.fixture(scope="module")
def admin_token(client):
    response = client.post("/api/user/login", json={
        "username": "admin",
        "password": "123456"
    })
    assert response.status_code == 200
    data = response.json()
    return data["data"]["token"]

@pytest.fixture(scope="module")
def user_token(client):
    response = client.post("/api/user/register", json={
        "username": "test_oper",
        "password": "123456",
        "real_name": "运维员",
        "phone": "13900139000"
    })
    response = client.post("/api/user/login", json={
        "username": "test_oper",
        "password": "123456"
    })
    assert response.status_code == 200
    data = response.json()
    return data["data"]["token"]

class TestHealthCheck:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "fire-patrol-server is running"

class TestUserAuthentication:
    def test_register(self, client):
        response = client.post("/api/user/register", json={
            "username": "test_user",
            "password": "123456",
            "real_name": "测试用户",
            "phone": "13800138000"
        })
        data = response.json()
        assert data["code"] in [200, 400]

    def test_login(self, client):
        response = client.post("/api/user/login", json={
            "username": "admin",
            "password": "123456"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "token" in data["data"]
        assert "user" in data["data"]

    def test_login_failure(self, client):
        response = client.post("/api/user/login", json={
            "username": "admin",
            "password": "wrong_password"
        })
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400

class TestAuthSecurity:
    def test_unauthorized_access(self, client):
        response = client.get("/api/user/info")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/user/info", headers=headers)
        assert response.status_code == 401

    def test_permission_denied(self, client, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/user/list?page=1&pageSize=10", headers=headers)
        assert response.status_code == 403

class TestUserModule:
    def test_get_user_info(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/user/info", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
        assert "username" in data["data"]

    def test_get_user_list(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/user/list?page=1&pageSize=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]

    def test_add_user(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/user/add", json={
            "username": "new_admin",
            "password": "123456",
            "real_name": "新管理员",
            "role": 2
        }, headers=headers)
        data = response.json()
        assert data["code"] in [200, 400]

class TestRobotModule:
    def test_get_robot_list(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/robot/list", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_robot_statistics(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/robot/statistics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total" in data["data"]
        assert "online" in data["data"]
        assert "offline" in data["data"]

    def test_add_robot(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/robot/add", json={
            "robot_sn": "ROBOT_TEST",
            "robot_name": "测试机器人",
            "area_name": "测试区域",
            "remark": "测试备注"
        }, headers=headers)
        data = response.json()
        assert data["code"] in [200, 400]

class TestPatrolModule:
    def test_get_task_list(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/patrol/task/list?page=1&pageSize=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_task_statistics(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/patrol/task/statistics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_add_task(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/patrol/task/add", json={
            "task_name": "测试巡检任务",
            "robot_sn": "ROBOT_001",
            "cycle_type": 1,
            "start_time": "08:00:00",
            "end_time": "18:00:00"
        }, headers=headers)
        data = response.json()
        assert data["code"] in [200, 400]

class TestAlarmModule:
    def test_get_alarm_list(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/alarm/list?page=1&pageSize=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_get_alarm_statistics(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/alarm/statistics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

class TestReportModule:
    def test_get_daily_report(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/report/daily", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

class TestAiModule:
    def test_ai_chat(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/ai/chat", json={"message": "测试AI对话"}, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "answer" in data["data"]

class TestSysLogModule:
    def test_get_log_list(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/sys/log/list?page=1&pageSize=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200