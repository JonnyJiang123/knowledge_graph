import io
import json
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.dependencies.ingestion import (
    get_data_source_repo,
    get_ingestion_job_repo,
    get_ingestion_service,
    require_ingestion_project,
)
from src.api.dependencies.auth import get_current_user
from src.application.services.ingestion_service import UploadResult
from src.domain.entities.data_source import DataSource
from src.domain.entities.ingestion_job import IngestionJob
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.value_objects.ingestion import (
    CleaningRuleType,
    FileArtifact,
    FileFormat,
    JobStatus,
    ProcessingMode,
)
from src.main import app


class FakeIngestionService:
    async def handle_file_upload(self, **kwargs):
        artifact = FileArtifact(
            artifact_id="artifact-1",
            project_id=kwargs["project_id"],
            stored_path="proj/raw/file.csv",
            file_format=FileFormat.CSV,
            size_bytes=32,
            uploaded_by=kwargs["user_id"],
        )
        job = IngestionJob.new(
            project_id=kwargs["project_id"],
            artifact_id=artifact.artifact_id,
            total_rows=2,
            mode=ProcessingMode.SYNC,
        )
        job.id = "job-1"
        job.status = JobStatus.COMPLETED
        return UploadResult(
            artifact=artifact,
            job=job,
            mode=ProcessingMode.SYNC,
            preview_rows=[{"name": "Ada"}, {"name": "Bob"}],
            row_count=2,
        )

    async def start_mysql_ingestion(self, **kwargs):
        artifact = FileArtifact(
            artifact_id="artifact-2",
            project_id=kwargs["project_id"],
            stored_path="proj/raw/mysql.csv",
            file_format=FileFormat.CSV,
            size_bytes=64,
            uploaded_by=kwargs["user_id"],
        )
        job = IngestionJob.new(
            project_id=kwargs["project_id"],
            artifact_id=artifact.artifact_id,
            total_rows=5,
            mode=ProcessingMode.ASYNC,
        )
        job.id = "job-async"
        return UploadResult(
            artifact=artifact,
            job=job,
            mode=ProcessingMode.ASYNC,
            preview_rows=[{"name": "System"}],
            row_count=5,
        )

    async def apply_rules_to_preview(self, artifact_id, rules):
        return [
            {"record": {"amount": -1}, "is_valid": False, "errors": ["amount >= 0"]},
            {"record": {"amount": 10}, "is_valid": True, "errors": []},
        ]


class FakeDataSourceRepo:
    def __init__(self):
        self.created: list[DataSource] = []

    async def list(self, project_id: str):
        source = DataSource.create_mysql(
            project_id=project_id,
            name="CRM",
            host="localhost",
            port=3306,
            database="crm",
            username="crm",
            password="secret",
        )
        source.id = "src-1"
        return [source]

    async def create(self, source: DataSource):
        source.id = source.id or str(uuid4())
        self.created.append(source)
        return source


class FakeJobRepo:
    async def list(self, project_id: str):
        job = IngestionJob.new(
            project_id=project_id,
            artifact_id="artifact-1",
            total_rows=10,
            mode=ProcessingMode.ASYNC,
        )
        job.id = "job-list"
        return [job]

    async def get(self, job_id: str):
        job = IngestionJob.new(
            project_id="proj-1",
            artifact_id="artifact-1",
            total_rows=10,
            mode=ProcessingMode.ASYNC,
        )
        job.id = job_id
        return job


@pytest.fixture(autouse=True)
def override_ingestion_dependencies():
    fake_service = FakeIngestionService()
    fake_sources = FakeDataSourceRepo()
    fake_jobs = FakeJobRepo()
    app.dependency_overrides[get_ingestion_service] = lambda: fake_service
    app.dependency_overrides[get_data_source_repo] = lambda: fake_sources
    app.dependency_overrides[get_ingestion_job_repo] = lambda: fake_jobs
    app.dependency_overrides[require_ingestion_project] = lambda: Project(
        id="proj-1",
        name="Project",
        description=None,
        industry="FINANCE",
        owner_id="user-1",
    )
    app.dependency_overrides[get_current_user] = lambda: User(
        id="user-1",
        username="tester",
        email="tester@example.com",
        hashed_password="x",
    )
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_sources_returns_masked_config(client: AsyncClient):
    response = await client.get("/api/ingestion/sources", params={"project_id": "proj-1"})
    assert response.status_code == 200
    body = response.json()
    assert body["items"][0]["config"]["password"] == "********"


@pytest.mark.asyncio
async def test_upload_file_returns_preview(client: AsyncClient):
    rules = json.dumps(
        [
            {
                "field": "amount",
                "rule_type": CleaningRuleType.RANGE.value,
                "params": {"min": 0},
            }
        ]
    )
    files = {
        "file": ("sample.csv", io.BytesIO(b"name,amount\nAda,10\nBob,20\n"), "text/csv"),
    }
    data = {"project_id": "proj-1", "rules": rules}
    response = await client.post(
        "/api/ingestion/upload/file",
        data=data,
        files=files,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["artifact_id"] == "artifact-1"
    assert len(body["preview_rows"]) == 2


@pytest.mark.asyncio
async def test_apply_preview_rules(client: AsyncClient):
    payload = {
        "artifact_id": "artifact-1",
        "rules": [
            {
                "field": "amount",
                "rule_type": CleaningRuleType.RANGE.value,
                "params": {"min": 0},
            }
        ],
    }
    response = await client.post("/api/ingestion/preview", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body[0]["is_valid"] is False
