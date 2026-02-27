from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.value_objects.rule_type import RuleType


@dataclass(slots=True)
class GetReasoningResultQuery:
    """获取推理结果查询"""
    job_id: str
    owner_id: str


@dataclass(slots=True)
class ListReasoningResultsQuery:
    """列示推理结果查询"""
    project_id: str
    owner_id: str
    rule_id: str | None = None
    rule_type: RuleType | None = None
    matched_only: bool = True
    limit: int = 50
    offset: int = 0


@dataclass(slots=True)
class GetReasoningJobStatusQuery:
    """获取推理任务状态查询"""
    job_id: str
    owner_id: str


@dataclass(slots=True)
class ListReasoningRulesQuery:
    """列示推理规则查询"""
    project_id: str
    owner_id: str
    rule_type: RuleType | None = None
    is_active: bool | None = None
    limit: int = 50
    offset: int = 0


@dataclass(slots=True)
class GetReasoningRuleDetailQuery:
    """获取规则详情查询"""
    rule_id: str
    owner_id: str
