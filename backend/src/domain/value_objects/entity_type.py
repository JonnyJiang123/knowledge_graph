from __future__ import annotations

from enum import Enum


class EntityType(str, Enum):
    ENTERPRISE = "ENTERPRISE"
    PERSON = "PERSON"
    ACCOUNT = "ACCOUNT"
    TRANSACTION = "TRANSACTION"
    SUPPLIER = "SUPPLIER"
    DRUG = "DRUG"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False
