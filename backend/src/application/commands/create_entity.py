from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.value_objects.entity_type import EntityType


@dataclass(slots=True)
class CreateEntityCommand:
    project_id: str
    owner_id: str
    external_id: str
    type: EntityType
    labels: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
