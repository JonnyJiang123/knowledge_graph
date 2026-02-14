from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.domain.value_objects.relation_type import RelationType


@dataclass
class Relation:
    project_id: str
    source_id: str
    target_id: str
    type: RelationType
    id: str = field(default_factory=lambda: str(uuid4()))
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            self.type = RelationType(self.type)
        if self.source_id == self.target_id:
            raise ValueError("Self-loop relations are not allowed")

    @classmethod
    def create(
        cls,
        *,
        project_id: str,
        source_id: str,
        target_id: str,
        type: RelationType | str,
        properties: dict[str, Any] | None = None,
    ) -> "Relation":
        return cls(
            project_id=project_id,
            source_id=source_id,
            target_id=target_id,
            type=type if isinstance(type, RelationType) else RelationType(type),
            properties=dict(properties or {}),
        )
