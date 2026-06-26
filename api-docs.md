## 智能巡检系统 - 后端接口文档

### 基础信息
- **基础URL**: `http://localhost:3000/api`
- **认证方式**: JWT Token，通过 `Authorization: Bearer <token>` 请求头传递
- **统一响应格式**:
```json
{
  "code": 200,
  "msg": "success",
  "data": null
}
```

### 通用分页响应格式
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [],
    "total": 0,
    "page": 1,
    "pageSize": 10
  }
}
```

### 健康检查
- **URL**: `GET /health`
- **无需认证**
- **成功响应**: `{ "code": 200, "msg": "fire-patrol-server is running", "data": null }`

---

### 一、用户模块 `/api/user`

#### 1. 注册
- **URL**: `POST /api/user/register`
- **无需认证**
- **请求体**:
```json
{
  "username": "string",      // 用户名，必填
  "password": "string",      // 密码，必填
  "real_name": "string",      // 真实姓名，必填
  "phone": "string"           // 手机号（可选）
}
```
- **说明**: 注册后 status 直接设为 1（正常），即可登录
- **成功响应**: `{ "code": 200, "msg": "注册成功，请等待管理员审核", "data": null }`

#### 2. 登录
- **URL**: `POST /api/user/login`
- **无需认证**
- **请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```
- **成功响应**:
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "string",
    "user": {
      "id": number,
      "username": "string",
      "real_name": "string",
      "phone": "string",
      "role": number,         // 1: 超级管理员, 2: 运维员
      "status": number        // 0-待审核/禁用, 1-正常启用
    }
  }
}
```

#### 3. 退出登录
- **URL**: `POST /api/user/logout`
- **需要认证**

#### 4. 获取用户信息
- **URL**: `GET /api/user/info`
- **需要认证**
- **成功响应**: 返回 id, username, real_name, phone, role, status

#### 5. 获取用户列表（管理员）
- **URL**: `GET /api/user/list?page=1&pageSize=10&status=`
- **需要管理员认证**
- **请求参数**: `page`, `pageSize`, `status`（可选，0-待审核/1-正常/2-禁用）
- **成功响应**: 分页返回用户数组（含 id, username, real_name, phone, role, status, create_time）

#### 6. 获取用户详情（管理员）
- **URL**: `GET /api/user/:id`
- **需要管理员认证**

#### 7. 添加用户（管理员）
- **URL**: `POST /api/user/add`
- **需要管理员认证**
- **请求体**: `{ "username", "password", "real_name", "role" }`

#### 8. 更新用户（管理员）
- **URL**: `PUT /api/user/update`
- **需要管理员认证**
- **请求体**: `{ "id", "real_name", "phone", "role" }`

#### 9. 删除用户（管理员）
- **URL**: `POST /api/user/delete`
- **需要管理员认证**
- **请求体**: `{ "id": number }`

#### 10. 更新用户状态（管理员）
- **URL**: `POST /api/user/updateStatus`
- **需要管理员认证**
- **请求体**: `{ "id": number, "status": number }`
  - status: 0-待审核/禁用, 1-正常启用

#### 11. 重置密码
- **URL**: `POST /api/user/resetPwd`
- **无需认证**
- **请求体**:
```json
{
  "username": "string",
  "phone": "string",
  "newPassword": "string"
}
```

---

### 二、机器人模块 `/api/robot`

#### 1. 获取机器人列表
- **URL**: `GET /api/robot/list`
- **需要认证**
- **成功响应**: 返回机器人数组（含 id, robot_sn, robot_name, area_name, online_status, battery, run_mode, firmware_version, last_upload_time, create_by, remark, create_time, update_time）

#### 2. 获取机器人详情
- **URL**: `GET /api/robot/:id`
- **需要认证**

#### 3. 按SN获取机器人
- **URL**: `GET /api/robot/sn/:robot_sn`
- **需要认证**

#### 4. 获取机器人统计
- **URL**: `GET /api/robot/statistics`
- **需要认证**
- **成功响应**: `{ "total": number, "online": number, "offline": number }`

#### 5. 添加机器人
- **URL**: `POST /api/robot/add`
- **需要认证**
- **请求体**: `{ "robot_sn", "robot_name", "area_name", "remark"(可选) }`

#### 6. 更新机器人
- **URL**: `PUT /api/robot/update`
- **需要认证**
- **请求体**: `{ "id", "robot_name", "area_name", "remark" }`

#### 7. 删除机器人
- **URL**: `POST /api/robot/delete`
- **需要认证**
- **请求体**: `{ "id": number }`

#### 8. 发送控制命令
- **URL**: `POST /api/robot/sendCmd`
- **需要认证**
- **请求体**:
```json
{
  "robot_sn": "string",
  "cmd_code": "string",
  "param": "string"
}
```

#### 9. 获取指令记录
- **URL**: `GET /api/robot/cmd/list?robot_sn=&page=1&pageSize=10&cmd_status=`
- **需要认证**
- **成功响应**: 分页返回指令记录数组（含 id, robot_sn, sensor_record_id, cmd_code, hardware_cmd, cmd_param, operator, send_time, response_code, response_msg, finish_time, cmd_status）
  - cmd_status: 1-已下发, 2-执行成功, 3-执行失败, 4-超时

#### 10. 获取传感器历史数据
- **URL**: `GET /api/robot/sensor/history?robot_sn=&page=1&pageSize=20&startTime=&endTime=`
- **需要认证**
- **成功响应**: 分页返回传感器数组（含 id, robot_sn, patrol_record_id, temperature, humidity, smoke_level, max_single_temp, human_detected, fire_risk, thermal_matrix, battery, collect_time）

#### 11. 获取最新传感器数据
- **URL**: `GET /api/robot/sensor/latest/:robot_sn`
- **需要认证**
- **成功响应**: 返回单条最新传感器记录（字段同上）

#### 12. 获取传感器统计
- **URL**: `GET /api/robot/sensor/statistics?robot_sn=&startTime=&endTime=`
- **需要认证**

---

### 三、巡检任务模块 `/api/patrol`

#### 1. 获取巡检任务列表
- **URL**: `GET /api/patrol/task/list?page=1&pageSize=10&robot_sn=`
- **需要认证**
- **成功响应**: 分页返回任务数组（含 id, task_name, robot_sn, cycle_type, start_time, end_time, route_points, status, create_by, remark, create_time, update_time）
  - cycle_type: 1-每日, 2-工作日, 3-周末, 4-单次
  - status: 0-停用, 1-启用

#### 2. 获取巡检任务统计
- **URL**: `GET /api/patrol/task/statistics`
- **需要认证**
- **成功响应**: `{ "total": number, "enabled": number, "disabled": number }`

#### 3. 添加巡检任务
- **URL**: `POST /api/patrol/task/add`
- **需要认证**
- **请求体**:
```json
{
  "task_name": "string",
  "robot_sn": "string",
  "cycle_type": number,
  "start_time": "string",      // TIME格式 HH:mm:ss
  "end_time": "string",        // TIME格式 HH:mm:ss
  "route_points": []            // 巡检点位列表JSON数组（可选）
}
```

#### 4. 更新巡检任务
- **URL**: `PUT /api/patrol/task/update`
- **需要认证**
- **请求体**: `{ "id", "task_name", "cycle_type", "start_time", "end_time", "route_points", "status" }`

#### 5. 更新任务状态
- **URL**: `POST /api/patrol/task/status`
- **需要认证**
- **请求体**: `{ "id": number, "status": number }`（0-停用, 1-启用）

#### 6. 删除巡检任务
- **URL**: `POST /api/patrol/task/delete`
- **需要认证**
- **请求体**: `{ "id": number }`

#### 7. 获取巡检记录列表
- **URL**: `GET /api/patrol/record/list?page=1&pageSize=10&robot_sn=&startTime=&endTime=`
- **需要认证**
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [{
      "id": number,
      "task_id": number,
      "robot_sn": "string",
      "start_time": "string",
      "end_time": "string | null",
      "patrol_status": number,      // 1-进行中, 2-已完成, 3-异常中断
      "data_count": number,          // 本次采集传感器数据条数
      "alarm_count": number,         // 本次巡检产生告警数量
      "patrol_result": "string",
      "create_by": "string",
      "create_time": "string"
    }],
    "total": number
  }
}
```

