# 智能巡检系统 - 后端接口文档

**版本**: v1.3  
**更新日期**: 2026-06-11

**更新说明**: 删除 AI 模块相关功能

## 文档说明

本文档为智能巡检系统的后端 API 接口规范，包含系统所有功能模块的接口定义，作为前端开发对接、后端开发实现和测试验证的依据。

---

## 目录

1. [认证模块](#1-认证模块)
2. [机器人模块](#2-机器人模块)
3. [热成像模块](#3-热成像模块)
4. [环境监测模块](#4-环境监测模块)
5. [告警模块](#5-告警模块)
6. [设备模块](#6-设备模块)
7. [传感器模块](#7-传感器模块)
8. [消息模块](#8-消息模块)
9. [用户模块](#9-用户模块)
10. [系统模块](#10-系统模块)
11. [报告模块](#11-报告模块)
12. [错误码说明](#12-错误码说明)

---

## 基础配置

### 请求头

| 字段名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `Content-Type` | string | 是 | `application/json` |
| `Authorization` | string | 否 | Bearer Token，格式：`Bearer {token}` |
| `X-User-Id` | string | 否 | 用户ID |

### 响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": 1699999999999
}
```

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `code` | number | 状态码，200 表示成功 |
| `message` | string | 响应消息 |
| `data` | any | 响应数据 |
| `timestamp` | number | 时间戳 |

---

## 1. 认证模块

### 1.1 用户登录

- **接口名称**：用户登录
- **请求路径**：`/api/auth/login`
- **请求方法**：POST
- **权限要求**：无需登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `username` | string | 否 | - | 用户名 |
| `phone` | string | 否 | - | 手机号 |
| `password` | string | 是 | - | 密码 |
| `captcha` | string | 否 | - | 验证码 |

> **说明**：`username` 和 `phone` 至少填一个

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `token` | string | JWT token |
| `user.id` | string | 用户ID |
| `user.username` | string | 用户名 |
| `user.phone` | string | 手机号 |
| `user.role` | string | 用户角色 |
| `user.permissions` | array | 权限列表 |

#### 示例

**请求**：
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "u001",
      "username": "admin",
      "phone": "13800138000",
      "role": "admin",
      "permissions": ["view", "edit", "delete"]
    }
  },
  "timestamp": 1699999999999
}
```

---

### 1.2 用户注册

- **接口名称**：用户注册
- **请求路径**：`/api/auth/register`
- **请求方法**：POST
- **权限要求**：无需登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `username` | string | 是 | - | 用户名 |
| `phone` | string | 是 | - | 手机号 |
| `password` | string | 是 | - | 密码 |
| `confirmPassword` | string | 是 | - | 确认密码 |
| `role` | string | 否 | viewer | 角色：viewer/operator/admin |
| `adminKey` | string | 否 | - | 管理员密钥（注册管理员时必填） |

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | string | 新用户ID |
| `username` | string | 用户名 |
| `role` | string | 用户角色 |

#### 示例

**请求（注册普通用户）**：
```json
{
  "username": "user1",
  "phone": "13900000001",
  "password": "123456",
  "confirmPassword": "123456",
  "role": "viewer"
}
```

**请求（注册管理员）**：
```json
{
  "username": "admin1",
  "phone": "13900000002",
  "password": "123456",
  "confirmPassword": "123456",
  "role": "admin",
  "adminKey": "admin-secret-key"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": "xxx",
    "username": "user1",
    "role": "viewer"
  },
  "timestamp": 1699999999999
}
```

> **说明**：注册管理员账户需要提供正确的管理员密钥，默认密钥为 `admin-secret-key`

---

### 1.3 密码重置

- **接口名称**：密码重置
- **请求路径**：`/api/auth/reset-password`
- **请求方法**：POST
- **权限要求**：无需登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `phone` | string | 是 | - | 手机号 |
| `newPassword` | string | 是 | - | 新密码 |
| `captcha` | string | 否 | - | 验证码 |

---

## 2. 机器人模块

### 2.1 获取机器人位置

- **接口名称**：获取机器人位置
- **请求路径**：`/api/robot/positions`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `robotId` | string | 否 | - | 机器人ID，不传返回全部 |

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `id` | string | 机器人ID |
| `x` | number | X坐标 |
| `y` | number | Y坐标 |
| `battery` | number | 电量(%) |
| `status` | string | 状态：moving/idle/offline |
| `speed` | number | 速度(m/s) |

---

### 2.2 获取机器人列表

- **接口名称**：获取机器人列表
- **请求路径**：`/api/robot`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 10 | 每页数量 |
| `status` | string | 否 | - | 状态筛选 |

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `list` | array | 机器人列表 |
| `list[].id` | string | 机器人ID |
| `list[].name` | string | 机器人名称 |
| `list[].model` | string | 型号 |
| `list[].battery` | number | 电量(%) |
| `list[].status` | string | 状态 |
| `total` | number | 总数 |
| `page` | number | 当前页 |

---

### 2.3 添加机器人

- **接口名称**：添加机器人
- **请求路径**：`/api/robot`
- **请求方法**：POST
- **权限要求**：管理员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | 是 | - | 机器人名称 |
| `model` | string | 是 | - | 型号 |
| `location` | string | 否 | - | 部署位置 |

---

### 2.4 更新机器人信息

- **接口名称**：更新机器人信息
- **请求路径**：`/api/robot/{robotId}`
- **请求方法**：PUT
- **权限要求**：管理员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | 否 | - | 机器人名称 |
| `model` | string | 否 | - | 型号 |
| `location` | string | 否 | - | 部署位置 |

---

### 2.5 删除机器人

- **接口名称**：删除机器人
- **请求路径**：`/api/robot/{robotId}`
- **请求方法**：DELETE
- **权限要求**：管理员

---

### 2.6 控制机器人

- **接口名称**：控制机器人
- **请求路径**：`/api/robot/{robotId}/control`
- **请求方法**：POST
- **权限要求**：操作员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `action` | string | 是 | - | 动作：move/stop/turn_left/turn_right |
| `speed` | number | 否 | 1 | 速度(0-10) |
| `duration` | number | 否 | - | 持续时间(秒) |

---

## 3. 热成像模块

### 3.1 获取热成像数据

- **接口名称**：获取热成像数据
- **请求路径**：`/api/sse/latest-data`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `maxTemp` | array | 8x8温度矩阵 |
| `temperature` | number | 环境温度(°C) |
| `humidity` | number | 湿度(%) |
| `gas` | number | 可燃气体浓度(ppm) |
| `battery` | number | 电量(%) |
| `humanDetected` | boolean | 是否检测到人 |

---

### 3.2 获取历史热成像数据

- **接口名称**：获取历史热成像数据
- **请求路径**：`/api/thermal-imaging/history`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `startTime` | string | 是 | - | 开始时间(ISO格式) |
| `endTime` | string | 是 | - | 结束时间(ISO格式) |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 100 | 每页数量 |

---

## 4. 环境监测模块

### 4.1 获取环境数据

- **接口名称**：获取环境数据
- **请求路径**：`/api/environment/latest`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `temperature` | number | 温度(°C) |
| `humidity` | number | 湿度(%) |
| `gas` | number | 可燃气体浓度(ppm) |
| `pm25` | number | PM2.5(μg/m³) |
| `maxThermalTemp` | number | 热成像最高温度(°C) |
| `updateTime` | string | 更新时间 |

---

### 4.2 获取环境数据历史

- **接口名称**：获取环境数据历史
- **请求路径**：`/api/environment/history`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `startTime` | string | 是 | - | 开始时间 |
| `endTime` | string | 是 | - | 结束时间 |
| `interval` | string | 否 | 1m | 时间间隔：1m/5m/15m/1h |

---

## 5. 告警模块

### 5.1 获取告警列表

- **接口名称**：获取告警列表
- **请求路径**：`/api/alerts`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `level` | string | 否 | - | 告警级别：warning/danger |
| `status` | string | 否 | - | 状态：pending/processed |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 20 | 每页数量 |

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `list` | array | 告警列表 |
| `list[].id` | string | 告警ID |
| `list[].type` | string | 告警类型 |
| `list[].level` | string | 告警级别 |
| `list[].message` | string | 告警消息 |
| `list[].device` | string | 设备ID |
| `list[].time` | string | 告警时间 |
| `list[].status` | string | 处理状态 |

---

### 5.2 处理告警

- **接口名称**：处理告警
- **请求路径**：`/api/alerts/{alertId}/process`
- **请求方法**：PUT
- **权限要求**：操作员及以上

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `action` | string | 是 | - | 处理动作：confirm/ignore |
| `remark` | string | 否 | - | 处理备注 |

---

## 6. 设备模块

### 6.1 获取设备统计

- **接口名称**：获取设备统计
- **请求路径**：`/api/devices/stats`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `total` | number | 设备总数 |
| `online` | number | 在线数量 |
| `offline` | number | 离线数量 |
| `warning` | number | 告警数量 |

---

### 6.2 获取设备列表

- **接口名称**：获取设备列表
- **请求路径**：`/api/devices`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 20 | 每页数量 |
| `status` | string | 否 | - | 状态筛选 |

---

### 6.3 获取设备详情

- **接口名称**：获取设备详情
- **请求路径**：`/api/devices/{deviceId}`
- **请求方法**：GET
- **权限要求**：已登录

---

## 7. 传感器模块

### 7.1 获取传感器数据

- **接口名称**：获取传感器数据
- **请求路径**：`/api/sensors`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `list` | array | 传感器列表 |
| `list[].id` | string | 传感器ID |
| `list[].name` | string | 传感器名称 |
| `list[].type` | string | 类型：temperature/humidity/gas |
| `list[].value` | number | 当前值 |
| `list[].unit` | string | 单位 |
| `list[].status` | string | 状态：normal/warning/danger |

---

### 7.2 获取最新温度数据

- **接口名称**：获取最新温度数据
- **请求路径**：`/api/sensors/temperature`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `value` | number | 温度值 |
| `unit` | string | 单位：°C |
| `updateTime` | string | 更新时间 |

#### 示例

**响应**：
```json
{
  "code": 200,
  "message": "温度数据获取成功",
  "data": {
    "value": 26.32,
    "unit": "°C",
    "updateTime": "2026-06-11T10:42:02.910975"
  },
  "timestamp": 1781145722911
}
```

---

### 7.3 获取最新湿度数据

- **接口名称**：获取最新湿度数据
- **请求路径**：`/api/sensors/humidity`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `value` | number | 湿度值 |
| `unit` | string | 单位：% |
| `updateTime` | string | 更新时间 |

#### 示例

**响应**：
```json
{
  "code": 200,
  "message": "湿度数据获取成功",
  "data": {
    "value": 59.41,
    "unit": "%",
    "updateTime": "2026-06-11T10:42:04.971921"
  },
  "timestamp": 1781145724972
}
```

---

### 7.4 获取最新可燃气体数据

- **接口名称**：获取最新可燃气体数据
- **请求路径**：`/api/sensors/gas`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `value` | number | 可燃气体浓度值 |
| `unit` | string | 单位：ppm |
| `updateTime` | string | 更新时间 |

#### 示例

**响应**：
```json
{
  "code": 200,
  "message": "可燃气体数据获取成功",
  "data": {
    "value": 496.97,
    "unit": "ppm",
    "updateTime": "2026-06-11T10:42:07.034169"
  },
  "timestamp": 1781145727034
}
```

---

## 8. 消息模块

### 8.1 获取消息列表

- **接口名称**：获取消息列表
- **请求路径**：`/api/messages`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `type` | string | 否 | - | 消息类型 |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 20 | 每页数量 |

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `list` | array | 消息列表 |
| `list[].id` | string | 消息ID |
| `list[].title` | string | 标题 |
| `list[].content` | string | 内容 |
| `list[].type` | string | 类型 |
| `list[].time` | string | 时间 |
| `list[].unread` | boolean | 是否已读 |

---

### 8.2 标记消息已读

- **接口名称**：标记消息已读
- **请求路径**：`/api/messages/{messageId}/read`
- **请求方法**：PUT
- **权限要求**：已登录

---

### 8.3 标记所有消息已读

- **接口名称**：标记所有消息已读
- **请求路径**：`/api/messages/read-all`
- **请求方法**：PUT
- **权限要求**：已登录

---

### 8.4 删除消息

- **接口名称**：删除消息
- **请求路径**：`/api/messages/{messageId}`
- **请求方法**：DELETE
- **权限要求**：已登录

---

## 9. 用户模块

### 9.1 获取用户列表

- **接口名称**：获取用户列表
- **请求路径**：`/api/users`
- **请求方法**：GET
- **权限要求**：管理员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 20 | 每页数量 |
| `role` | string | 否 | - | 角色筛选 |

---

### 9.2 获取当前用户信息

- **接口名称**：获取当前用户信息
- **请求路径**：`/api/users/me`
- **请求方法**：GET
- **权限要求**：已登录

---

### 9.3 更新用户信息

- **接口名称**：更新用户信息
- **请求路径**：`/api/users/{userId}`
- **请求方法**：PUT
- **权限要求**：管理员或本人

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `username` | string | 否 | - | 用户名 |
| `phone` | string | 否 | - | 手机号 |
| `role` | string | 否 | - | 角色(仅管理员) |

---

### 9.4 删除用户

- **接口名称**：删除用户
- **请求路径**：`/api/users/{userId}`
- **请求方法**：DELETE
- **权限要求**：管理员

---

## 10. 系统模块

### 10.1 获取系统状态

- **接口名称**：获取系统状态
- **请求路径**：`/api/system/status`
- **请求方法**：GET
- **权限要求**：已登录

#### 响应数据

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `status` | string | 系统状态：normal/warning/danger |
| `uptime` | number | 运行时长(秒) |
| `version` | string | 系统版本 |
| `cpuUsage` | number | CPU使用率(%) |
| `memoryUsage` | number | 内存使用率(%) |

---

### 10.2 获取系统日志

- **接口名称**：获取系统日志
- **请求路径**：`/api/system/logs`
- **请求方法**：GET
- **权限要求**：管理员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `level` | string | 否 | - | 日志级别：info/warn/error |
| `startTime` | string | 否 | - | 开始时间 |
| `endTime` | string | 否 | - | 结束时间 |
| `page` | number | 否 | 1 | 页码 |

---

### 10.3 更新系统配置

- **接口名称**：更新系统配置
- **请求路径**：`/api/system/config`
- **请求方法**：PUT
- **权限要求**：管理员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `updateInterval` | number | 否 | - | 数据更新间隔 (毫秒) |
| `alertThreshold` | object | 否 | - | 告警阈值配置 |

---

## 11. 报告模块

### 11.1 获取报告列表

- **接口名称**：获取报告列表
- **请求路径**：`/api/reports`
- **请求方法**：GET
- **权限要求**：已登录

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `type` | string | 否 | - | 报告类型 |
| `page` | number | 否 | 1 | 页码 |
| `size` | number | 否 | 20 | 每页数量 |

---

### 11.2 获取报告详情

- **接口名称**：获取报告详情
- **请求路径**：`/api/reports/{reportId}`
- **请求方法**：GET
- **权限要求**：已登录

---

### 11.3 生成报告

- **接口名称**：生成报告
- **请求路径**：`/api/reports/generate`
- **请求方法**：POST
- **权限要求**：管理员

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `type` | string | 是 | - | 报告类型 |
| `startTime` | string | 是 | - | 开始时间 |
| `endTime` | string | 是 | - | 结束时间 |

---

## 12. 错误码说明

| 错误码 | 说明 | HTTP状态码 |
| :--- | :--- | :--- |
| 200 | 成功 | 200 |
| 400 | 请求参数错误 | 400 |
| 401 | 未登录或Token失效 | 401 |
| 403 | 无权限访问 | 403 |
| 404 | 资源不存在 | 404 |
| 409 | 资源冲突 | 409 |
| 500 | 服务器内部错误 | 500 |
| 1001 | 用户不存在 | 400 |
| 1002 | 密码错误 | 400 |
| 1003 | 验证码错误 | 400 |
| 1004 | 用户已存在 | 409 |
| 2001 | 机器人不存在 | 404 |
| 2002 | 机器人离线 | 400 |
| 3001 | 设备不存在 | 404 |
| 4001 | 告警不存在 | 404 |

---

## 附录：接口权限矩阵

| 接口模块 | 游客 | 普通用户 | 操作员 | 管理员 |
| :--- | :---: | :---: | :---: | :---: |
| 登录/注册 | ✅ | - | - | - |
| 获取机器人位置 | - | ✅ | ✅ | ✅ |
| 控制机器人 | - | - | ✅ | ✅ |
| 添加/删除机器人 | - | - | - | ✅ |
| 获取告警列表 | - | ✅ | ✅ | ✅ |
| 处理告警 | - | - | ✅ | ✅ |
| 获取用户列表 | - | - | - | ✅ |
| 更新系统配置 | - | - | - | ✅ |

---

## 附录：已实现接口清单

### 已实现接口（共34个）

| 模块 | 接口 | 方法 | 路径 |
| :--- | :--- | :--- | :--- |
| 认证 | 用户登录 | POST | `/api/auth/login` |
| 认证 | 用户注册 | POST | `/api/auth/register` |
| 认证 | 密码重置 | POST | `/api/auth/reset-password` |
| 机器人 | 获取机器人位置 | GET | `/api/robot/positions` |
| 机器人 | 获取机器人列表 | GET | `/api/robot` |
| 机器人 | 添加机器人 | POST | `/api/robot` |
| 机器人 | 更新机器人信息 | PUT | `/api/robot/{robotId}` |
| 机器人 | 删除机器人 | DELETE | `/api/robot/{robotId}` |
| 机器人 | 控制机器人 | POST | `/api/robot/{robotId}/control` |
| 热成像 | 获取热成像数据 | GET | `/api/sse/latest-data` |
| 热成像 | 获取历史热成像数据 | GET | `/api/thermal-imaging/history` |
| 环境监测 | 获取环境数据 | GET | `/api/environment/latest` |
| 环境监测 | 获取环境数据历史 | GET | `/api/environment/history` |
| 告警 | 获取告警列表 | GET | `/api/alerts` |
| 告警 | 处理告警 | PUT | `/api/alerts/{alertId}/process` |
| 设备 | 获取设备统计 | GET | `/api/devices/stats` |
| 设备 | 获取设备列表 | GET | `/api/devices` |
| 设备 | 获取设备详情 | GET | `/api/devices/{deviceId}` |
| 传感器 | 获取传感器数据 | GET | `/api/sensors` |
| 消息 | 获取消息列表 | GET | `/api/messages` |
| 消息 | 标记消息已读 | PUT | `/api/messages/{messageId}/read` |
| 消息 | 标记所有消息已读 | PUT | `/api/messages/read-all` |
| 消息 | 删除消息 | DELETE | `/api/messages/{messageId}` |
| 用户 | 获取用户列表 | GET | `/api/users` |
| 用户 | 获取当前用户信息 | GET | `/api/users/me` |
| 用户 | 更新用户信息 | PUT | `/api/users/{userId}` |
| 用户 | 删除用户 | DELETE | `/api/users/{userId}` |
| 系统 | 获取系统状态 | GET | `/api/system/status` |
| 系统 | 获取系统日志 | GET | `/api/system/logs` |
| 系统 | 更新系统配置 | PUT | `/api/system/config` |
| AI | 环境数据预测 | POST | `/api/ai/predict/environment` |
| AI | 设备故障预测 | POST | `/api/ai/predict/device-failure` |
| AI | 异常检测 | POST | `/api/ai/detect/anomalies` |
| AI | 智能分析报告 | POST | `/api/ai/generate/report` |
| AI | 自然语言查询 | POST | `/api/ai/query` |
| AI | 环境数据分析 | GET | `/api/ai/analyze/environment` |
| 报告 | 获取报告列表 | GET | `/api/reports` |
| 报告 | 获取报告详情 | GET | `/api/reports/{reportId}` |
| 报告 | 生成报告 | POST | `/api/reports/generate` |

---

**文档版本**：v1.1  
**生成日期**：2026-05-22  
**适用项目**：智能巡检系统  
**接口覆盖率**：100%

---

## 测试结果

**测试日期**：2026-05-22  
**测试脚本**：test_api.py  
**测试结果**：14/14 通过  
**通过率**：100%

### 核心接口测试状态

| 接口名称 | 方法 | 路径 | 状态 |
| :--- | :---: | :--- | :---: |
| 用户登录 | POST | `/api/auth/login` | ✅ 通过 |
| 系统状态 | GET | `/api/system/status` | ✅ 通过 |
| 用户列表 | GET | `/api/users` | ✅ 通过 |
| 设备列表 | GET | `/api/devices` | ✅ 通过 |
| 设备统计 | GET | `/api/devices/stats` | ✅ 通过 |
| 机器人列表 | GET | `/api/robot` | ✅ 通过 |
| 机器人位置 | GET | `/api/robot/positions` | ✅ 通过 |
| 传感器列表 | GET | `/api/sensors` | ✅ 通过 |
| 环境数据 | GET | `/api/environment/latest` | ✅ 通过 |
| 告警列表 | GET | `/api/alerts` | ✅ 通过 |
| 消息列表 | GET | `/api/messages` | ✅ 通过 |
| 报告列表 | GET | `/api/reports` | ✅ 通过 |
| 系统日志 | GET | `/api/system/logs` | ✅ 通过 |
| 热成像数据 | GET | `/api/sse/latest-data` | ✅ 通过 |

**备注**：数据库当前为空，所有列表接口返回空数据属正常行为。