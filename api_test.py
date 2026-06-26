import requests

BASE_URL = "http://localhost:8000"

# 注册用户
r = requests.post(f"{BASE_URL}/api/user/register", json={
    "username": "testuser002",
    "password": "Test@123456",
    "real_name": "测试用户2",
    "phone": "13800000002"
})
print("Register:", r.json())

# 登录获取Token
r = requests.post(f"{BASE_URL}/api/user/login", json={
    "username": "testuser002",
    "password": "Test@123456"
})
data = r.json()
print("Login:", data)
token = data.get('data', {}).get('token')
print("Token:", token)

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试机器人列表
    r = requests.get(f"{BASE_URL}/api/robot/list", headers=headers)
    print("\nRobot List Response:")
    print("Status:", r.status_code)
    print("Data:", r.text[:1000])
    
    # 测试传感器数据列表
    r = requests.get(f"{BASE_URL}/api/sensor/data/list", headers=headers)
    print("\nSensor Data List Response:")
    print("Status:", r.status_code)
    print("Data:", r.text[:1000])
    
    # 测试报警列表
    r = requests.get(f"{BASE_URL}/api/alarm/list", headers=headers)
    print("\nAlarm List Response:")
    print("Status:", r.status_code)
    print("Data:", r.text[:1000])
else:
    print("Failed to get token")