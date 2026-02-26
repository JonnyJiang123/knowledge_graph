from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.entities.rule import Action, Condition
from src.domain.value_objects.rule_type import RuleType


@dataclass(slots=True)
class CreateRuleCommand:
    """创建规则命令"""
    project_id: str
    owner_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: list[Condition] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    priority: int = 0
    is_active: bool = True


@dataclass(slots=True)
class UpdateRuleCommand:
    """更新规则命令"""
    rule_id: str
    owner_id: str
    name: str | None = None
    description: str | None = None
    conditions: list[Condition] | None = None
    actions: list[Action] | None = None
    priority: int | None = None
    is_active: bool | None = None


@dataclass(slots=True)
class DeleteRuleCommand:
    """删除规则命令"""
    rule_id: str
    owner_id: str


@dataclass(slots=True)
class ActivateRuleCommand:
    """激活规则命令"""
    rule_id: str
    owner_id: str


@dataclass(slots=True)
class DeactivateRuleCommand:
    """停用规则命令"""
    rule_id: str
    owner_id: str
