import socket
import threading
import json
import gzip
import time
import os
from datetime import datetime
from collections import deque
from dotenv import load_dotenv
import sys
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.models.sensor import PatrolSensorData, PatrolThermalData
from app.models.robot import PatrolRobot
from app.models.alarm import PatrolAlarm

load_dotenv()

PORT = int(os.getenv('SOCKET_PORT', 8888))
HOST = os.getenv('SOCKET_HOST', '0.0.0.0')
SOCKET_TIMEOUT = int(os.getenv('SOCKET_TIMEOUT', 300000))
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', 1000))
BATCH_PROCESSING_ENABLED = os.getenv('BATCH_PROCESSING_ENABLED', 'false').lower() == 'true'
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
COMPRESSION_ENABLED = os.getenv('COMPRESSION_ENABLED', 'false').lower() == 'true'
ERROR_RETRY_LIMIT = int(os.getenv('ERROR_RETRY_LIMIT', 3))
ERROR_RETRY_DELAY = int(os.getenv('ERROR_RETRY_DELAY', 1000))
HEARTBEAT_INTERVAL = int(os.getenv('HEARTBEAT_INTERVAL', 30000))
HEARTBEAT_TIMEOUT = int(os.getenv('HEARTBEAT_TIMEOUT', 90000))

SMOKE_ALARM_THRESHOLD = int(os.getenv('SMOKE_ALARM_THRESHOLD', 50))
FIRE_RISK_ALARM_THRESHOLD = int(os.getenv('FIRE_RISK_ALARM_THRESHOLD', 2))

clients = {}
client_id_counter = 0
client_id_lock = threading.Lock()
server_socket = None

connection_pool = {
    'active_connections': 0,
    'max_connections': MAX_CONNECTIONS,
    'connection_stats': {
        'total_connections': 0,
        'failed_connections': 0,
        'closed_connections': 0,
        'peak_connections': 0
    },
    'lock': threading.Lock()
}

client_batches = {}
client_errors = {}
client_heartbeats = {}

performance_metrics = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'total_data_received': 0,
    'total_data_sent': 0,
    'avg_response_time': 0,
    'response_times': deque(maxlen=100),
    'total_alarms_created': 0,
    'start_time': time.time()
}

METRICS_INTERVAL = 60000

def compress_data(data):
    try:
        if isinstance(data, str):
            data = data.encode('utf-8')
        return gzip.compress(data)
    except Exception as error:
        print(f"Data compression failed: {error}")
        return data

def decompress_data(data):
    try:
        return gzip.decompress(data).decode('utf-8')
    except Exception as error:
        print(f"Data decompression failed: {error}")
        return data.decode('utf-8') if isinstance(data, bytes) else str(data)

def send_heartbeat(client_id, client_data):
    try:
        if client_data and client_data.get('socket'):
            client_data['socket'].sendall(b'PING\n')
            client_heartbeats[client_id] = {
                'last_sent': datetime.now(),
                'last_received': client_heartbeats.get(client_id, {}).get('last_received', datetime.now())
            }
            print(f"Sent heartbeat to client #{client_id}")
    except Exception as error:
        print(f"Failed to send heartbeat to client #{client_id}: {error}")

def check_heartbeat_timeouts():
    now = datetime.now()
    to_remove = []
    for client_id, heartbeat in client_heartbeats.items():
        client_data = clients.get(client_id)
        if client_data and client_data.get('socket'):
            time_since_last_received = (now - heartbeat['last_received']).total_seconds() * 1000
            if time_since_last_received > HEARTBEAT_TIMEOUT:
                print(f"Client #{client_id} heartbeat timeout, disconnecting")
                try:
                    client_data['socket'].close()
                except:
                    pass
                to_remove.append(client_id)
        else:
            to_remove.append(client_id)
    
    for client_id in to_remove:
        client_heartbeats.pop(client_id, None)

def handle_heartbeat_response(client_id):
    if client_id in client_heartbeats:
        client_heartbeats[client_id]['last_received'] = datetime.now()
    else:
        client_heartbeats[client_id] = {'last_sent': datetime.now(), 'last_received': datetime.now()}
    print(f"Received heartbeat response from client #{client_id}")

