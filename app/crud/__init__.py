from app.crud.user import CRUDUser
from app.crud.robot import CRUDRobot
from app.crud.device import CRUDDevice
from app.crud.sensor import CRUDSensor
from app.crud.sensor_data import CRUDSensorData
from app.crud.thermal_data import CRUDThermalData
from app.crud.alert import CRUDAlert
from app.crud.message import CRUDMessage
from app.crud.report import CRUDReport
from app.crud.system_config import CRUDSystemConfig
from app.crud.system_log import CRUDSystemLog

user = CRUDUser()
robot = CRUDRobot()
device = CRUDDevice()
sensor = CRUDSensor()
sensor_data = CRUDSensorData()
thermal_data = CRUDThermalData()
alert = CRUDAlert()
message = CRUDMessage()
report = CRUDReport()
system_config = CRUDSystemConfig()
system_log = CRUDSystemLog()