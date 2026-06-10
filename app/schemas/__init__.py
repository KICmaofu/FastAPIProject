from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, ResetPasswordRequest
from app.schemas.robot import RobotCreate, RobotUpdate, RobotResponse, RobotPositionResponse, RobotControlRequest
from app.schemas.thermal import ThermalDataResponse, ThermalDataHistoryRequest
from app.schemas.environment import EnvironmentDataResponse, EnvironmentHistoryRequest
from app.schemas.alert import AlertResponse, AlertProcessRequest, AlertListRequest
from app.schemas.device import DeviceResponse, DeviceStatsResponse, DeviceCreate, DeviceUpdate
from app.schemas.sensor import SensorResponse
from app.schemas.message import MessageResponse, MessageListRequest
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserListRequest
from app.schemas.system import SystemStatusResponse, SystemLogRequest, SystemConfigUpdate
from app.schemas.ai import AIPredictionRequest, AIPredictionResponse, AIQueryRequest, AIDetectRequest
from app.schemas.report import ReportResponse, ReportCreate, ReportListRequest