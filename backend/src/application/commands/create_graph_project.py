from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.value_objects.industry import Industry


@dataclass(slots=True)
class CreateGraphProjectCommand:
    name: str
    owner_id: str
    industry: Industry
    description: str | None = None
    metadata: dict[str, Any] | None = None
