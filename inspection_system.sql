-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `inspection_system` 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE `inspection_system`;

-- ------------------------------
-- 1. 用户表
-- ------------------------------
CREATE TABLE `t_user` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `username` VARCHAR(50) NOT NULL COMMENT '用户名',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '加密密码',
  `role` ENUM('admin','operator','viewer') NOT NULL COMMENT '角色',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除标志 0未删 1已删',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_role` (`role`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ------------------------------
-- 2. 设备表
-- ------------------------------
CREATE TABLE `t_device` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `name` VARCHAR(100) NOT NULL COMMENT '设备名称',
  `type` ENUM('robot','sensor','gateway','other') NOT NULL COMMENT '设备类型',
  `model` VARCHAR(50) DEFAULT NULL COMMENT '型号',
  `status` ENUM('online','offline','warning') NOT NULL DEFAULT 'offline' COMMENT '状态',
  `location` VARCHAR(200) DEFAULT NULL COMMENT '位置描述',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- ------------------------------
-- 3. 机器人表
-- ------------------------------
CREATE TABLE `t_robot` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `name` VARCHAR(100) NOT NULL COMMENT '机器人名称',
  `model` VARCHAR(50) NOT NULL COMMENT '型号',
  `battery` DECIMAL(5,1) NOT NULL DEFAULT 0 COMMENT '当前电量(%)',
  `status` ENUM('idle','moving','charging','offline') NOT NULL DEFAULT 'idle' COMMENT '状态',
  `location` VARCHAR(200) DEFAULT NULL COMMENT '部署位置描述',
  `speed` DECIMAL(5,2) DEFAULT 0.00 COMMENT '当前速度(m/s)',
  `last_online_time` DATETIME DEFAULT NULL COMMENT '最后在线时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_battery` (`battery`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机器人表';

-- ------------------------------
-- 4. 传感器表
-- ------------------------------
CREATE TABLE `t_sensor` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `name` VARCHAR(100) NOT NULL COMMENT '传感器名称',
  `type` ENUM('temperature','humidity','gas','pm25','thermal') NOT NULL COMMENT '类型',
  `unit` VARCHAR(20) NOT NULL COMMENT '单位',
  `status` ENUM('normal','warning','danger') NOT NULL DEFAULT 'normal' COMMENT '状态',
  `device_id` VARCHAR(32) DEFAULT NULL COMMENT '所属设备ID',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type`),
  KEY `idx_device_id` (`device_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_sensor_device` FOREIGN KEY (`device_id`) REFERENCES `t_device` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器表';

-- ------------------------------
-- 5. 传感器数据表（核心数据表，由机器人上报）
-- ------------------------------
CREATE TABLE `t_sensor_data` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `robot_id` VARCHAR(32) NOT NULL COMMENT '机器人ID',
  `temperature` DECIMAL(5,2) NOT NULL COMMENT '温度(°C)',
  `humidity` DECIMAL(5,2) NOT NULL COMMENT '湿度(%)',
  `smoke_level` DECIMAL(5,2) NOT NULL COMMENT '烟雾浓度(ppm)',
  `battery` DECIMAL(5,1) DEFAULT NULL COMMENT '机器人电量',
  `human_detected` TINYINT NOT NULL DEFAULT 0 COMMENT '是否检测到人(0/1)',
  `fire_risk` TINYINT NOT NULL DEFAULT 0 COMMENT '火灾风险等级(0-3)',
  `env_status` VARCHAR(50) DEFAULT NULL COMMENT '环境状态描述',
  `raw_json` JSON DEFAULT NULL COMMENT '原始JSON数据',
  `receive_time` DATETIME NOT NULL COMMENT '接收时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_robot_id` (`robot_id`),
  KEY `idx_receive_time` (`receive_time`),
  KEY `idx_human_detected` (`human_detected`),
  KEY `idx_fire_risk` (`fire_risk`),
  CONSTRAINT `fk_sensor_data_robot` FOREIGN KEY (`robot_id`) REFERENCES `t_robot` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='传感器数据表（机器人上报）';

