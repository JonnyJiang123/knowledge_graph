from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.domain.entities.entity import Entity
from src.domain.entities.relation import Relation
from src.domain.value_objects.industry import Industry


@dataclass
class GraphProject:
    name: str
    owner_id: str
    industry: Industry
    id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "ACTIVE"
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    entities: dict[str, Entity] = field(default_factory=dict)
    relations: dict[str, Relation] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if isinstance(self.industry, str):
            self.industry = Industry(self.industry)

    @classmethod
    def new(
        cls,
        *,
        name: str,
        owner_id: str,
        industry: Industry | str,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "GraphProject":
        return cls(
            name=name,
            owner_id=owner_id,
            industry=industry if isinstance(industry, Industry) else Industry(industry),
            description=description,
            metadata=dict(metadata or {}),
        )

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)

    def add_entity(self, entity: Entity) -> None:
        if entity.project_id != self.id:
            raise ValueError("Entity project mismatch")
        self.entities[entity.id] = entity
        self.touch()

    def add_relation(self, relation: Relation) -> None:
        if relation.project_id != self.id:
            raise ValueError("Relation project mismatch")
        if relation.source_id not in self.entities or relation.target_id not in self.entities:
            raise ValueError("Relation requires both entities in project")
        self.relations[relation.id] = relation
        self.touch()

    def remove_entity(self, entity_id: str) -> None:
        if entity_id in self.entities:
            del self.entities[entity_id]
            # remove relations touching entity
            self.relations = {
                rel_id: rel
                for rel_id, rel in self.relations.items()
                if rel.source_id != entity_id and rel.target_id != entity_id
            }
            self.touch()
