from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.domain.entities.data_source import DataSource
from src.domain.entities.ingestion_job import IngestionJob
from src.domain.services.cleaning_rule_engine import CleaningRule, CleaningRuleEngine
from src.domain.value_objects.ingestion import (
    CleaningRuleType,
    DataSourceType,
    FileFormat,
    JobStatus,
    ProcessingMode,
)


def test_data_source_masks_secret_in_summary() -> None:
    source = DataSource.create_mysql(
        project_id="proj-1",
        name="CRM",
        host="localhost",
        port=3306,
        database="crm_db",
        username="crm_user",
        password="plain-secret",
    )

    summary = source.safe_summary()

    assert summary["type"] == DataSourceType.MYSQL
    assert summary["config"]["password"] == "********"
    assert summary["config"]["host"] == "localhost"


def test_file_data_source_records_metadata() -> None:
    uploaded_at = datetime.now(UTC)
    source = DataSource.create_file(
        project_id="proj-1",
        name="quarterly-report",
        file_format=FileFormat.CSV,
        original_filename="report.csv",
        stored_path="storage/uploads/proj-1/report.csv",
        size_bytes=1024,
        uploaded_by="user-1",
        uploaded_at=uploaded_at,
    )

    assert source.type == DataSourceType.FILE
    assert source.config["file_format"] == FileFormat.CSV
    assert source.config["size_bytes"] == 1024
    assert source.config["uploaded_by"] == "user-1"


def test_ingestion_job_transitions_and_progress() -> None:
    job = IngestionJob.new(
        project_id="proj-1",
        artifact_id="artifact-1",
        total_rows=12000,
        mode=ProcessingMode.ASYNC,
    )

    assert job.status == JobStatus.PENDING
    job.start()
    assert job.status == JobStatus.RUNNING

    with pytest.raises(ValueError):
        job.complete(processed_rows=100, result_path=None)

    job.update_progress(processed_rows=6000)
    assert job.progress == pytest.approx(0.5)

    job.complete(processed_rows=12000, result_path="storage/uploads/proj-1/clean.parquet")
    assert job.status == JobStatus.COMPLETED
    assert job.result_path == "storage/uploads/proj-1/clean.parquet"


def test_cleaning_rule_engine_detects_invalid_records() -> None:
    rules = [
        CleaningRule(
            id=str(uuid4()),
            field="amount",
            rule_type=CleaningRuleType.RANGE,
            params={"min": 0, "max": 1000},
        ),
        CleaningRule(
            id=str(uuid4()),
            field="name",
            rule_type=CleaningRuleType.NOT_NULL,
            params={},
        ),
    ]
    record = {"amount": -5, "name": ""}

    result = CleaningRuleEngine().apply(record, rules)

    assert result["is_valid"] is False
    assert len(result["errors"]) == 2
    assert "amount" in result["errors"][0]