-- ------------------------------
-- 6. 热成像数据表（与传感器数据一一对应）
-- ------------------------------
CREATE TABLE `t_thermal_data` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `sensor_data_id` BIGINT NOT NULL COMMENT '关联传感器数据ID',
  `max_temp_matrix` JSON NOT NULL COMMENT '8×8温度矩阵',
  `max_temp_value` DECIMAL(6,2) DEFAULT NULL COMMENT '矩阵中最大温度',
  `min_temp_value` DECIMAL(6,2) DEFAULT NULL COMMENT '矩阵中最小温度',
  `avg_temp_value` DECIMAL(6,2) DEFAULT NULL COMMENT '矩阵平均温度',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_sensor_data_id` (`sensor_data_id`),
  CONSTRAINT `fk_thermal_sensor_data` FOREIGN KEY (`sensor_data_id`) REFERENCES `t_sensor_data` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热成像数据表';

-- ------------------------------
-- 7. 机器人位置历史表
-- ------------------------------
CREATE TABLE `t_robot_position_history` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `robot_id` VARCHAR(32) NOT NULL COMMENT '机器人ID',
  `x` DECIMAL(10,2) NOT NULL COMMENT 'X坐标',
  `y` DECIMAL(10,2) NOT NULL COMMENT 'Y坐标',
  `battery` DECIMAL(5,1) DEFAULT NULL COMMENT '记录时的电量',
  `speed` DECIMAL(5,2) DEFAULT NULL COMMENT '记录时的速度',
  `record_time` DATETIME NOT NULL COMMENT '记录时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_robot_id` (`robot_id`),
  KEY `idx_robot_time` (`robot_id`, `record_time`),
  KEY `idx_record_time` (`record_time`),
  CONSTRAINT `fk_position_robot` FOREIGN KEY (`robot_id`) REFERENCES `t_robot` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机器人位置历史表';

-- ------------------------------
-- 8. 环境数据汇总表（按时间间隔聚合）
-- ------------------------------
CREATE TABLE `t_environment_data` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `record_time` DATETIME NOT NULL COMMENT '记录时间（聚合起点）',
  `temperature` DECIMAL(5,2) DEFAULT NULL COMMENT '平均温度',
  `humidity` DECIMAL(5,2) DEFAULT NULL COMMENT '平均湿度',
  `gas` DECIMAL(5,2) DEFAULT NULL COMMENT '可燃气体浓度',
  `pm25` DECIMAL(5,2) DEFAULT NULL COMMENT 'PM2.5',
  `max_thermal_temp` DECIMAL(6,2) DEFAULT NULL COMMENT '热成像最高温度',
  `data_interval` VARCHAR(10) NOT NULL DEFAULT '1m' COMMENT '聚合间隔(1m/5m/1h)',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_record_time` (`record_time`),
  KEY `idx_interval_time` (`data_interval`, `record_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='环境数据汇总表';

-- ------------------------------
-- 9. 告警表
-- ------------------------------
CREATE TABLE `t_alert` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `type` VARCHAR(50) NOT NULL COMMENT '告警类型(高温/烟雾/火灾/异常)',
  `level` ENUM('warning','danger','critical') NOT NULL COMMENT '级别',
  `message` VARCHAR(500) NOT NULL COMMENT '告警消息',
  `device_id` VARCHAR(32) DEFAULT NULL COMMENT '关联设备ID',
  `robot_id` VARCHAR(32) DEFAULT NULL COMMENT '关联机器人ID',
  `sensor_data_id` BIGINT DEFAULT NULL COMMENT '触发告警的传感器数据ID',
  `status` ENUM('pending','confirmed','ignored') NOT NULL DEFAULT 'pending' COMMENT '处理状态',
  `process_remark` VARCHAR(500) DEFAULT NULL COMMENT '处理备注',
  `process_user_id` VARCHAR(32) DEFAULT NULL COMMENT '处理人ID',
  `process_time` DATETIME DEFAULT NULL COMMENT '处理时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '告警发生时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_level` (`level`),
  KEY `idx_status` (`status`),
  KEY `idx_type` (`type`),
  KEY `idx_device_id` (`device_id`),
  KEY `idx_robot_id` (`robot_id`),
  KEY `idx_sensor_data_id` (`sensor_data_id`),
  KEY `idx_create_time` (`create_time`),
  CONSTRAINT `fk_alert_device` FOREIGN KEY (`device_id`) REFERENCES `t_device` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_alert_robot` FOREIGN KEY (`robot_id`) REFERENCES `t_robot` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_alert_sensor_data` FOREIGN KEY (`sensor_data_id`) REFERENCES `t_sensor_data` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_alert_process_user` FOREIGN KEY (`process_user_id`) REFERENCES `t_user` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警表';

