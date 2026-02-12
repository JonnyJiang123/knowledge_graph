import re
from typing import Any, Iterable

from src.domain.value_objects.ingestion import CleaningRule, CleaningRuleType


class CleaningRuleEngine:
    """Simple rule evaluation engine for ingestion previews."""

    def apply(
        self,
        record: dict[str, Any],
        rules: Iterable[CleaningRule],
    ) -> dict[str, Any]:
        errors: list[str] = []
        cleaned = dict(record)

        for rule in rules:
            value = cleaned.get(rule.field)
            if rule.rule_type == CleaningRuleType.NOT_NULL:
                if value in (None, "", []):
                    errors.append(rule.message or f"{rule.field} cannot be empty")
            elif rule.rule_type == CleaningRuleType.RANGE:
                min_value = rule.params.get("min")
                max_value = rule.params.get("max")
                try:
                    numeric_value = float(value)
                except (TypeError, ValueError):
                    errors.append(rule.message or f"{rule.field} is not numeric")
                    continue

                if min_value is not None and numeric_value < min_value:
                    errors.append(rule.message or f"{rule.field} must be >= {min_value}")
                if max_value is not None and numeric_value > max_value:
                    errors.append(rule.message or f"{rule.field} must be <= {max_value}")
            elif rule.rule_type == CleaningRuleType.REGEX:
                pattern = rule.params.get("pattern")
                if pattern and (value is None or re.fullmatch(pattern, str(value)) is None):
                    errors.append(rule.message or f"{rule.field} does not match pattern")
            elif rule.rule_type == CleaningRuleType.DEDUPE:
                # Dedupe is handled at persistence layer; no-op here.
                continue

        return {
            "record": cleaned,
            "is_valid": not errors,
            "errors": errors,
        }
