# 项目目录结构

## 概述

本项目是一个基于 FastAPI 的后端服务，采用分层架构设计，主要包含 RESTful API 和 Socket 服务器两大模块。

---

## 目录结构

```
FastAPIProject/
├── .idea/                    # IDE 配置文件（自动生成）
├── .venv/                    # Python 虚拟环境
├── __pycache__/              # Python 字节码缓存
├── app/                      # 主应用目录
│   ├── config/               # 配置模块
│   ├── crud/                 # CRUD 操作层
│   ├── dependencies/         # 依赖注入
│   ├── models/               # 数据库模型（SQLAlchemy）
│   ├── routers/              # API 路由
│   ├── schemas/              # Pydantic 数据模型
│   ├── services/             # 业务逻辑层
│   └── utils/                # 工具函数
├── socket_server/            # Socket 服务器模块
├── .env                      # 环境变量配置
├── API_DOCUMENTATION.md      # API 文档
├── inspection_system.sql     # 数据库初始化脚本
├── main.py                   # 项目入口文件
└── requirements.txt          # Python 依赖列表
```

---

## 模块说明

### 1. app/config/

| 文件 | 说明 |
|------|------|
| `database.py` | 数据库连接配置（SQLAlchemy Engine 和 Session） |
| `settings.py` | 应用配置（环境变量读取、配置参数） |

### 2. app/crud/

| 文件 | 说明 |
|------|------|
| `__init__.py` | 模块初始化 |
| `base.py` | CRUD 基类（通用增删改查方法） |
| `user.py` | 用户数据操作 |
| `device.py` | 设备数据操作 |
| `sensor.py` | 传感器数据操作 |
| `sensor_data.py` | 传感器采集数据操作 |
| `thermal_data.py` | 热成像数据操作 |
| `alert.py` | 告警数据操作 |
| `robot.py` | 机器人数据操作 |
| `message.py` | 消息数据操作 |
| `report.py` | 报表数据操作 |
| `system_config.py` | 系统配置操作 |
| `system_log.py` | 系统日志操作 |

### 3. app/dependencies/

| 文件 | 说明 |
|------|------|
| `auth.py` | 认证依赖（Token 验证、用户权限检查） |

### 4. app/models/

| 文件 | 说明 |
|------|------|
| `__init__.py` | 模型导出 |
| `user.py` | 用户模型 |
| `device.py` | 设备模型 |
| `sensor.py` | 传感器模型 |
| `sensor_data.py` | 传感器数据模型 |
| `thermal_data.py` | 热成像数据模型 |
| `alert.py` | 告警模型 |
| `robot.py` | 机器人模型 |
| `robot_position_history.py` | 机器人位置历史模型 |
| `message.py` | 消息模型 |
| `report.py` | 报表模型 |
| `system_config.py` | 系统配置模型 |
| `system_log.py` | 系统日志模型 |
| `environment_data.py` | 环境数据模型 |
| `ai_prediction.py` | AI 预测模型 |

### 5. app/routers/

| 文件 | 说明 |
|------|------|
| `__init__.py` | 路由导出 |
| `auth_router.py` | 认证路由（登录、注册） |
| `user_router.py` | 用户管理路由 |
| `device_router.py` | 设备管理路由 |
| `sensor_router.py` | 传感器管理路由 |
| `thermal_router.py` | 热成像数据路由 |
| `alert_router.py` | 告警管理路由 |
| `robot_router.py` | 机器人管理路由 |
| `message_router.py` | 消息管理路由 |
| `report_router.py` | 报表路由 |
| `system_router.py` | 系统配置路由 |
| `environment_router.py` | 环境数据路由 |
| `ai_router.py` | AI 预测路由 |

### 6. app/schemas/

| 文件 | 说明 |
|------|------|
| `__init__.py` | 模型导出 |
| `auth.py` | 认证请求/响应模型 |
| `user.py` | 用户请求/响应模型 |
| `device.py` | 设备请求/响应模型 |
| `sensor.py` | 传感器请求/响应模型 |
| `thermal.py` | 热成像数据模型 |
| `alert.py` | 告警请求/响应模型 |
| `robot.py` | 机器人请求/响应模型 |
| `message.py` | 消息请求/响应模型 |
| `report.py` | 报表请求/响应模型 |
| `system.py` | 系统配置模型 |
| `environment.py` | 环境数据模型 |
| `ai.py` | AI 预测模型 |
| `common.py` | 通用模型（分页、响应包装等） |

### 7. app/services/

| 文件 | 说明 |
|------|------|
| `__init__.py` | 服务导出 |
| `auth_service.py` | 认证服务（密码验证、Token 生成） |
| `user_service.py` | 用户服务 |
| `device_service.py` | 设备服务 |
| `sensor_service.py` | 传感器服务 |
| `alert_service.py` | 告警服务 |
| `robot_service.py` | 机器人服务 |
| `message_service.py` | 消息服务 |
| `report_service.py` | 报表服务 |
| `system_service.py` | 系统服务 |
| `ai_service.py` | AI 服务 |

### 8. app/utils/

| 文件 | 说明 |
|------|------|
| `logger.py` | 日志配置 |
| `response.py` | 统一响应格式封装 |
| `security.py` | 安全工具（密码哈希、加密等） |

### 9. socket_server/

| 文件 | 说明 |
|------|------|
| `__init__.py` | 模块初始化 |
| `socket_server.py` | Socket 服务器主逻辑 |
| `data_validator.py` | 数据验证器 |
| `data_storage.py` | 数据存储处理 |

---

## 核心文件

| 文件 | 说明 |
|------|------|
| `main.py` | 项目入口，FastAPI 应用实例创建 |
| `requirements.txt` | Python 依赖包列表 |
| `.env` | 环境变量（数据库连接、密钥等） |
| `inspection_system.sql` | 数据库初始化 SQL 脚本 |

---

## 架构说明

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (routers)                    │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer (services)                 │
├─────────────────────────────────────────────────────────────┤
│                      CRUD Layer (crud)                      │
├─────────────────────────────────────────────────────────────┤
│                    Model Layer (models)                     │
├─────────────────────────────────────────────────────────────┤
│                        Database                             │
└─────────────────────────────────────────────────────────────┘
```

采用经典的分层架构：
- **路由层**：处理 HTTP 请求，参数校验，调用服务层
- **服务层**：业务逻辑处理，事务管理
- **CRUD 层**：数据库操作封装
- **模型层**：数据库表映射
- **数据层**：数据库持久化