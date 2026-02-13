from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.domain.value_objects.ingestion import JobStatus
from src.infrastructure.queue.tasks import ingestion_task


@pytest.mark.asyncio
async def test_run_job_successfully_updates_status(mocker):
    repo = mocker.AsyncMock()
    mocker.patch(
        "src.infrastructure.queue.tasks.ingestion_task.MySQLIngestionJobRepository",
        return_value=repo,
    )
    session_cm = mocker.AsyncMock()
    session_cm.__aenter__.return_value = mocker.Mock()
    mocker.patch(
        "src.infrastructure.queue.tasks.ingestion_task.async_session_maker",
        return_value=session_cm,
    )
    mocker.patch(
        "src.infrastructure.queue.tasks.ingestion_task._process_artifact",
        return_value="proj-1/clean/file.json",
    )

    payload = {
        "job_id": "job-1",
        "project_id": "proj-1",
        "artifact_id": "artifact-1",
        "artifact_path": "proj-1/raw/file.csv",
        "file_format": "CSV",
        "total_rows": 200,
        "rules": [],
    }

    await ingestion_task._run_job(payload)

    repo.update_status.assert_any_call("job-1", JobStatus.RUNNING, processed_rows=0)
    repo.update_status.assert_any_call(
        "job-1",
        JobStatus.COMPLETED,
        processed_rows=200,
        result_path="proj-1/clean/file.json",
    )


@pytest.mark.asyncio
async def test_run_job_records_failure(mocker):
    repo = mocker.AsyncMock()
    mocker.patch(
        "src.infrastructure.queue.tasks.ingestion_task.MySQLIngestionJobRepository",
        return_value=repo,
    )
    session_cm = mocker.AsyncMock()
    session_cm.__aenter__.return_value = mocker.Mock()
    mocker.patch(
        "src.infrastructure.queue.tasks.ingestion_task.async_session_maker",
        return_value=session_cm,
    )
    mocker.patch(
        "src.infrastructure.queue.tasks.ingestion_task._process_artifact",
        side_effect=ValueError("boom"),
    )

    payload = {
        "job_id": "job-2",
        "project_id": "proj-1",
        "artifact_id": "artifact-2",
        "artifact_path": "proj-1/raw/file.csv",
        "file_format": "CSV",
        "total_rows": 10,
        "rules": [],
    }

    with pytest.raises(ValueError):
        await ingestion_task._run_job(payload)

    repo.update_status.assert_any_call("job-2", JobStatus.FAILED, error_message="boom")


@pytest.mark.asyncio
async def test_process_artifact_filters_rows(tmp_path, monkeypatch):
    artifact_path = tmp_path / "proj-1" / "raw"
    artifact_path.mkdir(parents=True)
    csv_file = artifact_path / "file.csv"
    csv_file.write_text("amount,name\n-5,Alice\n20,Bob\n", encoding="utf-8")

    monkeypatch.setattr(ingestion_task.settings, "upload_base_dir", tmp_path)

    payload = {
        "project_id": "proj-1",
        "artifact_id": "artifact-9",
        "artifact_path": "proj-1/raw/file.csv",
        "file_format": "CSV",
        "rules": [
            {
                "id": "rule-1",
                "field": "amount",
                "rule_type": "RANGE",
                "params": {"min": 0},
                "message": None,
            }
        ],
    }

    result_path = await ingestion_task._process_artifact(payload)

    output = tmp_path / result_path
    assert output.exists()
    records = json.loads(output.read_text(encoding="utf-8"))
    assert records == [{"amount": 20, "name": "Bob"}]
