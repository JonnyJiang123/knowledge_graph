from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.relation_type import RelationType


class GraphEntityCreate(BaseModel):
    external_id: str
    type: EntityType
    labels: List[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEntityResponse(BaseModel):
    id: str
    project_id: str
    external_id: Optional[str] = None
    type: Optional[EntityType] = None
    labels: List[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)
    version: Optional[int] = None


class GraphRelationCreate(BaseModel):
    source_id: str
    target_id: str
    type: RelationType
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphRelationResponse(BaseModel):
    id: str
    project_id: str
    source_id: str
    target_id: str
    type: RelationType | str
    properties: dict[str, Any] = Field(default_factory=dict)


class NeighborResponse(BaseModel):
    entities: list[GraphEntityResponse]
    relations: list[GraphRelationResponse]
