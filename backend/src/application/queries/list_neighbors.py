from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ListNeighborsQuery:
    project_id: str
    owner_id: str
    entity_id: str
    depth: int = 1
    limit: int | None = None
