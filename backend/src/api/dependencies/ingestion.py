from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_user
from src.application.services.ingestion_service import IngestionService
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.ports.repositories import (
    DataSourceRepository,
    IngestionJobRepository,
    PreviewCachePort,
    TaskQueuePort,
)
from src.infrastructure.cache.in_memory import InMemoryPreviewCache
from src.infrastructure.persistence.mysql.database import get_db
from src.infrastructure.persistence.mysql.project_repository import MySQLProjectRepository
from src.infrastructure.persistence.mysql.repositories.data_source_repository import (
    MySQLDataSourceRepository,
)
from src.infrastructure.persistence.mysql.repositories.ingestion_job_repository import (
    MySQLIngestionJobRepository,
)
from src.infrastructure.queue.local_queue import LocalTaskQueue
from src.infrastructure.storage.local_storage import LocalFileStorage


@lru_cache(maxsize=1)
def _preview_cache() -> PreviewCachePort:
    return InMemoryPreviewCache()


@lru_cache(maxsize=1)
def _task_queue() -> TaskQueuePort:
    return LocalTaskQueue()


async def get_preview_cache() -> PreviewCachePort:
    return _preview_cache()


async def get_task_queue() -> TaskQueuePort:
    return _task_queue()


async def get_data_source_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DataSourceRepository:
    return MySQLDataSourceRepository(db)


async def get_ingestion_job_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IngestionJobRepository:
    return MySQLIngestionJobRepository(db)


async def get_ingestion_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    preview_cache: Annotated[PreviewCachePort, Depends(get_preview_cache)],
    task_queue: Annotated[TaskQueuePort, Depends(get_task_queue)],
) -> IngestionService:
    return IngestionService(
        data_source_repo=MySQLDataSourceRepository(db),
        job_repo=MySQLIngestionJobRepository(db),
        storage=LocalFileStorage(),
        preview_cache=preview_cache,
        task_queue=task_queue,
    )


async def require_ingestion_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Project:
    """Dedicated guard to centralize ingestion-specific project checks."""
    repo = MySQLProjectRepository(db)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not current_user.can_manage_project(project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have ingestion access to this project",
        )

    return project
