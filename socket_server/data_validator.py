FIRE_RISK_MAP = {
    'LOW': 0,
    'MEDIUM': 1,
    'HIGH': 2,
    'CRITICAL': 3
}

ENV_STATUS_MAP = {
    'NORMAL': 0,
    'WARNING': 1,
    'ALERT': 2,
    'EMERGENCY': 3
}

def fix_unquoted_enum_values(json_string):
    fixed = json_string
    fire_risk_values = '|'.join(FIRE_RISK_MAP.keys())
    env_status_values = '|'.join(ENV_STATUS_MAP.keys())
    
    import re
    fire_risk_regex = re.compile(r'"fire_risk":\s*(' + fire_risk_values + r')', re.IGNORECASE)
    fixed = fire_risk_regex.sub(r'"fire_risk":"\1"', fixed)
    
    env_status_regex = re.compile(r'"env_status":\s*(' + env_status_values + r')', re.IGNORECASE)
    fixed = env_status_regex.sub(r'"env_status":"\1"', fixed)
    
    return fixed

def validate_temperature(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError('温度必须是有效的数字')
    if value < -40 or value > 130:
        raise ValueError(f'温度值超出合理范围: {value}°C')
    return round(float(value), 2)

def validate_humidity(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError('湿度必须是有效的数字')
    if value < 0 or value > 100:
        raise ValueError(f'湿度值超出合理范围: {value}%')
    return round(float(value), 2)

def validate_smoke_level(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError('烟雾浓度必须是有效的数字')
    if value < 0 or value > 10000.00:
        raise ValueError(f'烟雾浓度值超出合理范围: {value}')
    return round(float(value), 2)

def validate_max_temp(value):
    if not isinstance(value, list):
        raise ValueError('最高温度数组格式错误')
    if len(value) != 8:
        raise ValueError(f'最高温度数组长度错误: {len(value)}，应为8')
    
    for i, row in enumerate(value):
        if not isinstance(row, list) or len(row) != 8:
            raise ValueError(f'最高温度数组第{i}行格式错误')
        for j, val in enumerate(row):
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise ValueError(f'最高温度数组[{i}][{j}]必须是有效的数字')
            if val < -100 or val > 200:
                print(f'警告: 最高温度数组[{i}][{j}]超出正常范围: {val}°C')
    
    return value

def validate_boolean(value, field_name):
    if not isinstance(value, bool):
        raise ValueError(f'{field_name}必须是布尔值')
    return value

def validate_fire_risk(value):
    if isinstance(value, int):
        if value not in FIRE_RISK_MAP.values():
            raise ValueError(f'无效的火灾风险等级: {value}')
        return value
    if isinstance(value, str):
        upper_value = value.upper()
        if upper_value not in FIRE_RISK_MAP:
            raise ValueError(f'无效的火灾风险等级: {value}，有效值为: {", ".join(FIRE_RISK_MAP.keys())}')
        return FIRE_RISK_MAP[upper_value]
    raise ValueError('火灾风险等级必须是字符串或数字')

def validate_env_status(value):
    if isinstance(value, (int, float)):
        return str(round(float(value), 2))
    if isinstance(value, str):
        num_value = None
        try:
            num_value = float(value)
            return str(round(num_value, 2))
        except ValueError:
            pass
        
        upper_value = value.upper()
        if upper_value not in ENV_STATUS_MAP:
            raise ValueError(f'无效的环境状态: {value}，有效值为: {", ".join(ENV_STATUS_MAP.keys())}')
        return str(ENV_STATUS_MAP[upper_value])
    raise ValueError('环境状态必须是字符串或数字')

def validate_battery(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError('电池电量必须是有效的数字')
    if value < 0 or value > 100:
        raise ValueError(f'电池电量超出合理范围: {value}%')
    return round(value)

def validate_device_id(value):
    if not value:
        return 'unknown'
    if not isinstance(value, str):
        return str(value)
    return value[:50]

def parse_and_validate_data(raw_data, processing_id):
    import json
    
    try:
        if isinstance(raw_data, bytes):
            json_string = raw_data.decode('utf-8').strip()
        else:
            json_string = str(raw_data).strip()
        
        json_string = fix_unquoted_enum_values(json_string)
        json_data = json.loads(json_string)
    except Exception as error:
        raise ValueError(f'JSON解析失败: {error}')
    
    if not json_data.get('type'):
        raise ValueError('缺少数据类型')
    
    if 'sensor_data' not in json_data.get('type', '').lower():
        print(f'警告: 未知的数据类型: {json_data.get("type")}')
    
    parsed_data = {
        'processingId': processing_id,
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'deviceId': validate_device_id(json_data.get('device_id') or json_data.get('deviceId')),
        'temperature': validate_temperature(json_data.get('temperature')),
        'humidity': validate_humidity(json_data.get('humidity')),
        'smokeLevel': validate_smoke_level(json_data.get('smoke_level')),
        'maxTemp': validate_max_temp(json_data.get('max_temp')),
        'humanDetected': validate_boolean(json_data.get('human_detected'), 'human_detected'),
        'fireRisk': validate_fire_risk(json_data.get('fire_risk')),
        'envStatus': validate_env_status(json_data.get('env_status')),
        'battery': validate_battery(json_data.get('battery'))
    }
    
    print(f'数据验证通过 [ID: {processing_id}]')
    return parsed_data