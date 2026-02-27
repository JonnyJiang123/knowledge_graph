"""后台任务状态路由"""

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """获取任务状态"""
    # 查询任务状态
    # 示例返回
    return {
        "job_id": job_id,
        "status": "completed",  # pending, running, completed, failed
        "type": "extraction",
        "created_at": "2026-02-27T10:00:00Z",
        "started_at": "2026-02-27T10:00:05Z",
        "completed_at": "2026-02-27T10:05:00Z",
        "result": {
            "entities_extracted": 100,
            "relations_extracted": 50
        },
        "error": None
    }


@router.get("/{job_id}/progress")
async def get_job_progress(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """获取任务进度"""
    return {
        "job_id": job_id,
        "status": "running",
        "progress": {
            "total": 1000,
            "processed": 450,
            "percentage": 45.0,
            "estimated_remaining_seconds": 120
        },
        "current_stage": "extracting_relations",
        "stages": [
            {"name": "preprocessing", "status": "completed"},
            {"name": "extracting_entities", "status": "completed"},
            {"name": "extracting_relations", "status": "running"},
            {"name": "saving_results", "status": "pending"}
        ]
    }
