"""金融DTO - 风险报告、欺诈告警、关联图谱"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    """风险因子"""
    value: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    description: str


class AssociatedRisk(BaseModel):
    """关联风险"""
    enterprise_id: str
    enterprise_name: str
    risk_level: str  # LOW, MEDIUM, HIGH
    impact: float = Field(..., ge=0, le=1)


class RiskReport(BaseModel):
    """企业信用风险报告"""
    enterprise_id: str
    enterprise_name: str
    overall_score: float = Field(..., ge=0, le=100)
    risk_level: str  # LOW, MEDIUM, HIGH
    factors: dict[str, RiskFactor]
    associated_risks: list[AssociatedRisk]
    updated_at: datetime


class FraudAlert(BaseModel):
    """欺诈检测告警"""
    alert_id: str
    alert_type: str
    severity: str  # LOW, MEDIUM, HIGH
    description: str
    affected_accounts: list[str]
    confidence: float = Field(..., ge=0, le=1)
    detected_at: datetime
    status: str = "active"  # active, resolved, ignored


class FraudDetectionResult(BaseModel):
    """欺诈检测结果"""
    detection_id: str
    status: str
    alerts: list[FraudAlert]
    risk_score: float = Field(..., ge=0, le=1)
    summary: str
    created_at: datetime


class AssociationNode(BaseModel):
    """关联图谱节点"""
    id: str
    name: str
    type: str
    risk_level: str = "UNKNOWN"
    properties: dict[str, Any] = Field(default_factory=dict)


class AssociationEdge(BaseModel):
    """关联图谱边"""
    source: str
    target: str
    relation_type: str
    confidence: float = 1.0
    properties: dict[str, Any] = Field(default_factory=dict)


class AssociationGraph(BaseModel):
    """企业关联图谱"""
    enterprise_id: str
    enterprise_name: str
    depth: int
    nodes: list[AssociationNode]
    edges: list[AssociationEdge]
    total_nodes: int
    total_edges: int
    clusters: list[dict[str, Any]] = Field(default_factory=list)


class InvestmentInfo(BaseModel):
    """投资信息"""
    target_enterprise_id: str
    target_name: str
    investment_ratio: float
    investment_amount: float | None = None
    investment_date: datetime | None = None


class ShareholderInfo(BaseModel):
    """股东信息"""
    shareholder_id: str
    shareholder_name: str
    shareholding_ratio: float
    shareholder_type: str  # PERSON, ENTERPRISE
