from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from celery.utils.log import get_task_logger

from src.config import settings
from src.domain.services.reasoning.finance_rules import FinanceRuleEngine
from src.domain.services.reasoning.healthcare_rules import HealthcareRuleEngine
from src.domain.services.reasoning.rule_engine import RuleContext, RuleEngine
from src.domain.value_objects.risk_level import RiskLevel
from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository
from src.infrastructure.queue.celery_app import celery_app

logger = get_task_logger(__name__)


class ReasoningJobStatus:
    """推理任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@celery_app.task(name="reasoning.run_reasoning_job", bind=True)
def run_reasoning_job(self, **payload: Any) -> None:
    """执行推理任务的入口点"""
    asyncio.run(_execute_reasoning_job(self, payload))


async def _execute_reasoning_job(task: Any, payload: dict[str, Any]) -> None:
    """执行推理任务"""
    job_id: str = payload["job_id"]
    project_id: str = payload["project_id"]
    job_type: str = payload.get("job_type", "general")

    logger.info("Starting reasoning job %s of type %s", job_id, job_type)

    # 更新任务状态
    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 0, "current_step": "Initializing"},
    )

    try:
        # 根据任务类型执行不同的推理
        if job_type == "fraud_detection":
            results = await _run_fraud_detection(payload, task)
        elif job_type == "risk_propagation":
            results = await _run_risk_propagation(payload, task)
        elif job_type == "healthcare_check":
            results = await _run_healthcare_check(payload, task)
        else:
            results = await _run_general_reasoning(payload, task)

        # 保存结果
        await _save_results(job_id, project_id, results)

        task.update_state(
            state=ReasoningJobStatus.COMPLETED,
            meta={"progress": 100, "results_count": len(results)},
        )

        logger.info("Reasoning job %s completed with %d results", job_id, len(results))

    except Exception as exc:
        logger.exception("Reasoning job %s failed", job_id)
        task.update_state(
            state=ReasoningJobStatus.FAILED,
            meta={"error": str(exc)},
        )
        raise


async def _run_general_reasoning(
    payload: dict[str, Any],
    task: Any,
) -> list[dict[str, Any]]:
    """执行通用推理"""
    project_id: str = payload["project_id"]
    rule_ids: list[str] | None = payload.get("rule_ids")
    rule_types: list[str] | None = payload.get("rule_types")
    target_entity_ids: list[str] | None = payload.get("target_entity_ids")

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 10, "current_step": "Loading rules"},
    )

    # 初始化图仓库和规则引擎
    graph_repo = Neo4jGraphRepository()
    engine = RuleEngine(graph_repo)

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 30, "current_step": "Building context"},
    )

    # 构建上下文
    context = await _build_context(graph_repo, project_id, target_entity_ids)

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 50, "current_step": "Evaluating rules"},
    )

    # TODO: 从数据库加载规则并评估
    # rules = await _load_rules(project_id, rule_ids, rule_types)
    # results = await engine.evaluate_all_rules(rules, context)

    # 模拟结果
    results = []

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 90, "current_step": "Processing results"},
    )

    return [
        {
            "rule_id": r.rule_id,
            "rule_name": r.rule_name,
            "matched": r.matched,
            "matched_entities": r.matched_entities,
            "matched_relations": r.matched_relations,
            "risk_level": r.risk_level.value if r.risk_level else None,
            "message": r.message,
            "details": r.details,
            "triggered_at": r.triggered_at.isoformat(),
        }
        for r in results
    ]


async def _run_fraud_detection(
    payload: dict[str, Any],
    task: Any,
) -> list[dict[str, Any]]:
    """执行欺诈检测"""
    project_id: str = payload["project_id"]
    detection_types: list[str] = payload.get("detection_types", [])
    target_entity_ids: list[str] | None = payload.get("target_entity_ids")

    graph_repo = Neo4jGraphRepository()
    engine = FinanceRuleEngine(graph_repo)

    results = []

    if not target_entity_ids:
        # 如果没有指定目标实体，则检测所有企业实体
        # TODO: 从数据库加载所有企业实体
        target_entity_ids = []

    for idx, entity_id in enumerate(target_entity_ids):
        progress = int((idx / len(target_entity_ids)) * 80) + 10
        task.update_state(
            state=ReasoningJobStatus.RUNNING,
            meta={
                "progress": progress,
                "current_step": f"Checking entity {entity_id}",
            },
        )

        # 循环担保检测
        if not detection_types or "CIRCULAR_GUARANTEE" in detection_types:
            result = await engine.detect_circular_guarantee(project_id, entity_id)
            if result:
                results.append({
                    "type": "circular_guarantee",
                    "fraud_type": result.fraud_type,
                    "confidence_score": result.confidence_score,
                    "involved_entities": result.involved_entities,
                    "message": result.message,
                    "details": result.details,
                })

        # 资金回流检测
        if not detection_types or "MONEY_CIRCULATION" in detection_types:
            result = await engine.detect_money_circulation(project_id, entity_id)
            if result:
                results.append({
                    "type": "money_circulation",
                    "fraud_type": result.fraud_type,
                    "confidence_score": result.confidence_score,
                    "involved_entities": result.involved_entities,
                    "message": result.message,
                    "details": result.details,
                })

        # 关联交易检测
        if not detection_types or "RELATED_TRANSACTION" in detection_types:
            result = await engine.detect_related_party_transaction(project_id, entity_id)
            if result:
                results.append({
                    "type": "related_transaction",
                    "fraud_type": result.fraud_type,
                    "confidence_score": result.confidence_score,
                    "involved_entities": result.involved_entities,
                    "message": result.message,
                    "details": result.details,
                })

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 90, "current_step": "Aggregating results"},
    )

    return results


async def _run_risk_propagation(
    payload: dict[str, Any],
    task: Any,
) -> dict[str, Any]:
    """执行风险传播分析"""
    project_id: str = payload["project_id"]
    source_entity_id: str = payload["source_entity_id"]
    risk_level_str: str = payload["risk_level"]
    max_depth: int = payload.get("max_depth", 5)

    risk_level = RiskLevel(risk_level_str)

    graph_repo = Neo4jGraphRepository()
    engine = FinanceRuleEngine(graph_repo)

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 20, "current_step": "Analyzing risk propagation"},
    )

    result = await engine.analyze_risk_propagation(
        project_id, source_entity_id, risk_level
    )

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 80, "current_step": "Processing propagation results"},
    )

    return {
        "source_entity": result.source_entity,
        "risk_level": result.risk_level.value,
        "affected_count": len(result.affected_entities),
        "affected_entities": result.affected_entities,
        "propagation_paths": result.propagation_path,
    }


async def _run_healthcare_check(
    payload: dict[str, Any],
    task: Any,
) -> list[dict[str, Any]]:
    """执行医疗检查"""
    project_id: str = payload["project_id"]
    check_types: list[str] = payload.get("check_types", [])
    patient_id: str | None = payload.get("patient_id")
    drug_ids: list[str] = payload.get("drug_ids", [])
    symptom_ids: list[str] = payload.get("symptom_ids", [])

    graph_repo = Neo4jGraphRepository()
    engine = HealthcareRuleEngine(graph_repo)

    results = []

    # 药物相互作用检查
    if (not check_types or "DRUG_INTERACTION" in check_types) and len(drug_ids) >= 2:
        task.update_state(
            state=ReasoningJobStatus.RUNNING,
            meta={"progress": 30, "current_step": "Checking drug interactions"},
        )

        interactions = await engine.check_drug_interactions(project_id, drug_ids)
        for interaction in interactions:
            results.append({
                "type": "drug_interaction",
                "drug1": interaction.drug1,
                "drug2": interaction.drug2,
                "interaction_type": interaction.interaction_type,
                "severity": interaction.severity,
                "mechanism": interaction.mechanism,
                "recommendation": interaction.recommendation,
            })

    # 症状-疾病匹配
    if (not check_types or "SYMPTOM_MATCH" in check_types) and symptom_ids:
        task.update_state(
            state=ReasoningJobStatus.RUNNING,
            meta={"progress": 60, "current_step": "Matching symptoms to diseases"},
        )

        match_result = await engine.match_symptoms_to_diseases(project_id, symptom_ids)
        results.append({
            "type": "symptom_disease_match",
            "symptoms": match_result.symptoms,
            "matched_diseases": match_result.matched_diseases,
            "confidence_score": match_result.confidence_score,
        })

    # 诊疗合规性检查
    if (not check_types or "DIAGNOSIS_COMPLIANCE" in check_types) and patient_id:
        task.update_state(
            state=ReasoningJobStatus.RUNNING,
            meta={"progress": 80, "current_step": "Checking diagnosis compliance"},
        )

        # TODO: 需要诊断ID
        # compliance = await engine.check_diagnosis_compliance(project_id, patient_id, diagnosis_id)

    task.update_state(
        state=ReasoningJobStatus.RUNNING,
        meta={"progress": 90, "current_step": "Finalizing healthcare check"},
    )

    return results


async def _build_context(
    graph_repo: Neo4jGraphRepository,
    project_id: str,
    entity_ids: list[str] | None,
) -> RuleContext:
    """构建规则评估上下文"""
    context = RuleContext(project_id=project_id)

    if entity_ids:
        # 加载指定实体及其关系
        for entity_id in entity_ids:
            # TODO: 从图数据库加载实体和关系
            pass

    return context


async def _save_results(
    job_id: str,
    project_id: str,
    results: list[dict[str, Any]] | dict[str, Any],
) -> None:
    """保存推理结果到文件"""
    result_dir = settings.upload_base_dir / project_id / "reasoning"
    result_dir.mkdir(parents=True, exist_ok=True)

    result_file = result_dir / f"{job_id}.json"

    output = {
        "job_id": job_id,
        "project_id": project_id,
        "completed_at": datetime.now(UTC).isoformat(),
        "results": results,
    }

    result_file.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("Results saved to %s", result_file)
