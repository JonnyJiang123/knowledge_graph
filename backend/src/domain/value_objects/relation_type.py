from __future__ import annotations

from enum import Enum


class RelationType(str, Enum):
    OWNS = "OWNS"
    CONTROLS = "CONTROLS"
    TRANSFERRED_TO = "TRANSFERRED_TO"
    GUARANTEES = "GUARANTEES"
    SUPPLIES = "SUPPLIES"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False
