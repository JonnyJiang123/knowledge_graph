from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from fastapi import UploadFile

from src.application.services.ingestion_service import IngestionService, UploadResult
from src.domain.value_objects.ingestion import CleaningRule


@dataclass
class StartFileIngestionCommand:
    project_id: str
    user_id: str
    upload: UploadFile
    rules: Sequence[CleaningRule]


@dataclass
class StartMySQLIngestionCommand:
    project_id: str
    user_id: str
    source_id: str
    table: str
    rules: Sequence[CleaningRule]


async def start_file_ingestion(
    service: IngestionService,
    command: StartFileIngestionCommand,
) -> UploadResult:
    return await service.handle_file_upload(
        project_id=command.project_id,
        user_id=command.user_id,
        upload=command.upload,
        rules=command.rules,
    )


async def start_mysql_ingestion(
    service: IngestionService,
    command: StartMySQLIngestionCommand,
) -> UploadResult:
    return await service.start_mysql_ingestion(
        project_id=command.project_id,
        user_id=command.user_id,
        source_id=command.source_id,
        table=command.table,
        rules=command.rules,
    )
