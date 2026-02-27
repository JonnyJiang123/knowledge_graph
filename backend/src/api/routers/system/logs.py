"""系统日志路由 - 系统管理"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/system/logs", tags=["system"])


@router.get("")
async def query_logs(
    level: Optional[str] = Query(None, description="日志级别"),
    service: Optional[str] = Query(None, description="服务名称"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """查询系统日志"""
    # 示例数据
    logs = [
        {
            "id": "log-1",
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "service": "api",
            "message": "系统启动成功",
            "user_id": None,
            "request_id": "req-001"
        },
        {
            "id": "log-2",
            "timestamp": datetime.now().isoformat(),
            "level": "WARNING",
            "service": "ingestion",
            "message": "数据摄取任务耗时较长",
            "user_id": "user-1",
            "request_id": "req-002"
        }
    ]

    if level:
        logs = [l for l in logs if l["level"] == level.upper()]

    return {
        "logs": logs[offset:offset + limit],
        "total": len(logs),
        "limit": limit,
        "offset": offset
    }


@router.get("/stats")
async def get_log_stats(
    current_user: dict = Depends(get_current_user),
):
    """获取日志统计"""
    return {
        "total_logs_today": 1500,
        "by_level": {
            "DEBUG": 500,
            "INFO": 800,
            "WARNING": 150,
            "ERROR": 45,
            "CRITICAL": 5
        },
        "by_service": {
            "api": 600,
            "ingestion": 400,
            "extraction": 300,
            "query": 200
        }
    }
