from __future__ import annotations

import io
import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, Sequence
from uuid import uuid4

import aiofiles
import pandas as pd
from fastapi import UploadFile

from src.config import settings
from src.domain.entities.data_source import DataSource
from src.domain.entities.ingestion_job import IngestionJob
from src.domain.ports.repositories import (
    DataSourceRepository,
    FileStoragePort,
    IngestionJobRepository,
    PreviewCachePort,
    TaskQueuePort,
)
from src.domain.services.cleaning_rule_engine import CleaningRuleEngine
from src.domain.value_objects.ingestion import (
    CleaningRule,
    DataSourceType,
    FileArtifact,
    FileFormat,
    ProcessingMode,
)

MysqlFetcher = Callable[
    [dict[str, Any], int],
    Awaitable[tuple[pd.DataFrame, int]] | tuple[pd.DataFrame, int],
]


@dataclass
class UploadResult:
    artifact: FileArtifact
    job: IngestionJob
    mode: ProcessingMode
    preview_rows: list[dict[str, Any]]
    row_count: int


class IngestionService:
    """Coordinates ingestion commands across storage, repos, and preview cache."""

    def __init__(
        self,
        data_source_repo: DataSourceRepository,
        job_repo: IngestionJobRepository,
        storage: FileStoragePort,
        preview_cache: PreviewCachePort,
        task_queue: TaskQueuePort,
        *,
        cleaning_engine: CleaningRuleEngine | None = None,
        preview_ttl: int = 15 * 60,
        sync_file_size_limit: int | None = None,
        sync_row_limit: int | None = None,
        mysql_fetcher: Callable[[dict[str, Any], int], tuple[pd.DataFrame, int]] | MysqlFetcher | None = None,
        upload_base_dir: Path | None = None,
        pandas_module: Any = pd,
    ) -> None:
        self.data_source_repo = data_source_repo
        self.job_repo = job_repo
        self.storage = storage
        self.preview_cache = preview_cache
        self.task_queue = task_queue
        self.cleaning_engine = cleaning_engine or CleaningRuleEngine()
        self.preview_ttl = preview_ttl
        self.sync_file_size_limit = sync_file_size_limit or settings.sync_file_size_limit
        self.sync_row_limit = sync_row_limit or settings.sync_row_limit
        self.preview_row_limit = settings.preview_row_limit
        self._mysql_fetcher = mysql_fetcher
        self.clean_output_dir = Path(upload_base_dir or settings.upload_base_dir)
        self.clean_output_dir.mkdir(parents=True, exist_ok=True)
        self._pd = pandas_module

    async def handle_file_upload(
        self,
        *,
        project_id: str,
        user_id: str,
        upload: UploadFile,
        rules: Sequence[CleaningRule],
    ) -> UploadResult:
        contents = await upload.read()
        await upload.seek(0)
        file_format = self._detect_format(upload.filename or "upload")
        artifact = self._build_artifact(
            project_id=project_id,
            filename=upload.filename or "upload",
            file_format=file_format,
            size_bytes=len(contents),
            user_id=user_id,
        )
        await self.storage.save(artifact, contents)

        dataframe, row_count, preview_rows = self._profile_file(file_format, contents)
        cache_key = self._preview_cache_key(artifact.artifact_id)
        await self.preview_cache.set(cache_key, preview_rows, self.preview_ttl)

        mode = self._decide_mode(len(contents), row_count)
        job = self._build_job(project_id, artifact.artifact_id, row_count, mode)
        stored_job = await self._persist_job(job, artifact, rules, dataframe if mode == ProcessingMode.SYNC else None)

        if mode == ProcessingMode.ASYNC:
            await self.task_queue.enqueue(
                "ingestion.run_async_job",
                self._build_async_payload(
                    job_id=stored_job.id,
                    project_id=project_id,
                    artifact=artifact,
                    total_rows=row_count,
                    rules=rules,
                ),
            )

        return UploadResult(
            artifact=artifact,
            job=stored_job,
            mode=mode,
            preview_rows=preview_rows,
            row_count=row_count,
        )

    async def start_mysql_ingestion(
        self,
        *,
        project_id: str,
        user_id: str,
        source_id: str,
        table: str,
        rules: Sequence[CleaningRule],
    ) -> UploadResult:
        source = await self.data_source_repo.get(source_id)
        if source is None:
            raise ValueError("Data source not found")
        if source.type != DataSourceType.MYSQL:
            raise ValueError("Source is not MySQL")

        dataframe, total_rows = await self._fetch_mysql_dataframe(source, table)
        csv_bytes = dataframe.to_csv(index=False).encode("utf-8")
        artifact = self._build_artifact(
            project_id=project_id,
            filename=f"{table}.csv",
            file_format=FileFormat.CSV,
            size_bytes=len(csv_bytes),
            user_id=user_id,
        )
        await self.storage.save(artifact, csv_bytes)
        preview_rows = dataframe.head(self.preview_row_limit).to_dict(orient="records")
        await self.preview_cache.set(self._preview_cache_key(artifact.artifact_id), preview_rows, self.preview_ttl)

        mode = self._decide_mode(len(csv_bytes), total_rows)
        job = self._build_job(project_id, artifact.artifact_id, total_rows, mode, source.id)
        stored_job = await self._persist_job(job, artifact, rules, dataframe if mode == ProcessingMode.SYNC else None)

        if mode == ProcessingMode.ASYNC:
            await self.task_queue.enqueue(
                "ingestion.run_async_job",
                self._build_async_payload(
                    job_id=stored_job.id,
                    project_id=project_id,
                    artifact=artifact,
                    total_rows=total_rows,
                    rules=rules,
                ),
            )

        return UploadResult(
            artifact=artifact,
            job=stored_job,
            mode=mode,
            preview_rows=preview_rows,
            row_count=total_rows,
        )

    async def apply_rules_to_preview(
        self,
        artifact_id: str,
        rules: Sequence[CleaningRule],
    ) -> list[dict[str, Any]]:
        cached_rows = await self.preview_cache.get(self._preview_cache_key(artifact_id))
        if not cached_rows:
            return []

        return [self.cleaning_engine.apply(row, rules) for row in cached_rows]

    def _preview_cache_key(self, artifact_id: str) -> str:
        return f"preview:{artifact_id}"

    def _build_artifact(
        self,
        *,
        project_id: str,
        filename: str,
        file_format: FileFormat,
        size_bytes: int,
        user_id: str,
    ) -> FileArtifact:
        artifact_id = str(uuid4())
        safe_name = Path(filename).name.replace(" ", "_")
        stored_path = f"{project_id}/raw/{artifact_id}-{safe_name}"
        return FileArtifact(
            artifact_id=artifact_id,
            project_id=project_id,
            stored_path=stored_path,
            file_format=file_format,
            size_bytes=size_bytes,
            uploaded_by=user_id,
        )

    def _detect_format(self, filename: str) -> FileFormat:
        suffix = Path(filename).suffix.lower()
        mapping = {
            ".csv": FileFormat.CSV,
            ".txt": FileFormat.TXT,
            ".xlsx": FileFormat.XLSX,
            ".pdf": FileFormat.PDF,
            ".docx": FileFormat.DOCX,
        }
        return mapping.get(suffix, FileFormat.CSV)

    def _profile_file(
        self,
        file_format: FileFormat,
        contents: bytes,
    ) -> tuple[pd.DataFrame, int, list[dict[str, Any]]]:
        buffer = io.BytesIO(contents)
        if file_format in (FileFormat.CSV, FileFormat.TXT):
            df = self._pd.read_csv(buffer)
        elif file_format == FileFormat.XLSX:
            df = self._pd.read_excel(buffer)
        else:
            df = self._pd.DataFrame()
        row_count = int(df.shape[0])
        preview_rows = df.head(self.preview_row_limit).to_dict(orient="records")
        return df, row_count, preview_rows

    def _decide_mode(self, size_bytes: int, row_count: int) -> ProcessingMode:
        if size_bytes <= self.sync_file_size_limit and row_count <= self.sync_row_limit:
            return ProcessingMode.SYNC
        return ProcessingMode.ASYNC

    def _build_job(
        self,
        project_id: str,
        artifact_id: str,
        row_count: int,
        mode: ProcessingMode,
        source_id: str | None = None,
    ) -> IngestionJob:
        job = IngestionJob.new(
            project_id=project_id,
            artifact_id=artifact_id,
            total_rows=row_count,
            mode=mode,
            source_id=source_id,
        )
        job.id = str(uuid4())
        return job

    async def _persist_job(
        self,
        job: IngestionJob,
        artifact: FileArtifact,
        rules: Sequence[CleaningRule],
        dataframe: pd.DataFrame | None,
    ) -> IngestionJob:
        if job.mode == ProcessingMode.SYNC:
            job.start()
            df = dataframe if dataframe is not None else self._pd.DataFrame()
            result_path = await self._write_clean_output(artifact, df, rules)
            job.complete(processed_rows=job.total_rows, result_path=result_path)
        stored_job = await self.job_repo.create(job)
        return stored_job

    async def _write_clean_output(
        self,
        artifact: FileArtifact,
        dataframe: pd.DataFrame,
        rules: Sequence[CleaningRule],
    ) -> str:
        if dataframe.empty:
            cleaned_records: list[dict[str, Any]] = []
        else:
            cleaned_records = []
            for row in dataframe.to_dict(orient="records"):
                evaluation = self.cleaning_engine.apply(row, rules)
                if evaluation["is_valid"]:
                    cleaned_records.append(evaluation["record"])

        relative_path = Path(artifact.project_id) / "clean" / f"{artifact.artifact_id}.json"
        full_path = self.clean_output_dir / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(full_path, "w", encoding="utf-8") as stream:
            payload = json.dumps(cleaned_records, ensure_ascii=False)
            await stream.write(payload)
        return str(relative_path).replace("\\", "/")

    async def _fetch_mysql_dataframe(
        self,
        source: DataSource,
        table: str,
    ) -> tuple[pd.DataFrame, int]:
        if self._mysql_fetcher is None:
            raise RuntimeError("MySQL fetcher has not been configured for ingestion service")

        payload = dict(source.config)
        payload["table"] = table
        result = self._mysql_fetcher(payload, self.sync_row_limit)
        if inspect.isawaitable(result):
            dataframe, total_rows = await result  # type: ignore[assignment]
        else:
            dataframe, total_rows = result  # type: ignore[assignment]
        return dataframe, int(total_rows)

    def _build_async_payload(
        self,
        *,
        job_id: str,
        project_id: str,
        artifact: FileArtifact,
        total_rows: int,
        rules: Sequence[CleaningRule],
    ) -> dict[str, Any]:
        return {
            "job_id": job_id,
            "project_id": project_id,
            "artifact_id": artifact.artifact_id,
            "artifact_path": artifact.stored_path,
            "file_format": artifact.file_format.value,
            "total_rows": total_rows,
            "rules": [asdict(rule) for rule in rules],
        }