#### 8. 获取巡检记录详情
- **URL**: `GET /api/patrol/record/:id`
- **需要认证**
- **成功响应**: 返回单条巡检记录对象（字段同上）

#### 9. 获取巡检记录统计
- **URL**: `GET /api/patrol/record/statistics?startTime=&endTime=`
- **需要认证**
- **成功响应**: `{ "total": number, "ongoing": number, "completed": number, "interrupted": number, "total_data_count": number, "total_alarm_count": number }`

#### 10. 开始巡检
- **URL**: `POST /api/patrol/start`
- **需要认证**
- **请求体**: `{ "robot_sn": "string", "task_id": number(可选) }`
- **成功响应**: `{ "code": 200, "msg": "巡检开始成功", "data": { "record_id": number } }`

#### 11. 结束巡检
- **URL**: `POST /api/patrol/end`
- **需要认证**
- **请求体**: `{ "id": number, "patrol_result": "string"(可选) }`

---

### 四、告警模块 `/api/alarm`

#### 1. 获取告警列表
- **URL**: `GET /api/alarm/list?page=1&pageSize=10&alarm_level=RED&deal_status=0&robot_sn=&startTime=&endTime=`
- **需要认证**
- **请求参数**: `page`, `pageSize`, `alarm_level`(RED/ORANGE/NORMAL, 可选), `deal_status`(0-待处置/1-已处置, 可选), `robot_sn`(可选), `startTime`(可选), `endTime`(可选)
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "list": [{
      "id": number,
      "robot_sn": "string",
      "sensor_record_id": number,
      "hardware_alarm_type": number,  // 0-正常, 1-高温无人, 2-高温, 3-烟雾
      "alarm_type": "string",         // HIGH_TEMP/SMOKE/NO_HUMAN
      "alarm_level": "string",        // RED/ORANGE/NORMAL
      "alarm_desc": "string",
      "area_name": "string",
      "point_name": "string",
      "deal_status": number,          // 0-未处理, 1-已处理
      "deal_user": "string",
      "deal_content": "string",
      "deal_time": "string | null",
      "create_time": "string"
    }],
    "total": number
  }
}
```

#### 2. 获取告警详情
- **URL**: `GET /api/alarm/:id`
- **需要认证**
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": number,
    "robot_sn": "string",
    "alarm_level": "string",
    "alarm_desc": "string",
    "sensor_data": {
      "temperature": number,
      "humidity": number,
      "smoke_level": number,
      "max_single_temp": number,
      "collect_time": "string"
    }
  }
}
```

