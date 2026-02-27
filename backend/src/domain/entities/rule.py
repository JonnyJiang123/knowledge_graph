from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.domain.value_objects.rule_type import RuleType


@dataclass
class Condition:
    """规则条件"""
    field: str  # 字段路径，如 "entity.type", "relation.type", "property.amount"
    operator: str  # 操作符: equals, not_equals, in, not_in, gt, gte, lt, lte, contains, regex
    value: Any  # 比较值


@dataclass
class Action:
    """规则动作"""
    action_type: str  # 动作类型: alert, mark, create_relation, set_property
    target: str  # 目标: entity, relation, or specific id
    params: dict[str, Any] = field(default_factory=dict)  # 动作参数


@dataclass
class ReasoningRule:
    """推理规则实体"""
    project_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: list[Condition]
    actions: list[Action]
    priority: int = 0  # 优先级，数值越大优先级越高
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if isinstance(self.rule_type, str):
            self.rule_type = RuleType(self.rule_type)

    @classmethod
    def create(
        cls,
        *,
        project_id: str,
        name: str,
        description: str,
        rule_type: RuleType | str,
        conditions: list[Condition] | None = None,
        actions: list[Action] | None = None,
        priority: int = 0,
        is_active: bool = True,
    ) -> "ReasoningRule":
        """创建新规则"""
        return cls(
            project_id=project_id,
            name=name,
            description=description,
            rule_type=rule_type if isinstance(rule_type, RuleType) else RuleType(rule_type),
            conditions=list(conditions or []),
            actions=list(actions or []),
            priority=priority,
            is_active=is_active,
        )

    def update(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        conditions: list[Condition] | None = None,
        actions: list[Action] | None = None,
        priority: int | None = None,
        is_active: bool | None = None,
    ) -> None:
        """更新规则"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if conditions is not None:
            self.conditions = conditions
        if actions is not None:
            self.actions = actions
        if priority is not None:
            self.priority = priority
        if is_active is not None:
            self.is_active = is_active
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """停用规则"""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """激活规则"""
        self.is_active = True
        self.updated_at = datetime.now(UTC)
