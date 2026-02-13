from __future__ import annotations

import io
from uuid import uuid4

import pandas as pd
import pytest
from starlette.datastructures import UploadFile

from src.application.services.ingestion_service import IngestionService
from src.domain.entities.data_source import DataSource
from src.domain.value_objects.ingestion import (
    CleaningRule,
    CleaningRuleType,
    FileFormat,
    JobStatus,
    ProcessingMode,
)


@pytest.fixture
def service(mocker):
    data_source_repo = mocker.AsyncMock()
    job_repo = mocker.AsyncMock()
    storage = mocker.AsyncMock()
    preview_cache = mocker.AsyncMock()
    task_queue = mocker.AsyncMock()

    return IngestionService(
        data_source_repo=data_source_repo,
        job_repo=job_repo,
        storage=storage,
        preview_cache=preview_cache,
        task_queue=task_queue,
        preview_ttl=30,
        sync_file_size_limit=1024 * 1024,
        sync_row_limit=100,
    )


@pytest.mark.asyncio
async def test_sync_file_under_threshold(service, mocker):
    csv_bytes = b"name,amount\nAlice,10\nBob,20\n"
    upload = UploadFile(filename="small.csv", file=io.BytesIO(csv_bytes))

    job = mocker.Mock()
    job.status = JobStatus.COMPLETED
    service.job_repo.create.return_value = job

    result = await service.handle_file_upload(
        project_id="proj-1",
        user_id="user-9",
        upload=upload,
        rules=[],
    )

    assert result.mode == ProcessingMode.SYNC
    assert result.job.status == JobStatus.COMPLETED
    service.task_queue.enqueue.assert_not_called()
    service.storage.save.assert_awaited()
    assert len(result.preview_rows) == 2


@pytest.mark.asyncio
async def test_async_file_exceeds_threshold(service, mocker):
    service.sync_file_size_limit = 32  # bytes
    csv_bytes = b"name,amount\n" + b"x,1\n" * 200
    upload = UploadFile(filename="big.csv", file=io.BytesIO(csv_bytes))

    async def fake_create(job):
        job.id = str(uuid4())
        return job

    service.job_repo.create.side_effect = fake_create

    result = await service.handle_file_upload(
        project_id="proj-2",
        user_id="user-2",
        upload=upload,
        rules=[],
    )

    assert result.mode == ProcessingMode.ASYNC
    assert result.job.status == JobStatus.PENDING
    service.task_queue.enqueue.assert_awaited_once()


@pytest.mark.asyncio
async def test_mysql_ingestion_uses_fetcher(mocker):
    data_source_repo = mocker.AsyncMock()
    job_repo = mocker.AsyncMock()
    storage = mocker.AsyncMock()
    preview_cache = mocker.AsyncMock()
    task_queue = mocker.AsyncMock()

    source = DataSource.create_mysql(
        project_id="proj-3",
        name="CRM",
        host="localhost",
        port=3306,
        database="crm",
        username="crm",
        password="secret",
    )
    source.id = "src-1"
    data_source_repo.get.return_value = source

    dataframe = pd.DataFrame([{"name": "Ada", "amount": 5}])

    def fake_fetcher(config, limit):
        return dataframe, len(dataframe)

    async def fake_create(job):
        job.id = "job-mysql"
        return job

    job_repo.create.side_effect = fake_create

    service = IngestionService(
        data_source_repo=data_source_repo,
        job_repo=job_repo,
        storage=storage,
        preview_cache=preview_cache,
        task_queue=task_queue,
        mysql_fetcher=fake_fetcher,
    )

    result = await service.start_mysql_ingestion(
        project_id="proj-3",
        user_id="user-1",
        source_id="src-1",
        table="contacts",
        rules=[
            CleaningRule(
                id="r1",
                field="amount",
                rule_type=CleaningRuleType.RANGE,
                params={"min": 0},
            )
        ],
    )

    assert result.job.id == "job-mysql"
    assert result.row_count == 1
    storage.save.assert_awaited_once()
    preview_cache.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_apply_rules_to_cached_preview(service):
    service.preview_cache.get.return_value = [
        {"amount": -1, "name": "X"},
        {"amount": 5, "name": ""},
    ]
    rules = [
        CleaningRule(
            id="r1",
            field="amount",
            rule_type=CleaningRuleType.RANGE,
            params={"min": 0},
        ),
        CleaningRule(
            id="r2",
            field="name",
            rule_type=CleaningRuleType.NOT_NULL,
            params={},
        ),
    ]

    result = await service.apply_rules_to_preview("artifact-1", rules)

    assert len(result) == 2
    assert result[0]["is_valid"] is False
    assert result[1]["is_valid"] is False
