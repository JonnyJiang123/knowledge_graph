from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional

from src.domain.value_objects.ingestion import JobStatus, ProcessingMode


@dataclass
class IngestionJob:
    id: str
    project_id: str
    artifact_id: str
    mode: ProcessingMode
    source_id: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    total_rows: int = 0
    processed_rows: int = 0
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @classmethod
    def new(
        cls,
        project_id: str,
        artifact_id: str,
        total_rows: int,
        mode: ProcessingMode,
        source_id: Optional[str] = None,
    ) -> "IngestionJob":
        return cls(
            id="",
            project_id=project_id,
            artifact_id=artifact_id,
            total_rows=total_rows,
            mode=mode,
            source_id=source_id,
            status=JobStatus.PENDING,
        )

    @property
    def progress(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return min(1.0, self.processed_rows / self.total_rows)

    def start(self) -> None:
        if self.status != JobStatus.PENDING:
            raise ValueError("Job can only be started from pending state")
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now(UTC)

    def update_progress(self, processed_rows: int) -> None:
        if self.status != JobStatus.RUNNING:
            raise ValueError("Cannot update progress unless job is running")
        self.processed_rows = processed_rows

    def complete(self, processed_rows: int, result_path: Optional[str]) -> None:
        if self.status != JobStatus.RUNNING:
            raise ValueError("Job must be running to complete")
        if result_path is None:
            raise ValueError("Completed jobs require a result path")

        self.processed_rows = processed_rows
        self.result_path = result_path
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now(UTC)

    def fail(self, message: str) -> None:
        self.status = JobStatus.FAILED
        self.error_message = message
        self.completed_at = datetime.now(UTC)