def record_performance_metrics(start_time, success, data_received, data_sent, alarms_created=0):
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    
    performance_metrics['total_requests'] += 1
    performance_metrics['total_data_received'] += data_received
    performance_metrics['total_data_sent'] += data_sent
    performance_metrics['total_alarms_created'] += alarms_created
    performance_metrics['response_times'].append(response_time)
    
    if success:
        performance_metrics['successful_requests'] += 1
    else:
        performance_metrics['failed_requests'] += 1
    
    if performance_metrics['response_times']:
        performance_metrics['avg_response_time'] = sum(performance_metrics['response_times']) / len(performance_metrics['response_times'])

def log_performance_metrics():
    uptime = int((time.time() - performance_metrics['start_time']))
    requests_per_second = performance_metrics['total_requests'] / uptime if uptime > 0 else 0
    success_rate = (performance_metrics['successful_requests'] / performance_metrics['total_requests']) * 100 if performance_metrics['total_requests'] > 0 else 0
    
    print('=' * 80)
    print('Performance Metrics')
    print('=' * 80)
    print(f"Server uptime: {uptime} seconds")
    print(f"Total requests: {performance_metrics['total_requests']}")
    print(f"Successful requests: {performance_metrics['successful_requests']}")
    print(f"Failed requests: {performance_metrics['failed_requests']}")
    print(f"Success rate: {success_rate:.2f}%")
    print(f"Average response time: {performance_metrics['avg_response_time']:.2f} ms")
    print(f"Total data received: {performance_metrics['total_data_received'] / 1024:.2f} KB")
    print(f"Total data sent: {performance_metrics['total_data_sent'] / 1024:.2f} KB")
    print(f"Total alarms created: {performance_metrics['total_alarms_created']}")
    print(f"Current connections: {connection_pool['active_connections']}")
    print(f"Connection pool usage: {connection_pool['active_connections'] / connection_pool['max_connections'] * 100:.2f}%")
    print(f"Peak connections: {connection_pool['connection_stats']['peak_connections']}")
    print(f"Total connections: {connection_pool['connection_stats']['total_connections']}")
    print(f"Failed connections: {connection_pool['connection_stats']['failed_connections']}")
    print(f"Closed connections: {connection_pool['connection_stats']['closed_connections']}")
    print('=' * 80)

def process_batch(client_id, client_info):
    batch = client_batches.get(client_id, [])
    if not batch:
        return
    print(f"Processing batch data for client #{client_id}, total {len(batch)} items")
    for item in batch:
        handle_client_data_direct(item['socket'], client_id, client_info, item['data'])
    client_batches.pop(client_id, None)

def handle_client_data_direct(sock, client_id, client_info, data, retry_count=0):
    start_time = time.time()
    data_received = len(data) if isinstance(data, bytes) else len(str(data))
    data_sent = 0
    success = False
    alarms_created = 0
    
    try:
        print(f"Processing data for client #{client_id}, retry count: {retry_count}")
        result = process_raw_data(data, client_info)
        
        if result['success']:
            alarms_created = result.get('alarms_created', 0)
            response = f"Data processed successfully [ID: {result['processingId']}, Alarms: {alarms_created}]\n"
            if COMPRESSION_ENABLED:
                compressed_response = compress_data(response)
                sock.sendall(compressed_response)
                data_sent = len(compressed_response)
            else:
                sock.sendall(response.encode('utf-8'))
                data_sent = len(response)
            client_errors.pop(client_id, None)
            success = True
        else:
            response = f"Data processing failed: {result['error']}\n"
            if COMPRESSION_ENABLED:
                compressed_response = compress_data(response)
                sock.sendall(compressed_response)
                data_sent = len(compressed_response)
            else:
                sock.sendall(response.encode('utf-8'))
                data_sent = len(response)
    except Exception as error:
        print(f"Error processing data for client #{client_id}: {error}")
        
        error_count = client_errors.get(client_id, 0) + 1
        client_errors[client_id] = error_count
        
        if error_count <= ERROR_RETRY_LIMIT:
            print(f"Will retry processing data for client #{client_id}, attempt {error_count}")
            time.sleep(ERROR_RETRY_DELAY * error_count / 1000)
            handle_client_data_direct(sock, client_id, client_info, data, error_count)
            return
        else:
            print(f"Data processing failed for client #{client_id}, max retries reached")
            response = f"Server error: {error} (max retries reached)\n"
            if COMPRESSION_ENABLED:
                compressed_response = compress_data(response)
                sock.sendall(compressed_response)
                data_sent = len(compressed_response)
            else:
                sock.sendall(response.encode('utf-8'))
                data_sent = len(response)
            client_errors.pop(client_id, None)
    finally:
        record_performance_metrics(start_time, success, data_received, data_sent, alarms_created)

