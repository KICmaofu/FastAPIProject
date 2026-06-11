import socket
import json
import time
import random
from datetime import datetime

# Socket服务器配置
SOCKET_HOST = 'localhost'
SOCKET_PORT = 8888

def generate_sensor_data(device_id):
    """生成模拟传感器数据"""
    # 生成8x8的温度矩阵
    max_temp_matrix = []
    base_temp = random.uniform(20, 40)
    for i in range(8):
        row = []
        for j in range(8):
            temp = base_temp + random.uniform(-5, 5)
            row.append(round(temp, 2))
        max_temp_matrix.append(row)
    
    # 生成传感器数据
    data = {
        'device_id': device_id,
        'temperature': round(random.uniform(18, 35), 2),
        'humidity': round(random.uniform(40, 80), 2),
        'smoke_level': round(random.uniform(0, 500), 2),
        'max_temp': max_temp_matrix,
        'human_detected': random.choice([True, False]),
        'fire_risk': random.choice([0, 1, 2, 3]),
        'env_status': random.choice(['0', '1', '2', '3']),
        'battery': round(random.uniform(20, 100), 1)
    }
    return data

def send_socket_data(data):
    """通过socket发送数据"""
    try:
        # 创建socket连接
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SOCKET_HOST, SOCKET_PORT))
        
        # 将数据转换为JSON字符串并添加换行符
        json_data = json.dumps(data, ensure_ascii=False) + '\n'
        
        # 发送数据
        client_socket.sendall(json_data.encode('utf-8'))
        
        # 接收响应
        response = client_socket.recv(1024).decode('utf-8')
        
        # 关闭连接
        client_socket.close()
        
        return True, response
    except Exception as e:
        return False, str(e)

def main():
    print(f"开始发送200条socket模拟数据到 {SOCKET_HOST}:{SOCKET_PORT}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(1, 201):
        device_id = f"device_{i:03d}"
        sensor_data = generate_sensor_data(device_id)
        
        print(f"[{i}/200] 发送数据 - 设备ID: {device_id}, 温度: {sensor_data['temperature']}°C, 湿度: {sensor_data['humidity']}%")
        
        success, response = send_socket_data(sensor_data)
        
        if success:
            success_count += 1
            print(f"  ✓ 成功: {response.strip()}")
        else:
            fail_count += 1
            print(f"  ✗ 失败: {response}")
        
        # 添加小延迟避免发送过快
        time.sleep(0.1)
    
    print("=" * 60)
    print(f"发送完成！成功: {success_count}, 失败: {fail_count}")

if __name__ == "__main__":
    main()