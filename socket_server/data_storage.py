import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

def is_abnormal_data(parsed_data):
    if not parsed_data:
        return False
    
    fire_risk = parsed_data.get('fireRisk')
    if fire_risk in (2, 3):
        return True
    
    env_status = parsed_data.get('envStatus')
    if env_status in ('2', '3', 2, 3):
        return True
    
    return False

def ensure_dirs():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def save_raw_data(raw_data, processing_id, client_info, parsed_data=None):
    if not parsed_data or not is_abnormal_data(parsed_data):
        return
    
    ensure_dirs()
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    raw_file_path = os.path.join(RAW_DATA_DIR, f'{date_str}.json')
    
    raw_record = {
        'processingId': processing_id,
        'timestamp': datetime.now().isoformat(),
        'clientInfo': client_info,
        'rawData': raw_data.decode('utf-8') if isinstance(raw_data, bytes) else str(raw_data),
        'dataSize': len(raw_data) if isinstance(raw_data, bytes) else len(str(raw_data)),
        'abnormalType': 'FIRE_RISK' if parsed_data['fireRisk'] >= 2 else 'ENV_STATUS'
    }
    
    existing_data = []
    if os.path.exists(raw_file_path):
        try:
            with open(raw_file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = []
        except Exception as error:
            print(f'警告: 读取现有原始数据文件失败: {error}')
            existing_data = []
    
    existing_data.append(raw_record)
    
    with open(raw_file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f'警告: 异常原始数据已保存到: {raw_file_path}')

def save_processed_data(processed_data, processing_id):
    if not is_abnormal_data(processed_data):
        return
    
    ensure_dirs()
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    processed_file_path = os.path.join(PROCESSED_DATA_DIR, f'{date_str}.json')
    
    processed_record = {
        'processingId': processing_id,
        'timestamp': datetime.now().isoformat(),
        'data': processed_data,
        'abnormalType': 'FIRE_RISK' if processed_data['fireRisk'] >= 2 else 'ENV_STATUS'
    }
    
    existing_data = []
    if os.path.exists(processed_file_path):
        try:
            with open(processed_file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            if not isinstance(existing_data, list):
                existing_data = []
        except Exception as error:
            print(f'警告: 读取现有处理数据文件失败: {error}')
            existing_data = []
    
    existing_data.append(processed_record)
    
    with open(processed_file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
    
    print(f'警告: 异常处理数据已保存到: {processed_file_path}')