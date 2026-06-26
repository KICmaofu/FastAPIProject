# Schema导出
from app.schemas.common import ApiResponse, PagedData, PagedResponse, PasswordVerifyRequest, IdRequest, StatusRequest
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserInfoResponse, LoginResponse,
    UserAddRequest, UserUpdateRequest, ResetPwdRequest, UserDeleteRequest
)
from app.schemas.robot import (
    RobotInfo, RobotStatistics, RobotAddRequest, RobotUpdateRequest,
    RobotDeleteRequest, SendCmdRequest, CmdRecordInfo, SensorDataInfo
)
from app.schemas.patrol import (
    PatrolTaskInfo, PatrolTaskStatistics, PatrolTaskAddRequest,
    PatrolTaskUpdateRequest, PatrolTaskDeleteRequest, PatrolTaskStatusRequest,
    PatrolRecordInfo, PatrolRecordStatistics, StartPatrolRequest, EndPatrolRequest
)
from app.schemas.alarm import (
    AlarmInfo, AlarmDetail, AlarmStatistics, AlarmTrend,
    DealAlarmRequest, AlarmDeleteRequest
)
from app.schemas.report import EnvTrendData, AlarmTrendData, DailyReport, SensorStatistics
from app.schemas.ai import (
    AlarmAnalyzeRequest, AlarmAnalyzeResponse, AiChatRequest,
    AiChatResponse, AiChatRecord, ReportAnalyzeRequest
)
from app.schemas.system import LogInfo