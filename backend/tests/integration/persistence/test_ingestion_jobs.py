import pytest
from uuid import uuid4

from src.domain.entities.ingestion_job import IngestionJob
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.value_objects.ingestion import JobStatus, ProcessingMode
from src.infrastructure.persistence.mysql.models import UploadArtifactModel
from src.infrastructure.persistence.mysql.repositories.ingestion_job_repository import (
    MySQLIngestionJobRepository,
)


@pytest.fixture
async def artifact_model(db_session, project: Project, owner: User):
    artifact = UploadArtifactModel(
        id=str(uuid4()),
        project_id=project.id,
        source_id=None,
        file_format="CSV",
        stored_path=f"{project.id}/raw.csv",
        original_filename="raw.csv",
        size_bytes=100,
        created_by=owner.id,
    )
    db_session.add(artifact)
    await db_session.flush()
    return artifact


@pytest.mark.asyncio
async def test_create_and_update_job(
    ingestion_job_repo: MySQLIngestionJobRepository,
    project: Project,
    artifact_model: UploadArtifactModel,
):
    job = IngestionJob.new(
        project_id=project.id,
        artifact_id=artifact_model.id,
        total_rows=1000,
        mode=ProcessingMode.ASYNC,
    )
    job.id = str(uuid4())

    created = await ingestion_job_repo.create(job)
    assert created.status == JobStatus.PENDING

    await ingestion_job_repo.update_status(
        created.id,
        JobStatus.RUNNING,
        processed_rows=500,
    )
    await ingestion_job_repo.update_status(
        created.id,
        JobStatus.COMPLETED,
        processed_rows=1000,
        result_path=f"{project.id}/clean.parquet",
    )

    stored = await ingestion_job_repo.get(created.id)
    assert stored is not None
    assert stored.status == JobStatus.COMPLETED
    assert stored.result_path.endswith("clean.parquet")

    jobs = await ingestion_job_repo.list(project.id)
    assert any(j.id == created.id for j in jobs)
