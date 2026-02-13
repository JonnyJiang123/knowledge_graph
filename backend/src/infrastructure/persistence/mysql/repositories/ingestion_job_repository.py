from __future__ import annotations

from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.ingestion_job import IngestionJob
from src.domain.ports.repositories import IngestionJobRepository
from src.domain.value_objects.ingestion import JobStatus, ProcessingMode
from src.infrastructure.persistence.mysql.models import IngestionJobModel


class MySQLIngestionJobRepository(IngestionJobRepository):
    """MySQL implementation of the ingestion job repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: IngestionJobModel) -> IngestionJob:
        return IngestionJob(
            id=model.id,
            project_id=model.project_id,
            artifact_id=model.artifact_id,
            source_id=model.source_id,
            mode=ProcessingMode(model.mode),
            status=JobStatus(model.status),
            total_rows=model.total_rows,
            processed_rows=model.processed_rows,
            result_path=model.result_path,
            error_message=model.error_message,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
        )

    def _to_model(self, job: IngestionJob) -> IngestionJobModel:
        return IngestionJobModel(
            id=job.id or str(uuid4()),
            project_id=job.project_id,
            artifact_id=job.artifact_id,
            source_id=job.source_id,
            mode=job.mode.value,
            status=job.status.value,
            total_rows=job.total_rows,
            processed_rows=job.processed_rows,
            result_path=job.result_path,
            error_message=job.error_message,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )

    async def create(self, job: IngestionJob) -> IngestionJob:
        model = self._to_model(job)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        processed_rows: Optional[int] = None,
        result_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        model = await self.session.get(IngestionJobModel, job_id)
        if model is None:
            raise ValueError(f"Ingestion job {job_id} not found")

        model.status = status.value
        if processed_rows is not None:
            model.processed_rows = processed_rows
        if result_path is not None:
            model.result_path = result_path
        if error_message is not None:
            model.error_message = error_message

        if status == JobStatus.RUNNING and model.started_at is None:
            from datetime import datetime, UTC

            model.started_at = datetime.now(UTC)
        if status in (JobStatus.COMPLETED, JobStatus.FAILED):
            from datetime import datetime, UTC

            model.completed_at = datetime.now(UTC)

        await self.session.commit()

    async def get(self, job_id: str) -> Optional[IngestionJob]:
        model = await self.session.get(IngestionJobModel, job_id)
        return self._to_entity(model) if model else None

    async def list(self, project_id: str) -> list[IngestionJob]:
        result = await self.session.execute(
            select(IngestionJobModel)
                .where(IngestionJobModel.project_id == project_id)
                .order_by(IngestionJobModel.created_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]
