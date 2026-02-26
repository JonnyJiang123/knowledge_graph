from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.domain.entities.entity import Entity
from src.domain.entities.rule import Action, Condition, ReasoningRule
from src.domain.services.reasoning.rule_engine import (
    RuleContext,
    RuleEngine,
    RuleEvaluationResult,
)
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.relation_type import RelationType
from src.domain.value_objects.risk_level import RiskLevel
from src.domain.value_objects.rule_type import RuleType


@dataclass
class DrugInteractionResult(RuleEvaluationResult):
    """药物相互作用结果"""
    drug1: str = ""
    drug2: str = ""
    interaction_type: str = ""  # 相互作用类型: contraindication, warning, caution
    severity: str = ""  # 严重程度: high, moderate, low
    mechanism: str = ""  # 作用机制
    recommendation: str = ""  # 建议


@dataclass
class SymptomDiseaseMatchResult(RuleEvaluationResult):
    """症状-疾病匹配结果"""
    symptoms: list[str] = field(default_factory=list)
    matched_diseases: list[dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0


@dataclass
class DiagnosisComplianceResult(RuleEvaluationResult):
    """诊疗合规性结果"""
    compliance_type: str = ""  # 合规类型
    violations: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class HealthcareRuleEngine(RuleEngine):
    """医疗规则引擎 - 用于药物相互作用检测、症状-疾病匹配和诊疗合规性检查"""

    # 药物相互作用严重程度
    SEVERITY_HIGH = "high"
    SEVERITY_MODERATE = "moderate"
    SEVERITY_LOW = "low"

    # 相互作用类型
    INTERACTION_CONTRAINDICATION = "contraindication"  # 禁忌
    INTERACTION_WARNING = "warning"  # 警告
    INTERACTION_CAUTION = "caution"  # 注意

    def __init__(self, graph_repo: Any | None = None) -> None:
        super().__init__(graph_repo)
        # 药物相互作用知识库
        self._drug_interactions: dict[tuple[str, str], dict[str, Any]] = {}
        # 症状-疾病知识库
        self._symptom_disease_map: dict[str, list[dict[str, Any]]] = {}

    async def check_drug_interactions(
        self,
        project_id: str,
        drug_ids: list[str],
    ) -> list[DrugInteractionResult]:
        """检查药物相互作用
        
        检查给定的药物列表中是否存在相互作用
        """
        results: list[DrugInteractionResult] = []
        context = await self._load_drug_context(project_id, drug_ids)

        # 获取所有药物实体
        drugs = [
            context.entities[did] for did in drug_ids
            if did in context.entities
        ]

        # 两两检查相互作用
        for i, drug1 in enumerate(drugs):
            for drug2 in drugs[i + 1:]:
                interaction = self._check_two_drugs_interaction(drug1, drug2)
                if interaction:
                    result = DrugInteractionResult(
                        rule_id="drug_interaction_check",
                        rule_name="药物相互作用检查",
                        matched=True,
                        matched_entities=[drug1.id, drug2.id],
                        risk_level=self._severity_to_risk_level(interaction["severity"]),
                        drug1=drug1.properties.get("name", drug1.id),
                        drug2=drug2.properties.get("name", drug2.id),
                        interaction_type=interaction["type"],
                        severity=interaction["severity"],
                        mechanism=interaction.get("mechanism", ""),
                        recommendation=interaction.get("recommendation", ""),
                        message=f"检测到药物相互作用: {drug1.properties.get('name', '')} + {drug2.properties.get('name', '')}",
                        details=interaction,
                    )
                    results.append(result)

        return results

    async def match_symptoms_to_diseases(
        self,
        project_id: str,
        symptom_ids: list[str],
        min_match_ratio: float = 0.5,
    ) -> SymptomDiseaseMatchResult:
        """症状-疾病匹配
        
        根据症状列表匹配可能的疾病
        """
        context = await self._load_symptom_context(project_id, symptom_ids)

        # 获取症状名称
        symptom_names = [
            context.entities[sid].properties.get("name", sid)
            for sid in symptom_ids if sid in context.entities
        ]

        # 匹配疾病
        disease_matches: dict[str, dict[str, Any]] = {}

        for symptom_name in symptom_names:
            if symptom_name in self._symptom_disease_map:
                for disease_info in self._symptom_disease_map[symptom_name]:
                    disease_id = disease_info["disease_id"]
                    if disease_id not in disease_matches:
                        disease_matches[disease_id] = {
                            "disease_id": disease_id,
                            "disease_name": disease_info["disease_name"],
                            "matched_symptoms": [],
                            "total_symptoms": disease_info.get("total_symptoms", 0),
                            "weight_sum": 0,
                        }
                    disease_matches[disease_id]["matched_symptoms"].append(symptom_name)
                    disease_matches[disease_id]["weight_sum"] += disease_info.get("weight", 1)

        # 计算匹配度并筛选
        matched_diseases = []
        for disease in disease_matches.values():
            match_ratio = len(disease["matched_symptoms"]) / disease["total_symptoms"]
            if match_ratio >= min_match_ratio:
                confidence = min(1.0, disease["weight_sum"] / disease["total_symptoms"])
                matched_diseases.append({
                    "disease_id": disease["disease_id"],
                    "disease_name": disease["disease_name"],
                    "matched_symptoms": disease["matched_symptoms"],
                    "match_ratio": match_ratio,
                    "confidence": confidence,
                })

        # 按置信度排序
        matched_diseases.sort(key=lambda x: x["confidence"], reverse=True)

        # 计算总体置信度
        avg_confidence = (
            sum(d["confidence"] for d in matched_diseases) / len(matched_diseases)
            if matched_diseases else 0
        )

        return SymptomDiseaseMatchResult(
            rule_id="symptom_disease_match",
            rule_name="症状-疾病匹配",
            matched=len(matched_diseases) > 0,
            matched_entities=list(context.entities.keys()),
            symptoms=symptom_names,
            matched_diseases=matched_diseases,
            confidence_score=avg_confidence,
            message=f"匹配到 {len(matched_diseases)} 种可能的疾病",
            details={"top_diseases": matched_diseases[:5]},
        )

    async def check_diagnosis_compliance(
        self,
        project_id: str,
        patient_id: str,
        diagnosis_id: str,
    ) -> DiagnosisComplianceResult:
        """诊疗合规性检查
        
        检查诊疗过程是否符合规范：
        1. 必要检查是否完成
        2. 用药是否合理
        3. 诊断逻辑是否完整
        """
        context = await self._load_patient_context(project_id, patient_id)

        violations: list[dict[str, Any]] = []
        recommendations: list[str] = []

        # 获取患者相关的诊断和药物
        patient = context.entities.get(patient_id)
        if not patient:
            return DiagnosisComplianceResult(
                rule_id="diagnosis_compliance",
                rule_name="诊疗合规性检查",
                matched=False,
                message="未找到患者信息",
            )

        # 检查1: 诊断是否有症状支持
        symptoms = [
            e for e in context.entities.values()
            if e.type == EntityType.SYMPTOM
        ]
        if not symptoms:
            violations.append({
                "type": "missing_symptoms",
                "message": "诊断缺少症状支持",
                "severity": "high",
            })
            recommendations.append("请补充患者症状信息")

        # 检查2: 药物相互作用
        drugs = [
            e for e in context.entities.values()
            if e.type == EntityType.DRUG
        ]
        if len(drugs) >= 2:
            drug_ids = [d.id for d in drugs]
            interactions = await self.check_drug_interactions(project_id, drug_ids)
            if interactions:
                for interaction in interactions:
                    violations.append({
                        "type": "drug_interaction",
                        "message": interaction.message,
                        "severity": interaction.severity,
                        "drugs": [interaction.drug1, interaction.drug2],
                    })
                    recommendations.append(f"注意：{interaction.recommendation}")

        # 检查3: 疾病与药物匹配
        diseases = [
            e for e in context.entities.values()
            if e.type == EntityType.DISEASE
        ]
        for drug in drugs:
            contraindications = drug.properties.get("contraindications", [])
            for disease in diseases:
                disease_name = disease.properties.get("name", "")
                if disease_name in contraindications:
                    violations.append({
                        "type": "drug_contraindication",
                        "message": f"{drug.properties.get('name', '')} 禁用于 {disease_name}",
                        "severity": "critical",
                    })
                    recommendations.append(f"请更换治疗 {disease_name} 的药物")

        risk_level = RiskLevel.LOW
        if any(v["severity"] == "critical" for v in violations):
            risk_level = RiskLevel.CRITICAL
        elif any(v["severity"] == "high" for v in violations):
            risk_level = RiskLevel.HIGH
        elif violations:
            risk_level = RiskLevel.MEDIUM

        return DiagnosisComplianceResult(
            rule_id="diagnosis_compliance",
            rule_name="诊疗合规性检查",
            matched=len(violations) > 0,
            matched_entities=[patient_id, diagnosis_id],
            risk_level=risk_level,
            compliance_type="diagnosis",
            violations=violations,
            recommendations=recommendations,
            message=f"发现 {len(violations)} 处合规问题" if violations else "诊疗过程符合规范",
            details={"violation_count": len(violations)},
        )

    async def run_healthcare_rules(
        self,
        project_id: str,
        context: RuleContext,
    ) -> list[RuleEvaluationResult]:
        """运行医疗领域特定规则"""
        results: list[RuleEvaluationResult] = []

        # 规则1: 检测处方药与疾病匹配
        rule_drug_disease = ReasoningRule.create(
            project_id=project_id,
            name="药物-疾病适应症检查",
            description="检查处方药物是否适用于当前诊断的疾病",
            rule_type=RuleType.HEALTHCARE_DRUG,
            conditions=[
                Condition(
                    field="entity.type",
                    operator="equals",
                    value=EntityType.DRUG.value,
                ),
                Condition(
                    field="entity.properties.requires_prescription",
                    operator="equals",
                    value=True,
                ),
            ],
            actions=[
                Action(
                    action_type="validate_indication",
                    target="entity",
                    params={},
                ),
            ],
            priority=90,
        )

        # 规则2: 检测重复用药
        rule_duplicate_drug = ReasoningRule.create(
            project_id=project_id,
            name="重复用药检测",
            description="检测是否存在相同成分的药物重复开具",
            rule_type=RuleType.HEALTHCARE_DRUG,
            conditions=[
                Condition(
                    field="entity.type",
                    operator="equals",
                    value=EntityType.DRUG.value,
                ),
            ],
            actions=[
                Action(
                    action_type="alert",
                    target="entity",
                    params={"type": "duplicate_drug"},
                ),
            ],
            priority=85,
        )

        # 评估规则
        for rule in [rule_drug_disease, rule_duplicate_drug]:
            result = await self.evaluate_rule(rule, context)
            if result.matched:
                results.append(result)

        return results

    def add_drug_interaction(
        self,
        drug1: str,
        drug2: str,
        interaction_type: str,
        severity: str,
        mechanism: str = "",
        recommendation: str = "",
    ) -> None:
        """添加药物相互作用到知识库"""
        key = tuple(sorted([drug1, drug2]))
        self._drug_interactions[key] = {
            "drug1": drug1,
            "drug2": drug2,
            "type": interaction_type,
            "severity": severity,
            "mechanism": mechanism,
            "recommendation": recommendation,
        }

    def add_symptom_disease_mapping(
        self,
        symptom: str,
        disease_id: str,
        disease_name: str,
        weight: int = 1,
        total_symptoms: int = 1,
    ) -> None:
        """添加症状-疾病映射到知识库"""
        if symptom not in self._symptom_disease_map:
            self._symptom_disease_map[symptom] = []

        self._symptom_disease_map[symptom].append({
            "disease_id": disease_id,
            "disease_name": disease_name,
            "weight": weight,
            "total_symptoms": total_symptoms,
        })

    def _check_two_drugs_interaction(
        self,
        drug1: Entity,
        drug2: Entity,
    ) -> dict[str, Any] | None:
        """检查两个药物之间的相互作用"""
        name1 = drug1.properties.get("name", drug1.id)
        name2 = drug2.properties.get("name", drug2.id)

        key = tuple(sorted([name1, name2]))
        return self._drug_interactions.get(key)

    def _severity_to_risk_level(self, severity: str) -> RiskLevel:
        """将严重程度转换为风险等级"""
        mapping = {
            self.SEVERITY_HIGH: RiskLevel.HIGH,
            self.SEVERITY_MODERATE: RiskLevel.MEDIUM,
            self.SEVERITY_LOW: RiskLevel.LOW,
        }
        return mapping.get(severity, RiskLevel.LOW)

    async def _load_drug_context(
        self,
        project_id: str,
        drug_ids: list[str],
    ) -> RuleContext:
        """加载药物上下文"""
        # 简化实现，实际应从数据库加载
        return RuleContext(project_id=project_id)

    async def _load_symptom_context(
        self,
        project_id: str,
        symptom_ids: list[str],
    ) -> RuleContext:
        """加载症状上下文"""
        # 简化实现，实际应从数据库加载
        return RuleContext(project_id=project_id)

    async def _load_patient_context(
        self,
        project_id: str,
        patient_id: str,
    ) -> RuleContext:
        """加载患者上下文"""
        # 简化实现，实际应从数据库加载
        return RuleContext(project_id=project_id)
