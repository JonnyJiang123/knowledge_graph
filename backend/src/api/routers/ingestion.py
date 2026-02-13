from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.ingestion import (
    get_data_source_repo,
    get_ingestion_job_repo,
    get_ingestion_service,
    require_ingestion_project,
)
from src.api.schemas.ingestion import (
    CleaningRuleInput,
    CleaningRuleTemplate,
    DataSourceListResponse,
    DataSourceRequest,
    DataSourceResponse,
    FileUploadResponse,
    JobListResponse,
    JobResponse,
    MySQLConnectionTestRequest,
    MySQLConnectionTestResponse,
    MySQLImportRequest,
    PreviewApplyRequest,
    PreviewApplyResponseItem,
)
from src.application.commands import (
    RegisterMySQLDataSourceCommand,
    register_mysql_source,
)
from src.application.services.ingestion_service import IngestionService, UploadResult
from src.domain.entities.data_source import DataSource
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.ports.repositories import DataSourceRepository, IngestionJobRepository
from src.domain.value_objects.ingestion import CleaningRule, DataSourceType, JobStatus, ProcessingMode


router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])


CLEANING_TEMPLATES: list[CleaningRuleTemplate] = [
    CleaningRuleTemplate(
        key="not_null",
        label="Not Null",
        description="Ensure the field is not blank.",
        params_schema={},
    ),
    CleaningRuleTemplate(
        key="range",
        label="Numeric Range",
        description="Keep numbers between min/max boundaries.",
        params_schema={"min": {"type": "number"}, "max": {"type": "number"}},
    ),
    CleaningRuleTemplate(
        key="regex",
        label="Regex Match",
        description="Use a regular expression to validate the field.",
        params_schema={"pattern": {"type": "string"}},
    ),
]


def _map_rules(payload: list[CleaningRuleInput]) -> list[CleaningRule]:
    return [rule.to_domain() for rule in payload]


def _serialize_source(source: DataSource) -> DataSourceResponse:
    summary = source.safe_summary()
    return DataSourceResponse(
        id=summary["id"],
        project_id=summary["project_id"],
        name=summary["name"],
        type=summary["type"],
        status=summary["status"],
        config=summary["config"],
    )


def _to_upload_response(result: UploadResult) -> FileUploadResponse:
    return FileUploadResponse(
        artifact_id=result.artifact.artifact_id,
        job_id=result.job.id,
        mode=result.mode,
        status=result.job.status,
        preview_rows=result.preview_rows,
        row_count=result.row_count,
    )


@router.get("/templates/cleaning", response_model=list[CleaningRuleTemplate])
async def list_cleaning_templates():
    return CLEANING_TEMPLATES


@router.post("/sources/mysql/test", response_model=MySQLConnectionTestResponse)
async def test_mysql_source(payload: MySQLConnectionTestRequest):
    dsn = (
        f"mysql+asyncmy://{payload.username}:{payload.password}"
        f"@{payload.host}:{payload.port}/{payload.database}"
    )
    engine = create_async_engine(
        dsn,
        pool_pre_ping=True,
    )
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return MySQLConnectionTestResponse(success=True, message="Connection successful")
    except Exception as exc:  # pragma: no cover - errors reported to client
        return MySQLConnectionTestResponse(success=False, message=str(exc))
    finally:
        await engine.dispose()