def get_client_info(sock):
    try:
        remote_address = sock.getpeername()
        return f"{remote_address[0]}:{remote_address[1]}"
    except:
        return "unknown"

def handle_client_data(sock, client_id, client_info, data):
    try:
        processed_data = data
        
        if isinstance(data, bytes) and COMPRESSION_ENABLED:
            processed_data = decompress_data(data)
            print(f"Decompressed data, original size: {len(data)}, decompressed: {len(processed_data)}")
        
        if isinstance(processed_data, bytes):
            trimmed_data = processed_data.decode('utf-8').strip()
        else:
            trimmed_data = str(processed_data).strip()
        
        if trimmed_data == 'PONG':
            handle_heartbeat_response(client_id)
            return
        
        if BATCH_PROCESSING_ENABLED:
            if client_id not in client_batches:
                client_batches[client_id] = []
            
            batch = client_batches[client_id]
            batch.append({'socket': sock, 'data': processed_data})
            
            if len(batch) >= BATCH_SIZE:
                process_batch(client_id, client_info)
        else:
            handle_client_data_direct(sock, client_id, client_info, processed_data)
    except Exception as error:
        print(f"Error handling data for client #{client_id}: {error}")
        response = f"Server error: {error}\n"
        if COMPRESSION_ENABLED:
            compressed_response = compress_data(response)
            sock.sendall(compressed_response)
        else:
            sock.sendall(response.encode('utf-8'))

def cleanup_client(client_id, client_info, had_error=False):
    client_data = clients.get(client_id)
    if client_data:
        with connection_pool['lock']:
            connection_pool['active_connections'] -= 1
            connection_pool['connection_stats']['closed_connections'] += 1
            if connection_pool['active_connections'] < 0:
                connection_pool['active_connections'] = 0
        
        clients.pop(client_id, None)
        
        if BATCH_PROCESSING_ENABLED and client_id in client_batches:
            process_batch(client_id, client_info)
        
        client_errors.pop(client_id, None)
        client_heartbeats.pop(client_id, None)
        
        if client_data.get('connected_at'):
            connection_duration = (datetime.now() - client_data['connected_at']).total_seconds()
            print(f"Client #{client_id} connection cleaned up, duration: {connection_duration:.2f}s")

def handle_client_disconnect(client_id, client_info, had_error=False):
    if had_error:
        print(f"Client #{client_id} ({client_info}) disconnected abnormally")
    else:
        print(f"Client #{client_id} ({client_info}) disconnected normally")

def handle_client_error(client_id, client_info, error):
    print(f"Client #{client_id} ({client_info}) connection error: {error}")
    if hasattr(error, 'errno'):
        if error.errno == 104:
            print("Connection reset by peer")
        elif error.errno == 110:
            print("Connection timed out")
        elif error.errno == 32:
            print("Broken pipe, client may have closed connection")

def get_timestamp_string():
    return datetime.now().isoformat().replace(':', '-').replace('.', '-')

def determine_alarm_level(fire_risk, smoke_level):
    if fire_risk >= 3 or smoke_level > 100:
        return "RED"
    elif fire_risk >= 2 or smoke_level > SMOKE_ALARM_THRESHOLD:
        return "ORANGE"
    return "NORMAL"