-- ------------------------------
-- 10. 消息表
-- ------------------------------
CREATE TABLE `t_message` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `title` VARCHAR(200) NOT NULL COMMENT '标题',
  `content` TEXT DEFAULT NULL COMMENT '内容',
  `type` VARCHAR(50) DEFAULT NULL COMMENT '消息类型',
  `receiver_id` VARCHAR(32) NOT NULL COMMENT '接收用户ID（0为全部）',
  `is_read` TINYINT NOT NULL DEFAULT 0 COMMENT '0未读 1已读',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
  PRIMARY KEY (`id`),
  KEY `idx_receiver_read` (`receiver_id`, `is_read`),
  KEY `idx_type` (`type`),
  KEY `idx_create_time` (`create_time`),
  CONSTRAINT `fk_message_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';

-- ------------------------------
-- 11. AI预测结果表
-- ------------------------------
CREATE TABLE `t_ai_prediction` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `type` ENUM('environment','device_failure','anomaly') NOT NULL COMMENT '预测类型',
  `device_id` VARCHAR(32) DEFAULT NULL COMMENT '关联设备',
  `predict_time` DATETIME NOT NULL COMMENT '预测时间点',
  `result_json` JSON NOT NULL COMMENT '预测结果(温度/湿度/风险等)',
  `risk_level` ENUM('low','medium','high') DEFAULT NULL COMMENT '风险等级',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type`),
  KEY `idx_device_id` (`device_id`),
  KEY `idx_predict_time` (`predict_time`),
  CONSTRAINT `fk_prediction_device` FOREIGN KEY (`device_id`) REFERENCES `t_device` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI预测结果表';

-- ------------------------------
-- 12. 报告表
-- ------------------------------
CREATE TABLE `t_report` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `type` ENUM('daily','weekly','monthly') NOT NULL COMMENT '报告类型',
  `title` VARCHAR(200) NOT NULL COMMENT '报告标题',
  `content` LONGTEXT DEFAULT NULL COMMENT '报告内容(JSON或Markdown)',
  `start_time` DATETIME NOT NULL COMMENT '统计开始',
  `end_time` DATETIME NOT NULL COMMENT '统计结束',
  `creator_id` VARCHAR(32) NOT NULL COMMENT '创建人ID',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '软删除',
  PRIMARY KEY (`id`),
  KEY `idx_type` (`type`),
  KEY `idx_creator` (`creator_id`),
  KEY `idx_time_range` (`start_time`, `end_time`),
  CONSTRAINT `fk_report_creator` FOREIGN KEY (`creator_id`) REFERENCES `t_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告表';

-- ------------------------------
-- 13. 系统配置表
-- ------------------------------
CREATE TABLE `t_system_config` (
  `id` VARCHAR(32) NOT NULL COMMENT 'UUID',
  `config_key` VARCHAR(100) NOT NULL COMMENT '配置键',
  `config_value` TEXT DEFAULT NULL COMMENT '配置值(JSON)',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '描述',
  `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- ------------------------------
-- 14. 系统日志表
-- ------------------------------
CREATE TABLE `t_system_log` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `level` ENUM('info','warn','error') NOT NULL COMMENT '日志级别',
  `module` VARCHAR(50) DEFAULT NULL COMMENT '模块名',
  `content` TEXT DEFAULT NULL COMMENT '日志内容',
  `user_id` VARCHAR(32) DEFAULT NULL COMMENT '操作人ID',
  `ip_address` VARCHAR(50) DEFAULT NULL COMMENT '请求IP',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_level` (`level`),
  KEY `idx_module` (`module`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_create_time` (`create_time`),
  CONSTRAINT `fk_log_user` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统日志表';

-- 所有表创建完成