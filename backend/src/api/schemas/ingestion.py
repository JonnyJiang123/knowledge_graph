from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.domain.value_objects.ingestion import (
    CleaningRule,
    CleaningRuleType,
    DataSourceType,
    JobStatus,
    ProcessingMode,
)


class CleaningRuleTemplate(BaseModel):
    key: str
    label: str
    description: str
    params_schema: dict[str, Any] | None = None


class CleaningRuleInput(BaseModel):
    field: str
    rule_type: CleaningRuleType
    params: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None
    id: str | None = None

    def to_domain(self) -> CleaningRule:
        return CleaningRule(
            id=self.id or str(uuid4()),
            field=self.field,
            rule_type=self.rule_type,
            params=self.params,
            message=self.message,
        )


class MySQLConfig(BaseModel):
    host: str
    port: int = 3306
    database: str
    username: str
    password: str


class DataSourceRequest(BaseModel):
    project_id: str
    name: str
    type: DataSourceType
    mysql: Optional[MySQLConfig] = None


class DataSourceResponse(BaseModel):
    id: str
    project_id: str
    name: str
    type: DataSourceType
    status: str
    config: dict[str, Any]


class DataSourceListResponse(BaseModel):
    items: list[DataSourceResponse]
    total: int


class MySQLConnectionTestRequest(MySQLConfig):
    timeout_seconds: int | None = Field(default=5, ge=1, le=30)


class MySQLConnectionTestResponse(BaseModel):
    success: bool
    message: str | None = None


class FileUploadResponse(BaseModel):
    artifact_id: str
    job_id: str
    mode: ProcessingMode
    status: JobStatus
    preview_rows: list[dict[str, Any]]
    row_count: int


class PreviewApplyRequest(BaseModel):
    artifact_id: str
    rules: list[CleaningRuleInput] = Field(default_factory=list)


class PreviewApplyResponseItem(BaseModel):
    record: dict[str, Any]
    is_valid: bool
    errors: list[str]


class JobResponse(BaseModel):
    id: str
    project_id: str
    artifact_id: str
    mode: ProcessingMode
    status: JobStatus
    total_rows: int
    processed_rows: int
    result_path: str | None = None
    error_message: str | None = None


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int


class MySQLImportRequest(BaseModel):
    project_id: str
    source_id: str
    table: str
    rules: list[CleaningRuleInput] = Field(default_factory=list)