@router.post("/sources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
async def create_data_source(
    project_id: Annotated[str, Query(..., description="Project identifier")],
    payload: DataSourceRequest,
    repo: Annotated[DataSourceRepository, Depends(get_data_source_repo)],
    project: Annotated[Project, Depends(require_ingestion_project)],
):
    if payload.project_id != project.id or payload.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project mismatch for ingestion source")

    if payload.type != DataSourceType.MYSQL or payload.mysql is None:
        raise HTTPException(status_code=400, detail="Only MySQL sources are supported in this phase")

    command = RegisterMySQLDataSourceCommand(
        project_id=payload.project_id,
        name=payload.name,
        host=payload.mysql.host,
        port=payload.mysql.port,
        database=payload.mysql.database,
        username=payload.mysql.username,
        password=payload.mysql.password,
    )
    source = await register_mysql_source(repo, command)
    return _serialize_source(source)


@router.get("/sources", response_model=DataSourceListResponse)
async def list_sources(
    project_id: Annotated[str, Query(..., description="Project identifier")],
    repo: Annotated[DataSourceRepository, Depends(get_data_source_repo)],
    project: Annotated[Project, Depends(require_ingestion_project)],
):
    items = await repo.list(project.id)
    responses = [_serialize_source(item) for item in items]
    return DataSourceListResponse(items=responses, total=len(responses))


@router.post("/upload/file", response_model=FileUploadResponse)
async def upload_file(
    project_id: Annotated[str, Form(...)],
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
    project: Annotated[Project, Depends(require_ingestion_project)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
    rules: Annotated[str | None, Form()] = None,
):
    rule_models = _map_rules(_parse_rule_inputs(rules))
    result = await service.handle_file_upload(
        project_id=project.id,
        user_id=current_user.id,
        upload=file,
        rules=rule_models,
    )
    return _to_upload_response(result)


@router.post("/preview", response_model=list[PreviewApplyResponseItem])
async def apply_cleaning_preview(
    payload: PreviewApplyRequest,
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
):
    results = await service.apply_rules_to_preview(
        artifact_id=payload.artifact_id,
        rules=_map_rules(payload.rules),
    )
    return [
        PreviewApplyResponseItem(record=item["record"], is_valid=item["is_valid"], errors=item["errors"])
        for item in results
    ]


@router.post("/mysql/import", response_model=FileUploadResponse)
async def start_mysql_import(
    project_id: Annotated[str, Query(..., description="Project identifier")],
    payload: MySQLImportRequest,
    service: Annotated[IngestionService, Depends(get_ingestion_service)],
    project: Annotated[Project, Depends(require_ingestion_project)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if payload.project_id != project.id or payload.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project mismatch for ingestion job")
    rule_models = _map_rules(payload.rules)
    result = await service.start_mysql_ingestion(
        project_id=project.id,
        user_id=current_user.id,
        source_id=payload.source_id,
        table=payload.table,
        rules=rule_models,
    )
    return _to_upload_response(result)


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    project_id: Annotated[str, Query(...)],
    repo: Annotated[IngestionJobRepository, Depends(get_ingestion_job_repo)],
    project: Annotated[Project, Depends(require_ingestion_project)],
):
    jobs = await repo.list(project.id)
    responses = [_serialize_job(job) for job in jobs]
    return JobListResponse(items=responses, total=len(responses))


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    project_id: Annotated[str, Query(...)],
    repo: Annotated[IngestionJobRepository, Depends(get_ingestion_job_repo)],
    project: Annotated[Project, Depends(require_ingestion_project)],
):
    job = await repo.get(job_id)
    if not job or job.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return _serialize_job(job)


@router.get("/jobs/{job_id}/logs")
async def job_logs(
    job_id: str,
    project_id: Annotated[str, Query(...)],
    repo: Annotated[IngestionJobRepository, Depends(get_ingestion_job_repo)],
    project: Annotated[Project, Depends(require_ingestion_project)],
):
    job = await repo.get(job_id)
    if not job or job.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return {
        "job_id": job_id,
        "entries": [
            {"level": "INFO", "message": f"Ingestion job {job_id} is {job.status}", "timestamp": job.created_at},
        ],
    }


def _serialize_job(job) -> JobResponse:
    return JobResponse(
        id=job.id,
        project_id=job.project_id,
        artifact_id=job.artifact_id,
        mode=job.mode,
        status=job.status,
        total_rows=job.total_rows,
        processed_rows=job.processed_rows,
        result_path=job.result_path,
        error_message=job.error_message,
    )


def _parse_rule_inputs(raw_rules: str | None) -> list[CleaningRuleInput]:
    if not raw_rules:
        return []
    try:
        data = json.loads(raw_rules)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rules payload: {exc}") from exc
    return [CleaningRuleInput(**item) for item in data]
