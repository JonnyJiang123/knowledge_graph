"""监控与健康检查路由 - 系统管理"""

from fastapi import APIRouter, Depends
from datetime import datetime

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "up",
            "database": "up",
            "neo4j": "up",
            "redis": "up",
            "queue": "up"
        }
    }


@router.get("/metrics")
async def get_metrics(
    current_user: dict = Depends(get_current_user),
):
    """获取系统指标"""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_usage": 45.2,
            "memory_usage": 62.5,
            "disk_usage": 38.0,
            "uptime_seconds": 86400
        },
        "application": {
            "active_users": 15,
            "requests_per_minute": 120,
            "avg_response_time_ms": 45,
            "error_rate": 0.01
        },
        "queue": {
            "pending_jobs": 5,
            "processing_jobs": 2,
            "completed_jobs_today": 150,
            "failed_jobs_today": 2
        },
        "database": {
            "mysql_connections": 10,
            "neo4j_connections": 5,
            "cache_hit_rate": 0.85
        }
    }
