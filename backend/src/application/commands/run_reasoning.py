from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.domain.value_objects.rule_type import RuleType


@dataclass(slots=True)
class RunReasoningCommand:
    """执行推理命令"""
    project_id: str
    owner_id: str
    rule_ids: list[str] | None = None  # 指定规则ID列表，None表示运行所有规则
    rule_types: list[RuleType] | None = None  # 按规则类型筛选
    target_entity_ids: list[str] | None = None  # 目标实体ID列表
    parameters: dict[str, Any] = field(default_factory=dict)  # 额外参数
    async_execution: bool = True  # 是否异步执行


@dataclass(slots=True)
class RunFinanceFraudDetectionCommand:
    """执行金融欺诈检测命令"""
    project_id: str
    owner_id: str
    detection_types: list[str] = field(default_factory=list)
    # 可选: CIRCULAR_GUARANTEE, FICTITIOUS_TRANSACTION, MONEY_CIRCULATION, RELATED_TRANSACTION
    target_entity_ids: list[str] | None = None
    async_execution: bool = True


@dataclass(slots=True)
class RunRiskPropagationCommand:
    """执行风险传播分析命令"""
    project_id: str
    owner_id: str
    source_entity_id: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    max_depth: int = 5
    async_execution: bool = True


@dataclass(slots=True)
class RunHealthcareCheckCommand:
    """执行医疗检查命令"""
    project_id: str
    owner_id: str
    check_types: list[str] = field(default_factory=list)
    # 可选: DRUG_INTERACTION, SYMPTOM_MATCH, DIAGNOSIS_COMPLIANCE
    patient_id: str | None = None
    drug_ids: list[str] = field(default_factory=list)
    symptom_ids: list[str] = field(default_factory=list)
    async_execution: bool = True