#### 3. 处置告警
- **URL**: `POST /api/alarm/deal`
- **需要认证**
- **请求体**: `{ "id": number, "deal_content": "string" }`

#### 4. 删除告警
- **URL**: `POST /api/alarm/delete`
- **需要认证**
- **请求体**: `{ "id": number }`

#### 5. 获取告警统计
- **URL**: `GET /api/alarm/statistics`
- **需要认证**
- **成功响应**: `{ "total": number, "red": number, "orange": number, "normal": number, "pending": number, "dealt": number }`

#### 6. 获取最近告警
- **URL**: `GET /api/alarm/recent?limit=10`
- **需要认证**
- **成功响应**: 返回告警数组

#### 7. 获取告警趋势
- **URL**: `GET /api/alarm/trend?days=7`
- **需要认证**
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "labels": ["06/20", "06/21"],
    "level1": [5, 3],        // RED
    "level2": [2, 1],        // ORANGE
    "level3": [8, 6]         // NORMAL
  }
}
```

---

### 五、报表模块 `/api/report`

#### 1. 获取环境趋势
- **URL**: `GET /api/report/env/trend?robot_sn=ROBOT_001&startTime=&endTime=`
- **需要认证**
- **请求参数**:
  - `robot_sn`: 机器人序列号（可选）
  - `startTime`: 开始时间（可选，默认今天0点）
  - `endTime`: 结束时间（可选，默认当前时间）
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": [{
    "time": "string",            // collect_time
    "temperature": number,
    "humidity": number,
    "smoke_level": number,
    "max_single_temp": number
  }]
}
```

#### 2. 获取告警趋势
- **URL**: `GET /api/report/alarm/trend?type=day`
- **需要认证**
- **请求参数**: `type`: day-按小时统计(当天), week-近7天按天统计
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "labels": ["08:00", "09:00"],
    "level1": [5, 3],
    "level2": [2, 1],
    "level3": [8, 6]
  }
}
```

#### 3. 获取日报
- **URL**: `GET /api/report/daily?startTime=&endTime=`
- **需要认证**
- **请求参数**: `startTime`(可选，默认当天0点), `endTime`(可选，默认当前时间)
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "date": "string",
    "total_patrol": number,
    "completed_patrol": number,
    "total_alarm": number,
    "processed_alarm": number,
    "avg_temperature": number,
    "avg_humidity": number,
    "max_temperature": number
  }
}
```

