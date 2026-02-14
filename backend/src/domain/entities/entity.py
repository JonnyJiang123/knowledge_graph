from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.domain.value_objects.entity_type import EntityType


@dataclass
class Entity:
    project_id: str
    external_id: str
    type: EntityType
    id: str = field(default_factory=lambda: str(uuid4()))
    labels: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if isinstance(self.type, str):
            self.type = EntityType(self.type)

    @classmethod
    def create(
        cls,
        *,
        project_id: str,
        external_id: str,
        type: EntityType | str,
        labels: list[str] | None = None,
        properties: dict[str, Any] | None = None,
    ) -> "Entity":
        return cls(
            project_id=project_id,
            external_id=external_id,
            type=type if isinstance(type, EntityType) else EntityType(type),
            labels=list(labels or []),
            properties=dict(properties or {}),
        )

    def update_properties(self, **changes: Any) -> None:
        self.properties.update(changes)
        self.version += 1
        self.updated_at = datetime.now(UTC)
