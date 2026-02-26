from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from src.domain.value_objects.risk_level import RiskLevel
from src.domain.value_objects.rule_type import RuleType


# ========== Condition & Action Schemas ==========

class ConditionSchema(BaseModel):
    """规则条件Schema"""
    field: str = Field(..., description="字段路径，如 'entity.type', 'relation.type'")
    operator: str = Field(..., description="操作符: equals, not_equals, in, gt, gte, lt, lte, contains, regex")
    value: Any = Field(..., description="比较值")


class ActionSchema(BaseModel):
    """规则动作Schema"""
    action_type: str = Field(..., description="动作类型: alert, mark, create_relation, set_property")
    target: str = Field(..., description="目标: entity, relation, or specific id")
    params: dict[str, Any] = Field(default_factory=dict, description="动作参数")


# ========== Rule Schemas ==========

class RuleCreate(BaseModel):
    """创建规则请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    rule_type: RuleType
    conditions: List[ConditionSchema] = Field(default_factory=list)
    actions: List[ActionSchema] = Field(default_factory=list)
    priority: int = Field(default=0, ge=0, le=1000)
    is_active: bool = True


class RuleUpdate(BaseModel):
    """更新规则请求"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    conditions: Optional[List[ConditionSchema]] = None
    actions: Optional[List[ActionSchema]] = None
    priority: Optional[int] = Field(default=None, ge=0, le=1000)
    is_active: Optional[bool] = None


class RuleResponse(BaseModel):
    """规则响应"""
    id: str
    project_id: str
    name: str
    description: str
    rule_type: RuleType
    conditions: List[ConditionSchema]
    actions: List[ActionSchema]
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RuleListResponse(BaseModel):
    """规则列表响应"""
    items: List[RuleResponse]
    total: int
    limit: int
    offset: int


# ========== Reasoning Run Schemas ==========

class RunReasoningRequest(BaseModel):
    """执行推理请求"""
    rule_ids: Optional[List[str]] = Field(default=None, description="指定规则ID列表，None表示运行所有规则")
    rule_types: Optional[List[RuleType]] = Field(default=None, description="按规则类型筛选")
    target_entity_ids: Optional[List[str]] = Field(default=None, description="目标实体ID列表")
    parameters: dict[str, Any] = Field(default_factory=dict, description="额外参数")
    async_execution: bool = Field(default=True, description="是否异步执行")


class RunFinanceFraudRequest(BaseModel):
    """执行金融欺诈检测请求"""
    detection_types: List[str] = Field(
        default_factory=list,
        description="检测类型: CIRCULAR_GUARANTEE, FICTITIOUS_TRANSACTION, MONEY_CIRCULATION, RELATED_TRANSACTION"
    )
    target_entity_ids: Optional[List[str]] = None
    async_execution: bool = True


class RunRiskPropagationRequest(BaseModel):
    """执行风险传播分析请求"""
    source_entity_id: str
    risk_level: RiskLevel
    max_depth: int = Field(default=5, ge=1, le=10)
    async_execution: bool = True


class RunHealthcareCheckRequest(BaseModel):
    """执行医疗检查请求"""
    check_types: List[str] = Field(
        default_factory=list,
        description="检查类型: DRUG_INTERACTION, SYMPTOM_MATCH, DIAGNOSIS_COMPLIANCE"
    )
    patient_id: Optional[str] = None
    drug_ids: List[str] = Field(default_factory=list)
    symptom_ids: List[str] = Field(default_factory=list)
    async_execution: bool = True


class RunReasoningResponse(BaseModel):
    """执行推理响应"""
    job_id: str
    status: str  # pending, running, completed, failed
    message: str = ""
    estimated_duration: Optional[int] = None  # 预估执行时间(秒)


# ========== Reasoning Result Schemas ==========

class RuleEvaluationResultResponse(BaseModel):
    """规则评估结果响应"""
    rule_id: str
    rule_name: str
    matched: bool
    matched_entities: List[str] = Field(default_factory=list)
    matched_relations: List[str] = Field(default_factory=list)
    risk_level: Optional[RiskLevel] = None
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    triggered_at: datetime


class FraudDetectionResultResponse(RuleEvaluationResultResponse):
    """欺诈检测结果响应"""
    fraud_type: str
    confidence_score: float
    involved_entities: List[str]
    suspicious_amount: float = 0.0


class RiskPropagationResultResponse(BaseModel):
    """风险传播结果响应"""
    source_entity: str
    risk_level: RiskLevel
    affected_entities: List[dict[str, Any]]
    propagation_path: List[List[str]]


class DrugInteractionResultResponse(RuleEvaluationResultResponse):
    """药物相互作用结果响应"""
    drug1: str
    drug2: str
    interaction_type: str
    severity: str
    mechanism: str
    recommendation: str


class SymptomDiseaseMatchResponse(BaseModel):
    """症状-疾病匹配响应"""
    symptoms: List[str]
    matched_diseases: List[dict[str, Any]]
    confidence_score: float


class DiagnosisComplianceResponse(RuleEvaluationResultResponse):
    """诊疗合规性响应"""
    compliance_type: str
    violations: List[dict[str, Any]]
    recommendations: List[str]


class ReasoningResultDetail(BaseModel):
    """推理结果详情"""
    job_id: str
    project_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[RuleEvaluationResultResponse] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


# ========== Reasoning Job Status Schemas ==========

class ReasoningJobStatusResponse(BaseModel):
    """推理任务状态响应"""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    current_step: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
