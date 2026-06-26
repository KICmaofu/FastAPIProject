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
    return int(value)

def validate_max_temp(value):
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
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
    if value is None:
        return 0
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return 1 if value > 0 else 0
    raise ValueError(f'{field_name}必须是布尔值或整数')

def validate_fire_risk(value):
    if value is None:
        return 0
    if isinstance(value, int):
        if value < 0 or value > 3:
            raise ValueError(f'无效的火灾风险等级: {value}')
        return value
    if isinstance(value, str):
        upper_value = value.upper()
        if upper_value not in FIRE_RISK_MAP:
            raise ValueError(f'无效的火灾风险等级: {value}，有效值为: {", ".join(FIRE_RISK_MAP.keys())}')
        return FIRE_RISK_MAP[upper_value]
    raise ValueError('火灾风险等级必须是字符串或数字')

def validate_env_status(value):
    if value is None:
        return '0'
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
    if value is None:
        return 50
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError('电池电量必须是有效的数字')
    if value < 0 or value > 100:
        raise ValueError(f'电池电量超出合理范围: {value}%')
    return round(value)

def validate_robot_sn(value):
    if not value:
        return 'unknown'
    if not isinstance(value, str):
        return str(value)
    return value[:50]

def parse_and_validate_data(raw_data, processing_id):
    import json
    from datetime import datetime
    
    try:
        if isinstance(raw_data, bytes):
            json_string = raw_data.decode('utf-8').strip()
        else:
            json_string = str(raw_data).strip()
        
        json_string = fix_unquoted_enum_values(json_string)
        json_data = json.loads(json_string)
    except Exception as error:
        raise ValueError(f'JSON解析失败: {error}')
    
    robot_sn = json_data.get('robot_sn') or json_data.get('device_id') or json_data.get('deviceId')
    max_temp_field = json_data.get('max_temp') or json_data.get('maxTemp')
    
    max_single_temp = None
    thermal_matrix = None
    
    if max_temp_field:
        if isinstance(max_temp_field, list):
            thermal_matrix = json.dumps(max_temp_field)
            flat_values = [val for row in max_temp_field for val in row if isinstance(val, (int, float))]
            if flat_values:
                max_single_temp = max(flat_values)
        else:
            max_single_temp = float(max_temp_field)
    
    parsed_data = {
        'processingId': processing_id,
        'timestamp': datetime.now().isoformat(),
        'robot_sn': validate_robot_sn(robot_sn),
        'temperature': validate_temperature(json_data.get('temperature')),
        'humidity': validate_humidity(json_data.get('humidity')),
        'smoke_level': validate_smoke_level(json_data.get('smoke_level') or json_data.get('smokeLevel')),
        'max_single_temp': max_single_temp,
        'human_detected': validate_boolean(json_data.get('human_detected') or json_data.get('humanDetected'), 'human_detected'),
        'fire_risk': validate_fire_risk(json_data.get('fire_risk') or json_data.get('fireRisk')),
        'thermal_matrix': thermal_matrix,
        'battery': validate_battery(json_data.get('battery'))
    }
    
    print(f'数据验证通过 [ID: {processing_id}]')
    return parsed_data