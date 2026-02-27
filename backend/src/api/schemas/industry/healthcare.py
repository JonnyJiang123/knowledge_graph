"""医疗DTO - 诊断结果、药物相互作用、质控报告"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SymptomInfo(BaseModel):
    """症状信息"""
    id: str
    name: str
    category: str
    description: str = ""


class DiseaseInfo(BaseModel):
    """疾病信息"""
    id: str
    name: str
    icd_code: str
    description: str
    severity: str  # HIGH, MEDIUM, LOW
    departments: list[str]


class DiagnosisResult(BaseModel):
    """诊断结果"""
    disease_id: str
    disease_name: str
    match_score: float = Field(..., ge=0, le=1)
    matched_symptoms: list[str]
    description: str
    severity: str
    recommended_departments: list[str]


class DiagnosisResponse(BaseModel):
    """诊断响应"""
    possible_diseases: list[DiagnosisResult]
    recommended_departments: list[str]
    confidence: float = Field(..., ge=0, le=1)
    suggested_examinations: list[str] = Field(default_factory=list)
    suggested_symptoms: list[str] = Field(default_factory=list)


class DrugInfo(BaseModel):
    """药物信息"""
    id: str
    name: str
    category: str
    description: str = ""
    contraindications: list[str] = Field(default_factory=list)


class DrugInteractionDetail(BaseModel):
    """药物相互作用详情"""
    drug_a_id: str
    drug_a_name: str
    drug_b_id: str
    drug_b_name: str
    interaction_type: str  # CONTRAINDICATION, CAUTION, INFO
    severity: str  # HIGH, MEDIUM, LOW
    mechanism: str = ""  # 作用机制
    description: str
    recommendation: str
    source: str = ""  # 数据来源


class DrugInteractionResponse(BaseModel):
    """药物相互作用检查响应"""
    interactions: list[DrugInteractionDetail]
    has_contraindication: bool
    has_caution: bool
    summary: str
    checked_at: datetime


class QCReport(BaseModel):
    """病历质控报告"""
    record_id: str
    overall_score: float = Field(..., ge=0, le=100)
    issues: list[dict[str, Any]]
    suggestions: list[str]
    checked_rules: list[str]
    passed_rules: list[str]
    failed_rules: list[str]
    checked_at: datetime


class QCIssue(BaseModel):
    """质控问题"""
    type: str  # MISSING_FIELD, LOGIC_ERROR, FORMAT_ERROR, etc.
    field: str
    severity: str  # HIGH, MEDIUM, LOW
    message: str
    suggestion: str = ""
