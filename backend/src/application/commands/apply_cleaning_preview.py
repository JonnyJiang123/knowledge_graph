from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from src.application.services.ingestion_service import IngestionService
from src.domain.value_objects.ingestion import CleaningRule


@dataclass
class ApplyCleaningPreviewCommand:
    artifact_id: str
    rules: Sequence[CleaningRule]


async def apply_cleaning_preview(
    service: IngestionService,
    command: ApplyCleaningPreviewCommand,
):
    return await service.apply_rules_to_preview(command.artifact_id, command.rules)