---

### 六、AI智能模块 `/api/ai`

#### 1. AI分析告警
- **URL**: `POST /api/ai/alarm/analyze`
- **需要认证**
- **请求体**:
```json
{
  "alarm_id": number              // 告警ID，必填
}
```
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "analysis": "string"          // AI分析结果
  }
}
```

#### 2. AI对话
- **URL**: `POST /api/ai/chat`
- **需要认证**
- **请求体**:
```json
{
  "message": "string",            // 用户消息，必填
  "relate_alarm_id": number,      // 关联告警ID（可选）
  "relate_robot_sn": "string"     // 关联机器人序列号（可选）
}
```
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "answer": "string"            // AI回复
  }
}
```

#### 3. 获取对话历史
- **URL**: `GET /api/ai/chat/list?page=1&pageSize=20`
- **需要认证**
- **成功响应**: 分页返回对话记录数组（含 id, user_query, ai_answer, chat_type, relate_alarm_id, relate_robot_sn, create_time）
  - chat_type: 1-手动问答, 2-告警自动分析, 3-报表AI解读

#### 4. AI分析报表
- **URL**: `POST /api/ai/report/analyze`
- **需要认证**
- **请求体**:
```json
{
  "robot_sn": "string",           // 机器人序列号（可选）
  "startTime": "string",          // 开始时间（可选）
  "endTime": "string"             // 结束时间（可选）
}
```
- **成功响应**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "analysis": "string"
  }
}
```

---

### 七、系统日志模块 `/api/sys`

#### 1. 获取日志列表
- **URL**: `GET /api/sys/log/list?page=1&pageSize=10&username=&startTime=&endTime=`
- **需要管理员认证**
- **请求参数**: `page`, `pageSize`, `username`(可选), `startTime`(可选), `endTime`(可选)
- **成功响应**: 分页返回操作日志数组（含 id, username, module, operation, ip_address, detail, create_time）

---

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或token过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 枚举值说明

| 字段 | 值 | 说明 |
|------|-----|------|
| user.role | 1 | 超级管理员 |
| user.role | 2 | 运维员 |
| user.status | 0 | 待审核/禁用 |
| user.status | 1 | 正常启用 |
| robot.online_status | 0 | 离线 |
| robot.online_status | 1 | 在线 |
| robot.run_mode | 0 | 待机 |
| robot.run_mode | 1 | 自动巡检 |
| robot.run_mode | 2 | 手动遥控 |
| robot.run_mode | 3 | 充电中 |
| robot.run_mode | 4 | 故障 |
| alarm.alarm_level | RED | 红色告警（严重） |
| alarm.alarm_level | ORANGE | 橙色告警（中级） |
| alarm.alarm_level | NORMAL | 普通告警 |
| alarm.deal_status | 0 | 未处理 |
| alarm.deal_status | 1 | 已处理 |
| patrol_task.cycle_type | 1 | 每日 |
| patrol_task.cycle_type | 2 | 工作日 |
| patrol_task.cycle_type | 3 | 周末 |
| patrol_task.cycle_type | 4 | 单次 |
| patrol_task.status | 0 | 停用 |
| patrol_task.status | 1 | 启用 |
| patrol_record.patrol_status | 1 | 进行中 |
| patrol_record.patrol_status | 2 | 已完成 |
| patrol_record.patrol_status | 3 | 异常中断 |
| robot_cmd_record.cmd_status | 1 | 已下发 |
| robot_cmd_record.cmd_status | 2 | 执行成功 |
| robot_cmd_record.cmd_status | 3 | 执行失败 |
| robot_cmd_record.cmd_status | 4 | 超时 |
| ai_chat_record.chat_type | 1 | 手动问答 |
| ai_chat_record.chat_type | 2 | 告警自动分析 |
| ai_chat_record.chat_type | 3 | 报表AI解读 |

### 默认测试数据

数据库已预置以下数据：

**机器人**:
- `ROBOT_001` - 一号巡检机器人
-- =============================================
-- 1. 创建数据库
-- =============================================
CREATE DATABASE IF NOT EXISTS `inspection_system` 
DEFAULT CHARACTER SET utf8mb4 
DEFAULT COLLATE utf8mb4_unicode_ci;

USE `inspection_system`;

-- =============================================
-- 2. 系统字典模块（统一管理所有枚举值，避免前后端硬编码）
-- =============================================
-- 2.1 字典类型表
DROP TABLE IF EXISTS `sys_dict_type`;
CREATE TABLE `sys_dict_type` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `dict_code` VARCHAR(64) NOT NULL COMMENT '字典类型编码',
  `dict_name` VARCHAR(100) NOT NULL COMMENT '字典类型名称',
  `remark` VARCHAR(200) DEFAULT '' COMMENT '备注说明',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_dict_code` (`dict_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统字典类型表';

-- 2.2 字典项表
DROP TABLE IF EXISTS `sys_dict_item`;
CREATE TABLE `sys_dict_item` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `dict_code` VARCHAR(64) NOT NULL COMMENT '所属字典类型编码',
  `item_value` VARCHAR(64) NOT NULL COMMENT '字典项值',
  `item_label` VARCHAR(100) NOT NULL COMMENT '字典项显示名称',
  `sort` INT NOT NULL DEFAULT 0 COMMENT '排序号，升序排列',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_dict_code` (`dict_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统字典项表';

-- 初始化字典数据
INSERT INTO `sys_dict_type` (`dict_code`, `dict_name`) VALUES
('user_role', '用户角色'),
('user_status', '用户状态'),
('robot_online_status', '机器人在线状态'),
('robot_run_mode', '机器人运行模式'),
('fire_risk_type', '板端告警类型'),
('alarm_type', '告警类型'),
('alarm_level', '告警等级'),
('deal_status', '处置状态'),
('patrol_cycle', '巡检周期'),
('patrol_status', '巡检状态'),
('cmd_status', '指令执行状态'),
('ai_chat_type', 'AI对话类型');

INSERT INTO `sys_dict_item` (`dict_code`, `item_value`, `item_label`, `sort`) VALUES
-- 用户角色
('user_role', '1', '超级管理员', 1),
('user_role', '2', '运维员', 2),
-- 用户状态
('user_status', '0', '待审核/禁用', 1),
('user_status', '1', '正常启用', 2),
-- 机器人运行模式
('robot_run_mode', '0', '待机', 1),
('robot_run_mode', '1', '自动巡检', 2),
('robot_run_mode', '2', '手动遥控', 3),
('robot_run_mode', '3', '充电中', 4),
('robot_run_mode', '4', '故障', 5),
-- 板端告警类型
('fire_risk_type', '0', '正常', 1),
('fire_risk_type', '1', '高温无人预警', 2),
('fire_risk_type', '2', '高温告警', 3),
('fire_risk_type', '3', '烟雾告警', 4),
-- 告警等级
('alarm_level', 'RED', '红色高危', 1),
('alarm_level', 'ORANGE', '橙色预警', 2),
('alarm_level', 'NORMAL', '一般提示', 3),
-- 处置状态
('deal_status', '0', '待处理', 1),
('deal_status', '1', '已处理', 2),
-- 巡检周期
('patrol_cycle', '1', '每日', 1),
('patrol_cycle', '2', '工作日', 2),
('patrol_cycle', '3', '周末', 3),
('patrol_cycle', '4', '单次执行', 4),
-- 巡检状态
('patrol_status', '1', '进行中', 1),
('patrol_status', '2', '已完成', 2),
('patrol_status', '3', '异常中断', 3),
-- 指令状态
('cmd_status', '1', '已下发', 1),
('cmd_status', '2', '执行成功', 2),
('cmd_status', '3', '执行失败', 3),
('cmd_status', '4', '执行超时', 4),
-- AI对话类型
('ai_chat_type', '1', '手动问答', 1),
('ai_chat_type', '2', '告警自动分析', 2),
('ai_chat_type', '3', '报表智能解读', 3);

-- =============================================
-- 3. 系统用户表
-- =============================================
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '登录账号',
  `password` VARCHAR(100) NOT NULL COMMENT 'BCrypt加密密码',
  `real_name` VARCHAR(30) NOT NULL COMMENT '真实姓名',
  `phone` VARCHAR(20) DEFAULT NULL COMMENT '联系电话',
  `role` TINYINT NOT NULL COMMENT '角色：1-超级管理员 2-运维员',
  `status` TINYINT NOT NULL DEFAULT 0 COMMENT '账号状态：0-待审核/禁用 1-正常启用',
  `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` VARCHAR(50) DEFAULT '' COMMENT '最后登录IP地址',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除 1-已删除',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_phone` (`phone`),
  KEY `idx_role_status` (`role`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- 初始化超级管理员：账号 admin / 密码 123456
INSERT INTO `sys_user` (`username`, `password`, `real_name`, `role`, `status`)
VALUES ('admin', '$2b$10$7o9OWRsizOrGLZeAaVFBNOxjaGAozfE3f7GNJA85KJyEpLSSS1SlW', '系统管理员', 1, 1);

-- =============================================
-- 4. 巡检机器人设备表（维度表，与核心表通过robot_sn一对多关联）
-- =============================================
DROP TABLE IF EXISTS `robot`;
CREATE TABLE `robot` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `robot_sn` VARCHAR(64) NOT NULL COMMENT '机器人唯一序列号（TCP通信标识）',
  `robot_name` VARCHAR(100) DEFAULT '' COMMENT '机器人名称',
  `area_name` VARCHAR(100) NOT NULL COMMENT '负责巡检区域',
  `battery` DECIMAL(5,1) DEFAULT 0 COMMENT '当前电量 0-100%',
  `online_status` TINYINT NOT NULL DEFAULT 0 COMMENT '在线状态：0-离线 1-在线',
  `run_mode` TINYINT NOT NULL DEFAULT 0 COMMENT '运行模式：0-待机 1-自动巡检 2-手动遥控 3-充电中 4-故障',
  `firmware_version` VARCHAR(32) DEFAULT '' COMMENT '固件版本号',
  `last_upload_time` DATETIME DEFAULT NULL COMMENT '最后数据上报时间',
  `create_by` VARCHAR(50) DEFAULT '' COMMENT '创建人账号',
  `remark` VARCHAR(500) DEFAULT '' COMMENT '备注说明',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除 1-已删除',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_robot_sn` (`robot_sn`),
  KEY `idx_area` (`area_name`),
  KEY `idx_online_status` (`online_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巡检机器人设备表';

-- 初始化示例机器人
INSERT INTO `robot` (`robot_sn`, `robot_name`, `area_name`, `battery`, `online_status`, `run_mode`)
VALUES ('ROBOT_001', '一号巡检机器人', 'A区实验楼', 85.5, 0, 0);

-- =============================================
-- 5. 【核心事实表】机器人多模态传感器原始数据表
-- 全系统数据核心，所有业务表均关联此表溯源原始数据
-- =============================================
DROP TABLE IF EXISTS `robot_sensor_record`;
CREATE TABLE `robot_sensor_record` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID，全库数据溯源核心',
  `robot_sn` VARCHAR(64) NOT NULL COMMENT '机器人序列号，关联robot表',
  `patrol_record_id` BIGINT DEFAULT NULL COMMENT '关联巡检记录ID，NULL表示非巡检时段采集',
  `temperature` DECIMAL(6,2) NOT NULL COMMENT '环境温度（℃）',
  `humidity` DECIMAL(6,2) NOT NULL COMMENT '环境湿度（%RH）',
  `smoke_level` DECIMAL(6,2) NOT NULL COMMENT '烟雾浓度（PPM）',
  `max_single_temp` DECIMAL(6,2) NOT NULL COMMENT '热成像画面最高温度（℃）',
  `human_detected` TINYINT NOT NULL COMMENT '人体检测：0-无人 1-有人',
  `fire_risk` TINYINT NOT NULL COMMENT '板端告警类型：0-正常 1-高温无人 2-高温 3-烟雾',
  `thermal_matrix` JSON NOT NULL COMMENT '8×8热成像温度矩阵（MySQL原生JSON格式）',
  `battery` DECIMAL(5,1) NOT NULL COMMENT '上报时刻机器人电量（%）',
  `collect_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
  PRIMARY KEY (`id`),
  -- 核心索引1：按机器人+时间范围查询历史数据
  KEY `idx_robot_collect_time` (`robot_sn`, `collect_time`),
  -- 核心索引2：按巡检记录查询所有采集明细
  KEY `idx_patrol_collect_time` (`patrol_record_id`, `collect_time`),
  -- 覆盖索引：告警统计场景，直接从索引取数无需回表
  KEY `idx_robot_risk_time` (`robot_sn`, `fire_risk`, `collect_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='【核心事实表】机器人多模态传感器原始数据表';

-- =============================================
-- 6. 定时巡检任务配置表
-- =============================================
DROP TABLE IF EXISTS `patrol_task`;
CREATE TABLE `patrol_task` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `robot_sn` VARCHAR(64) NOT NULL COMMENT '绑定机器人序列号',
  `task_name` VARCHAR(100) NOT NULL COMMENT '任务名称',
  `cycle_type` TINYINT NOT NULL COMMENT '执行周期：1-每日 2-工作日 3-周末 4-单次',
  `start_time` TIME NOT NULL COMMENT '任务开始时间',
  `end_time` TIME NOT NULL COMMENT '任务结束时间',
  `route_points` JSON DEFAULT NULL COMMENT '巡检点位列表JSON',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '启用状态：0-停用 1-启用',
  `create_by` VARCHAR(50) DEFAULT '' COMMENT '创建人账号',
  `remark` VARCHAR(500) DEFAULT '' COMMENT '任务备注',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_robot_status` (`robot_sn`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定时巡检任务配置表';

-- =============================================
-- 7. 巡检执行历史记录表
-- 与核心表一对多关联，一次巡检对应多条传感器采集记录
-- =============================================
DROP TABLE IF EXISTS `patrol_record`;
CREATE TABLE `patrol_record` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `task_id` BIGINT DEFAULT NULL COMMENT '关联定时任务ID，手动巡检为NULL',
  `robot_sn` VARCHAR(64) NOT NULL COMMENT '机器人序列号',
  `patrol_status` TINYINT NOT NULL DEFAULT 1 COMMENT '巡检状态：1-进行中 2-已完成 3-异常中断',
  `start_time` DATETIME NOT NULL COMMENT '巡检开始时间',
  `end_time` DATETIME DEFAULT NULL COMMENT '巡检结束时间',
  `data_count` INT NOT NULL DEFAULT 0 COMMENT '本次采集传感器数据条数',
  `alarm_count` INT NOT NULL DEFAULT 0 COMMENT '本次巡检产生告警数量',
  `patrol_result` TEXT COMMENT '巡检总结描述',
  `create_by` VARCHAR(50) DEFAULT '' COMMENT '触发人（手动巡检时记录）',
  PRIMARY KEY (`id`),
  KEY `idx_robot_start_time` (`robot_sn`, `start_time`),
  KEY `idx_patrol_status` (`patrol_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='巡检执行历史记录表';

-- =============================================
-- 8. 火灾隐患告警记录表
-- 与核心表一对一关联，每条告警严格对应一条触发告警的原始采集数据
-- =============================================
DROP TABLE IF EXISTS `alarm_info`;
CREATE TABLE `alarm_info` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `robot_sn` VARCHAR(64) NOT NULL COMMENT '产生告警的机器人',
  `sensor_record_id` BIGINT NOT NULL COMMENT '关联核心表ID，溯源原始采集数据（逻辑外键）',
  `hardware_alarm_type` TINYINT NOT NULL COMMENT '硬件原始告警类型：0-正常 1-高温无人 2-高温 3-烟雾',
  `alarm_type` VARCHAR(30) NOT NULL COMMENT '告警类型：HIGH_TEMP-高温 / SMOKE-烟雾 / NO_HUMAN-无人高温',
  `alarm_level` VARCHAR(16) NOT NULL COMMENT '告警等级：RED-红色高危 / ORANGE-橙色预警 / NORMAL-一般提示',
  `alarm_desc` VARCHAR(500) NOT NULL COMMENT '告警描述',
  `area_name` VARCHAR(100) NOT NULL COMMENT '发生区域',
  `point_name` VARCHAR(100) DEFAULT '' COMMENT '点位名称',
  `deal_status` TINYINT NOT NULL DEFAULT 0 COMMENT '处置状态：0-未处理 1-已处理',
  `deal_user` VARCHAR(30) DEFAULT '' COMMENT '处置人账号',
  `deal_content` TEXT COMMENT '处置说明',
  `deal_time` DATETIME DEFAULT NULL COMMENT '处置完成时间',
  `is_deleted` TINYINT NOT NULL DEFAULT 0 COMMENT '逻辑删除：0-未删除 1-已删除',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '告警产生时间',
  PRIMARY KEY (`id`),
  -- 溯源核心索引：直接关联原始数据，唯一约束确保一条传感器记录最多产生一条告警
  UNIQUE KEY `uk_sensor_record_id` (`sensor_record_id`),
  -- 高频业务索引：未处理告警按等级+时间筛选
  KEY `idx_deal_level_create` (`deal_status`, `alarm_level`, `create_time`),
  KEY `idx_robot_create_time` (`robot_sn`, `create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='火灾隐患告警记录表';

-- =============================================
-- 9. 机器人远程控制指令记录表
-- 与核心表通过robot_sn+时间范围间接关联
-- =============================================
DROP TABLE IF EXISTS `robot_cmd_record`;
CREATE TABLE `robot_cmd_record` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `robot_sn` VARCHAR(64) NOT NULL COMMENT '目标机器人序列号',
  `sensor_record_id` BIGINT DEFAULT NULL COMMENT '关联核心表ID，溯源触发指令的原始采集数据',
  `cmd_code` VARCHAR(32) NOT NULL COMMENT '业务指令编码',
  `hardware_cmd` CHAR(1) DEFAULT '' COMMENT '下发硬件单字符指令',
  `cmd_param` VARCHAR(500) DEFAULT '' COMMENT '指令附加参数JSON',
  `operator` VARCHAR(50) NOT NULL COMMENT '下发操作人账号',
  `send_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '指令下发时间',
  `response_code` INT DEFAULT NULL COMMENT '机器人回执码：200-成功',
  `response_msg` VARCHAR(200) DEFAULT '' COMMENT '回执描述',
  `finish_time` DATETIME DEFAULT NULL COMMENT '指令执行完成时间',
  `cmd_status` TINYINT NOT NULL DEFAULT 1 COMMENT '指令状态：1-已下发 2-执行成功 3-执行失败 4-超时',
  PRIMARY KEY (`id`),
  KEY `idx_robot_sn` (`robot_sn`),
  KEY `idx_send_time` (`send_time`),
  KEY `idx_sensor_record_id` (`sensor_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机器人远程控制指令记录表';

-- =============================================
-- 10. AI智能体对话与建议记录表
-- 支持直接关联核心表原始数据，溯源分析依据
-- =============================================
DROP TABLE IF EXISTS `ai_chat_record`;
CREATE TABLE `ai_chat_record` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '提问/操作人账号',
  `chat_type` TINYINT NOT NULL DEFAULT 1 COMMENT '对话类型：1-手动问答 2-告警自动分析 3-报表AI解读',
  `sensor_record_id` BIGINT DEFAULT NULL COMMENT '关联核心表ID，溯源分析的原始采集数据',
  `user_query` TEXT NOT NULL COMMENT '用户提问文本 / 自动分析标识',
  `ai_answer` TEXT NOT NULL COMMENT 'DeepSeek生成的分析与整改建议',
  `relate_alarm_id` BIGINT DEFAULT NULL COMMENT '关联告警ID',
  `relate_robot_sn` VARCHAR(64) DEFAULT NULL COMMENT '关联机器人序列号',
  `tokens_used` INT DEFAULT 0 COMMENT '消耗Token数量',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_create_time` (`username`, `create_time`),
  KEY `idx_relate_alarm` (`relate_alarm_id`),
  KEY `idx_relate_sensor` (`sensor_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI智能体对话与建议记录表';

-- =============================================
-- 11. 系统操作审计日志表
-- =============================================
DROP TABLE IF EXISTS `sys_log`;
CREATE TABLE `sys_log` (
  `id` BIGINT AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '操作人账号',
  `module` VARCHAR(50) DEFAULT '' COMMENT '操作模块：用户/设备/告警/巡检/系统',
  `operation` VARCHAR(200) NOT NULL COMMENT '操作内容简述',
  `ip_address` VARCHAR(50) NOT NULL COMMENT '操作IP地址',
  `detail` TEXT COMMENT '操作详情JSON',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_create_time` (`username`, `create_time`),
  KEY `idx_module` (`module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作审计日志表';