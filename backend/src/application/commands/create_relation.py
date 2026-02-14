from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.value_objects.relation_type import RelationType


@dataclass(slots=True)
class CreateRelationCommand:
    project_id: str
    owner_id: str
    source_id: str
    target_id: str
    type: RelationType
    properties: dict[str, Any] = field(default_factory=dict)
