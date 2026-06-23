from app.services.auth_service import AuthService
from app.services.robot_service import RobotService
from app.services.device_service import DeviceService
from app.services.sensor_service import SensorService
from app.services.alert_service import AlertService
from app.services.message_service import MessageService
from app.services.user_service import UserService
from app.services.system_service import SystemService
from app.services.deepseek_service import deepseek_service
from app.services.report_service import ReportService
from app.services.agent_service import AgentService

auth_service = AuthService()
robot_service = RobotService()
device_service = DeviceService()
sensor_service = SensorService()
alert_service = AlertService()
message_service = MessageService()
user_service = UserService()
system_service = SystemService()
report_service = ReportService()
agent_service = AgentService()