def determine_alarm_type(fire_risk, smoke_level, human_detected):
    if smoke_level > SMOKE_ALARM_THRESHOLD:
        return "SMOKE"
    elif fire_risk >= 2:
        if human_detected:
            return "HIGH_TEMP"
        else:
            return "NO_HUMAN"
    return "HIGH_TEMP"

def determine_hardware_alarm_type(fire_risk):
    if fire_risk == 0:
        return 0
    elif fire_risk == 1:
        return 1
    elif fire_risk == 2:
        return 2
    elif fire_risk >= 3:
        return 3
    return 0

def should_create_alarm(fire_risk, smoke_level):
    return fire_risk >= FIRE_RISK_ALARM_THRESHOLD or smoke_level > SMOKE_ALARM_THRESHOLD

def process_raw_data(raw_data, client_info):
    processing_id = get_timestamp_string()
    
    print(f"Received client data: {client_info}")
    print(f"Raw data: {raw_data}")
    
    try:
        if isinstance(raw_data, bytes):
            json_string = raw_data.decode('utf-8').strip()
        else:
            json_string = str(raw_data).strip()
        
        start_index = -1
        for i, char in enumerate(json_string):
            if char in '{[':
                start_index = i
                break
        
        if start_index == -1:
            json_data = json.loads(json_string)
        else:
            json_string = json_string[start_index:]
            is_array = json_string[0] == '['
            open_char = '[' if is_array else '{'
            close_char = ']' if is_array else '}'
            
            bracket_count = 0
            in_string = False
            escape_next = False
            end_index = -1
            
            for i, char in enumerate(json_string):
                if escape_next:
                    escape_next = False
                    continue
                
                if char == '\\':
                    escape_next = True
                    continue
                
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                
                if not in_string:
                    if char == open_char:
                        bracket_count += 1
                    elif char == close_char:
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_index = i + 1
                            break
            
            if end_index > 0 and end_index < len(json_string):
                json_string = json_string[:end_index]
            
            json_data = json.loads(json_string)
        
        robot_sn = json_data.get('robot_sn') or json_data.get('device_id') or json_data.get('deviceId') or 'unknown'
        
        max_single_temp = None
        thermal_matrix = None
        
        max_temp_field = json_data.get('max_temp')
        if max_temp_field:
            if isinstance(max_temp_field, list):
                thermal_matrix = json.dumps(max_temp_field)
                flat_values = [val for row in max_temp_field for val in max_temp_field if isinstance(val, (int, float))]
                if flat_values:
                    max_single_temp = max(flat_values)
            else:
                max_single_temp = float(max_temp_field)
        
        parsed_data = {
            'processingId': processing_id,
            'timestamp': datetime.now().isoformat(),
            'robot_sn': robot_sn,
            'temperature': json_data.get('temperature'),
            'humidity': json_data.get('humidity'),
            'smoke_level': json_data.get('smoke_level') or json_data.get('smokeLevel') or 0,
            'max_single_temp': max_single_temp,
            'human_detected': json_data.get('human_detected') or json_data.get('humanDetected') or 0,
            'fire_risk': json_data.get('fire_risk') or json_data.get('fireRisk') or 0,
            'thermal_matrix': thermal_matrix,
            'battery': json_data.get('battery')
        }
        
        alarms_created = save_to_database(parsed_data, processing_id)
        
        return {'success': True, 'processingId': processing_id, 'data': parsed_data, 'alarms_created': alarms_created}
    except Exception as error:
        print(f"Data processing failed [ID: {processing_id}]: {error}")
        traceback.print_exc()
        return {'success': False, 'processingId': processing_id, 'error': str(error)}

