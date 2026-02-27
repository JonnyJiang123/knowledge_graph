"""备份后台任务"""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from celery.utils.log import get_task_logger

from src.application.commands.backup_project import BackupService
from src.config import settings
from src.infrastructure.queue.celery_app import celery_app

logger = get_task_logger(__name__)


class BackupJobStatus:
    """备份任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@celery_app.task(name="backup.run_backup_job", bind=True)
def run_backup_job(self, **payload: Any) -> None:
    """执行备份任务的入口点"""
    asyncio.run(_execute_backup_job(self, payload))


async def _execute_backup_job(task: Any, payload: dict[str, Any]) -> None:
    """执行备份任务"""
    job_id: str = payload["job_id"]
    project_ids: list[str] = payload.get("project_ids", [])
    include_graph: bool = payload.get("include_graph", True)
    include_documents: bool = payload.get("include_documents", True)

    logger.info("Starting backup job %s for %d projects", job_id, len(project_ids))

    task.update_state(
        state=BackupJobStatus.RUNNING,
        meta={"progress": 0, "current_step": "Initializing"},
    )

    try:
        # 初始化备份服务
        backup_service = BackupService(str(settings.upload_base_dir / "backups"))

        task.update_state(
            state=BackupJobStatus.RUNNING,
            meta={"progress": 10, "current_step": "Backing up projects"},
        )

        # 执行备份
        if len(project_ids) == 1:
            result = await backup_service.backup_project(
                project_ids[0],
                include_graph,
                include_documents
            )
        else:
            result = await backup_service.backup_multiple(
                project_ids,
                include_graph,
                include_documents
            )

        task.update_state(
            state=BackupJobStatus.RUNNING,
            meta={"progress": 90, "current_step": "Finalizing"},
        )

        if result.status == "failed":
            task.update_state(
                state=BackupJobStatus.FAILED,
                meta={"error": result.errors, "backup_id": result.backup_id},
            )
            logger.error("Backup job %s failed: %s", job_id, result.errors)
        else:
            task.update_state(
                state=BackupJobStatus.COMPLETED,
                meta={
                    "progress": 100,
                    "backup_id": result.backup_id,
                    "size_bytes": result.size_bytes,
                    "projects_backed_up": len(result.projects_backed_up),
                },
            )
            logger.info(
                "Backup job %s completed. Backup ID: %s, Size: %d bytes",
                job_id,
                result.backup_id,
                result.size_bytes,
            )

    except Exception as exc:
        logger.exception("Backup job %s failed", job_id)
        task.update_state(
            state=BackupJobStatus.FAILED,
            meta={"error": str(exc)},
        )
        raise
