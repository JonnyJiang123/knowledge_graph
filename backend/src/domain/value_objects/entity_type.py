from __future__ import annotations

from enum import Enum


class EntityType(str, Enum):
    # Organization & Business
    ENTERPRISE = "ENTERPRISE"
    ORGANIZATION = "ORGANIZATION"
    COMPANY = "COMPANY"
    
    # Person
    PERSON = "PERSON"
    
    # Financial
    ACCOUNT = "ACCOUNT"
    TRANSACTION = "TRANSACTION"
    SUPPLIER = "SUPPLIER"
    
    # Healthcare
    DRUG = "DRUG"
    DISEASE = "DISEASE"
    SYMPTOM = "SYMPTOM"
    
    # Generic
    LOCATION = "LOCATION"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    
    # Default for auto-extraction
    UNKNOWN = "UNKNOWN"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False