def save_to_database(parsed_data, processing_id):
    retry_count = 0
    max_retries = 3
    alarms_created = 0
    
    while retry_count < max_retries:
        try:
            db = SessionLocal()
            try:
                robot_sn = parsed_data['robot_sn'][:50]
                
                existing_robot = db.query(PatrolRobot).filter(PatrolRobot.robot_sn == robot_sn).first()
                if not existing_robot:
                    print(f"Robot {robot_sn} not found, creating new robot")
                    new_robot = PatrolRobot(
                        robot_sn=robot_sn,
                        robot_name=f"Robot {robot_sn}",
                        online_status=1,
                        battery=parsed_data.get('battery', 50),
                        run_mode=0,
                        firmware_version="Unknown",
                        last_upload_time=datetime.now()
                    )
                    db.add(new_robot)
                    db.flush()
                    print(f"Created new robot: {robot_sn}")
                else:
                    existing_robot.online_status = 1
                    existing_robot.battery = parsed_data.get('battery', existing_robot.battery)
                    existing_robot.last_upload_time = datetime.now()
                
                sensor_data = PatrolSensorData(
                    robot_sn=robot_sn,
                    patrol_record_id=None,
                    temperature=parsed_data.get('temperature', 0),
                    humidity=parsed_data.get('humidity', 0),
                    smoke_level=int(parsed_data.get('smoke_level', 0)),
                    max_single_temp=parsed_data.get('max_single_temp'),
                    human_detected=int(parsed_data.get('human_detected', 0)),
                    fire_risk=int(parsed_data.get('fire_risk', 0)),
                    thermal_matrix=parsed_data.get('thermal_matrix'),
                    battery=parsed_data.get('battery'),
                    collect_time=datetime.now()
                )
                
                db.add(sensor_data)
                db.flush()
                
                if parsed_data.get('thermal_matrix'):
                    thermal_data = PatrolThermalData(
                        robot_sn=robot_sn,
                        patrol_record_id=None,
                        thermal_image=None,
                        thermal_matrix=parsed_data.get('thermal_matrix'),
                        max_temp=parsed_data.get('max_single_temp'),
                        avg_temp=None,
                        min_temp=None,
                        collect_time=datetime.now()
                    )
                    db.add(thermal_data)
                
                fire_risk = int(parsed_data.get('fire_risk', 0))
                smoke_level = int(parsed_data.get('smoke_level', 0))
                
                if should_create_alarm(fire_risk, smoke_level):
                    alarm_level = determine_alarm_level(fire_risk, smoke_level)
                    alarm_type = determine_alarm_type(fire_risk, smoke_level, parsed_data.get('human_detected', 0))
                    hardware_alarm_type = determine_hardware_alarm_type(fire_risk)
                    
                    alarm_desc = f"检测到异常 - 火灾风险等级: {fire_risk}, 烟雾浓度: {smoke_level}"
                    
                    alarm = PatrolAlarm(
                        robot_sn=robot_sn,
                        sensor_record_id=sensor_data.id,
                        hardware_alarm_type=hardware_alarm_type,
                        alarm_type=alarm_type,
                        alarm_level=alarm_level,
                        alarm_desc=alarm_desc,
                        area_name="未知区域",
                        point_name="未知点位",
                        deal_status=0
                    )
                    
                    db.add(alarm)
                    alarms_created += 1
                    print(f"Alarm created for robot {robot_sn} [ID: {processing_id}]")
                
                db.commit()
                print(f"Data saved to database [ID: {processing_id}, Alarms: {alarms_created}]")
                return alarms_created
            finally:
                db.close()
        except Exception as error:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed to save to database (after {max_retries} retries): {error}")
                raise error
            print(f"Failed to save to database, retry {retry_count}: {error}")
            time.sleep(retry_count)

