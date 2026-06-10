from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user, require_admin
from app.models.user import User
from app.services import report_service
from app.schemas.report import ReportResponse, ReportCreate, ReportListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/reports", tags=["报告模块"])

@router.get("", summary="获取报告列表")
async def get_report_list(
    type: Optional[str] = Query(None, regex="^(daily|weekly|monthly)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = report_service.get_report_list(db, type, page, size)

    report_list = []
    for report in result["list"]:
        report_list.append(ReportResponse(
            id=report.id,
            type=report.type,
            title=report.title,
            content=report.content,
            startTime=report.start_time.isoformat(),
            endTime=report.end_time.isoformat(),
            createTime=report.create_time.isoformat()
        ))

    return success_response(data={
        "list": report_list,
        "total": result["total"],
        "page": result["page"]
    })

@router.get("/{reportId}", summary="获取报告详情")
async def get_report_detail(
    reportId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    report = report_service.get_report_by_id(db, reportId)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
    return success_response(data=ReportResponse(
        id=report.id,
        type=report.type,
        title=report.title,
        content=report.content,
        startTime=report.start_time.isoformat(),
        endTime=report.end_time.isoformat(),
        createTime=report.create_time.isoformat()
    ))

@router.post("/generate", summary="生成报告")
async def generate_report(
    request: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    report = report_service.generate_report(db, request, current_user.id)
    return success_response(data=ReportResponse(
        id=report.id,
        type=report.type,
        title=report.title,
        content=report.content,
        startTime=report.start_time.isoformat(),
        endTime=report.end_time.isoformat(),
        createTime=report.create_time.isoformat()
    ), message="生成成功")
