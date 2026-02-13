from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

import pandas as pd
from celery.utils.log import get_task_logger

from src.config import settings
from src.domain.services.cleaning_rule_engine import CleaningRuleEngine
from src.domain.value_objects.ingestion import (
    CleaningRule,
    CleaningRuleType,
    FileFormat,
    JobStatus,
)
from src.infrastructure.persistence.mysql.database import async_session_maker
from src.infrastructure.persistence.mysql.repositories.ingestion_job_repository import (
    MySQLIngestionJobRepository,
)
from src.infrastructure.queue.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="ingestion.run_async_job", bind=True)
def run_async_job(self, **payload: Any) -> None:
    """Entry-point for asynchronous ingestion processing."""
    asyncio.run(_run_job(payload))


async def _run_job(payload: dict[str, Any]) -> None:
    job_id: str = payload["job_id"]
    async with async_session_maker() as session:
        repo = MySQLIngestionJobRepository(session)
        try:
            await repo.update_status(job_id, JobStatus.RUNNING, processed_rows=0)
            result_path = await _process_artifact(payload)
            total_rows = payload.get("total_rows")
            await repo.update_status(
                job_id,
                JobStatus.COMPLETED,
                processed_rows=total_rows,
                result_path=result_path,
            )
        except Exception as exc:  # pragma: no cover - logged & re-raised for Celery visibility
            logger.exception("Async ingestion job %s failed", job_id)
            await repo.update_status(job_id, JobStatus.FAILED, error_message=str(exc))
            raise


async def _process_artifact(payload: dict[str, Any]) -> str:
    artifact_rel_path = Path(payload["artifact_path"])
    full_path = (
        artifact_rel_path
        if artifact_rel_path.is_absolute()
        else settings.upload_base_dir / artifact_rel_path
    )
    file_format = FileFormat(payload.get("file_format", FileFormat.CSV.value))
    dataframe = _read_dataframe(file_format, full_path)
    rules = _deserialize_rules(payload.get("rules", []))
    engine = CleaningRuleEngine()

    cleaned_records: list[dict[str, Any]] = []
    for row in dataframe.to_dict(orient="records"):
        result = engine.apply(row, rules)
        if result["is_valid"]:
            cleaned_records.append(result["record"])

    relative_output = Path(payload["project_id"]) / "clean" / f"{payload['artifact_id']}.json"
    output_path = settings.upload_base_dir / relative_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(cleaned_records, ensure_ascii=False), encoding="utf-8")
    return str(relative_output).replace("\\", "/")


def _read_dataframe(file_format: FileFormat, path: Path) -> pd.DataFrame:
    if file_format == FileFormat.XLSX:
        return pd.read_excel(path)
    if file_format == FileFormat.TXT:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def _deserialize_rules(rule_payload: list[dict[str, Any]]) -> list[CleaningRule]:
    rules: list[CleaningRule] = []
    for raw in rule_payload:
        rules.append(
            CleaningRule(
                id=raw.get("id", ""),
                field=raw["field"],
                rule_type=CleaningRuleType(raw["rule_type"]),
                params=raw.get("params", {}),
                message=raw.get("message"),
            )
        )
    return rules