def handle_client_connection(sock, addr):
    global client_id_counter
    
    with connection_pool['lock']:
        connection_pool['connection_stats']['total_connections'] += 1
        
        if connection_pool['active_connections'] >= connection_pool['max_connections']:
            print("Connection pool full, rejecting new connection")
            try:
                sock.sendall('Server connection limit reached, please try again later\n'.encode('utf-8'))
                sock.close()
            except:
                pass
            connection_pool['connection_stats']['failed_connections'] += 1
            return
        
        connection_pool['active_connections'] += 1
        if connection_pool['active_connections'] > connection_pool['connection_stats']['peak_connections']:
            connection_pool['connection_stats']['peak_connections'] = connection_pool['active_connections']
    
    with client_id_lock:
        client_id_counter += 1
        client_id = client_id_counter
    
    client_info = get_client_info(sock)
    
    client_data = {
        'socket': sock,
        'client_id': client_id,
        'client_info': client_info,
        'connected_at': datetime.now(),
        'last_activity': datetime.now(),
        'data_received': 0,
        'data_sent': 0
    }
    
    clients[client_id] = client_data
    
    try:
        sock.settimeout(SOCKET_TIMEOUT / 1000)
        
        print(f"Client #{client_id} connected - {client_info}")
        print(f"Current connections: {connection_pool['active_connections']}")
        
        welcome_message = (
            f"Welcome to Fire Patrol Sensor Data Server!\n"
            f"Your client ID: {client_id}\n"
            f"Current connections: {connection_pool['active_connections']}\n"
            f"Max connections: {connection_pool['max_connections']}\n"
            f"Please send sensor data in JSON format\n\n"
        )
        sock.sendall(welcome_message.encode('utf-8'))
        client_data['data_sent'] += len(welcome_message)
        
        buffer = b''
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                
                buffer += data
                client_data['data_received'] += len(data)
                client_data['last_activity'] = datetime.now()
                
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line.strip():
                        handle_client_data(sock, client_id, client_info, line)
            except socket.timeout:
                print(f"Client #{client_id} connection timeout")
                break
            except Exception as error:
                handle_client_error(client_id, client_info, error)
                break
    except Exception as error:
        print(f"Error handling client #{client_id} connection: {error}")
    finally:
        handle_client_disconnect(client_id, client_info)
        cleanup_client(client_id, client_info)
        try:
            sock.close()
        except:
            pass

def start_server(background=False):
    global server_socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket = server
    
    try:
        server.bind((HOST, PORT))
        server.listen(MAX_CONNECTIONS)
        server.settimeout(None)
        
        print('=' * 60)
        print('Fire Patrol Sensor Data Server Started')
        print(f"Listening on: {HOST}:{PORT}")
        print('Waiting for client connections...')
        print('=' * 60)
        
        def heartbeat_thread():
            while True:
                time.sleep(HEARTBEAT_INTERVAL / 1000)
                for client_id, client_data in list(clients.items()):
                    send_heartbeat(client_id, client_data)
        
        def heartbeat_check_thread():
            while True:
                time.sleep(HEARTBEAT_INTERVAL * 2 / 1000)
                check_heartbeat_timeouts()
        
        def metrics_thread():
            while True:
                time.sleep(METRICS_INTERVAL / 1000)
                log_performance_metrics()
        
        def accept_thread():
            while True:
                try:
                    sock, addr = server.accept()
                    threading.Thread(target=handle_client_connection, args=(sock, addr), daemon=True).start()
                except Exception as error:
                    print(f"Error accepting connection: {error}")
                    break
        
        threading.Thread(target=heartbeat_thread, daemon=True).start()
        threading.Thread(target=heartbeat_check_thread, daemon=True).start()
        threading.Thread(target=metrics_thread, daemon=True).start()
        threading.Thread(target=accept_thread, daemon=True).start()
        
        print(f"Heartbeat mechanism started, interval: {HEARTBEAT_INTERVAL}ms, timeout: {HEARTBEAT_TIMEOUT}ms")
        print(f"Performance monitoring started, interval: {METRICS_INTERVAL}ms")
        print(f"Alarm thresholds - Fire Risk: >= {FIRE_RISK_ALARM_THRESHOLD}, Smoke: > {SMOKE_ALARM_THRESHOLD}")
        
        if background:
            return server
        else:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nReceived exit signal, shutting down server...")
                shutdown_server(server)
    except Exception as error:
        print(f"Server startup failed: {error}")
        if hasattr(error, 'errno'):
            if error.errno == 98:
                print(f"Port {PORT} is already in use")
            elif error.errno == 13:
                print(f"Permission denied, cannot bind to port {PORT}")
        return None

def shutdown_server(server):
    print("Closing all client connections...")
    for client_id, client_data in list(clients.items()):
        try:
            client_data['socket'].sendall('Server is shutting down, goodbye!\n'.encode('utf-8'))
            client_data['socket'].close()
        except:
            pass
    clients.clear()
    server.close()
    print("Server closed")

if __name__ == "__main__":
    start_server()