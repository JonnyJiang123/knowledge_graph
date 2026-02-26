from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import get_current_user
from src.api.schemas.reasoning import (
    DiagnosisComplianceResponse,
    DrugInteractionResultResponse,
    FraudDetectionResultResponse,
    ReasoningJobStatusResponse,
    ReasoningResultDetail,
    RiskPropagationResultResponse,
    RuleCreate,
    RuleListResponse,
    RuleResponse,
    RuleUpdate,
    RunFinanceFraudRequest,
    RunHealthcareCheckRequest,
    RunReasoningRequest,
    RunReasoningResponse,
    RunRiskPropagationRequest,
    SymptomDiseaseMatchResponse,
)
from src.application.commands.create_rule import (
    ActivateRuleCommand,
    CreateRuleCommand,
    DeactivateRuleCommand,
    DeleteRuleCommand,
    UpdateRuleCommand,
)
from src.application.commands.run_reasoning import (
    RunFinanceFraudDetectionCommand,
    RunHealthcareCheckCommand,
    RunReasoningCommand,
    RunRiskPropagationCommand,
)
from src.application.queries.get_reasoning_results import (
    GetReasoningJobStatusQuery,
    GetReasoningResultQuery,
    GetReasoningRuleDetailQuery,
    ListReasoningResultsQuery,
    ListReasoningRulesQuery,
)
from src.domain.entities.rule import Action, Condition
from src.domain.entities.user import User
from src.domain.value_objects.rule_type import RuleType

router = APIRouter(prefix="/api/reasoning", tags=["reasoning"])


# ========== Helper Functions ==========

def _map_reasoning_error(exc: Exception) -> HTTPException:
    """将领域错误映射为HTTP异常"""
    error_message = str(exc).lower()

    if "not found" in error_message:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    if "access" in error_message or "permission" in error_message:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
    if "invalid" in error_message or "validation" in error_message:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Internal server error: {exc}",
    )


def _convert_conditions(conditions: list[Any]) -> list[Condition]:
    """转换条件Schema为领域对象"""
    return [
        Condition(
            field=c.field,
            operator=c.operator,
            value=c.value,
        )
        for c in conditions
    ]


def _convert_actions(actions: list[Any]) -> list[Action]:
    """转换动作Schema为领域对象"""
    return [
        Action(
            action_type=a.action_type,
            target=a.target,
            params=a.params,
        )
        for a in actions
    ]


# ========== Rule Management Endpoints ==========

@router.post(
    "/projects/{project_id}/rules",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建推理规则",
)
async def create_rule(
    project_id: str,
    payload: RuleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """创建新的推理规则"""
    command = CreateRuleCommand(
        project_id=project_id,
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        rule_type=payload.rule_type,
        conditions=_convert_conditions(payload.conditions),
        actions=_convert_actions(payload.actions),
        priority=payload.priority,
        is_active=payload.is_active,
    )

    # TODO: 调用服务层处理命令
    # result = await reasoning_service.create_rule(command)

    # 模拟响应
    return RuleResponse(
        id="rule-123",
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        rule_type=payload.rule_type,
        conditions=payload.conditions,
        actions=payload.actions,
        priority=payload.priority,
        is_active=payload.is_active,
        created_at=__import__("datetime").datetime.now(),
        updated_at=__import__("datetime").datetime.now(),
    )


@router.get(
    "/projects/{project_id}/rules",
    response_model=RuleListResponse,
    summary="列出推理规则",
)
async def list_rules(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    rule_type: Annotated[RuleType | None, Query(description="按规则类型筛选")] = None,
    is_active: Annotated[bool | None, Query(description="按激活状态筛选")] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """列出项目中的所有推理规则"""
    query = ListReasoningRulesQuery(
        project_id=project_id,
        owner_id=current_user.id,
        rule_type=rule_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

    # TODO: 调用服务层处理查询
    # result = await reasoning_service.list_rules(query)

    # 模拟响应
    return RuleListResponse(
        items=[],
        total=0,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/rules/{rule_id}",
    response_model=RuleResponse,
    summary="获取规则详情",
)
async def get_rule(
    rule_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取规则的详细信息"""
    query = GetReasoningRuleDetailQuery(
        rule_id=rule_id,
        owner_id=current_user.id,
    )

    # TODO: 调用服务层处理查询
    # result = await reasoning_service.get_rule(query)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.put(
    "/rules/{rule_id}",
    response_model=RuleResponse,
    summary="更新规则",
)
async def update_rule(
    rule_id: str,
    payload: RuleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """更新现有规则"""
    command = UpdateRuleCommand(
        rule_id=rule_id,
        owner_id=current_user.id,
        name=payload.name,
        description=payload.description,
        conditions=_convert_conditions(payload.conditions) if payload.conditions else None,
        actions=_convert_actions(payload.actions) if payload.actions else None,
        priority=payload.priority,
        is_active=payload.is_active,
    )

    # TODO: 调用服务层处理命令
    # result = await reasoning_service.update_rule(command)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除规则",
)
async def delete_rule(
    rule_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """删除推理规则"""
    command = DeleteRuleCommand(
        rule_id=rule_id,
        owner_id=current_user.id,
    )

    # TODO: 调用服务层处理命令
    # await reasoning_service.delete_rule(command)

    return None


@router.post(
    "/rules/{rule_id}/activate",
    response_model=RuleResponse,
    summary="激活规则",
)
async def activate_rule(
    rule_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """激活推理规则"""
    command = ActivateRuleCommand(
        rule_id=rule_id,
        owner_id=current_user.id,
    )

    # TODO: 调用服务层处理命令

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.post(
    "/rules/{rule_id}/deactivate",
    response_model=RuleResponse,
    summary="停用规则",
)
async def deactivate_rule(
    rule_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """停用推理规则"""
    command = DeactivateRuleCommand(
        rule_id=rule_id,
        owner_id=current_user.id,
    )

    # TODO: 调用服务层处理命令

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


# ========== Reasoning Execution Endpoints ==========

@router.post(
    "/projects/{project_id}/rules/run",
    response_model=RunReasoningResponse,
    summary="执行推理",
)
async def run_reasoning(
    project_id: str,
    payload: RunReasoningRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """执行推理规则"""
    command = RunReasoningCommand(
        project_id=project_id,
        owner_id=current_user.id,
        rule_ids=payload.rule_ids,
        rule_types=payload.rule_types,
        target_entity_ids=payload.target_entity_ids,
        parameters=payload.parameters,
        async_execution=payload.async_execution,
    )

    # TODO: 调用服务层处理命令
    # result = await reasoning_service.run_reasoning(command)

    # 模拟响应
    return RunReasoningResponse(
        job_id=f"job-{project_id}-{__import__('uuid').uuid4().hex[:8]}",
        status="pending" if payload.async_execution else "running",
        message="Reasoning job started",
        estimated_duration=30,
    )


@router.post(
    "/projects/{project_id}/fraud-detection",
    response_model=RunReasoningResponse,
    summary="执行金融欺诈检测",
)
async def run_fraud_detection(
    project_id: str,
    payload: RunFinanceFraudRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """执行金融欺诈检测分析"""
    command = RunFinanceFraudDetectionCommand(
        project_id=project_id,
        owner_id=current_user.id,
        detection_types=payload.detection_types,
        target_entity_ids=payload.target_entity_ids,
        async_execution=payload.async_execution,
    )

    # TODO: 调用服务层处理命令

    return RunReasoningResponse(
        job_id=f"fraud-{project_id}-{__import__('uuid').uuid4().hex[:8]}",
        status="pending" if payload.async_execution else "running",
        message="Fraud detection job started",
        estimated_duration=60,
    )


@router.post(
    "/projects/{project_id}/risk-propagation",
    response_model=RunReasoningResponse,
    summary="执行风险传播分析",
)
async def run_risk_propagation(
    project_id: str,
    payload: RunRiskPropagationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """执行风险传播分析"""
    command = RunRiskPropagationCommand(
        project_id=project_id,
        owner_id=current_user.id,
        source_entity_id=payload.source_entity_id,
        risk_level=payload.risk_level.value,
        max_depth=payload.max_depth,
        async_execution=payload.async_execution,
    )

    # TODO: 调用服务层处理命令

    return RunReasoningResponse(
        job_id=f"risk-{project_id}-{__import__('uuid').uuid4().hex[:8]}",
        status="pending" if payload.async_execution else "running",
        message="Risk propagation analysis started",
        estimated_duration=45,
    )


@router.post(
    "/projects/{project_id}/healthcare-check",
    response_model=RunReasoningResponse,
    summary="执行医疗检查",
)
async def run_healthcare_check(
    project_id: str,
    payload: RunHealthcareCheckRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """执行医疗合规性检查"""
    command = RunHealthcareCheckCommand(
        project_id=project_id,
        owner_id=current_user.id,
        check_types=payload.check_types,
        patient_id=payload.patient_id,
        drug_ids=payload.drug_ids,
        symptom_ids=payload.symptom_ids,
        async_execution=payload.async_execution,
    )

    # TODO: 调用服务层处理命令

    return RunReasoningResponse(
        job_id=f"health-{project_id}-{__import__('uuid').uuid4().hex[:8]}",
        status="pending" if payload.async_execution else "running",
        message="Healthcare check started",
        estimated_duration=30,
    )


# ========== Results Endpoints ==========

@router.get(
    "/results/{job_id}",
    response_model=ReasoningResultDetail,
    summary="获取推理结果",
)
async def get_reasoning_result(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取推理任务的结果"""
    query = GetReasoningResultQuery(
        job_id=job_id,
        owner_id=current_user.id,
    )

    # TODO: 调用服务层处理查询

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.get(
    "/results/{job_id}/status",
    response_model=ReasoningJobStatusResponse,
    summary="获取推理任务状态",
)
async def get_reasoning_job_status(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取推理任务的执行状态"""
    query = GetReasoningJobStatusQuery(
        job_id=job_id,
        owner_id=current_user.id,
    )

    # TODO: 调用服务层处理查询

    # 模拟响应
    return ReasoningJobStatusResponse(
        job_id=job_id,
        status="running",
        progress=50.0,
        current_step="Evaluating rules",
    )


@router.get(
    "/projects/{project_id}/results",
    summary="列出推理结果",
)
async def list_reasoning_results(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    rule_id: Annotated[str | None, Query(description="按规则ID筛选")] = None,
    rule_type: Annotated[RuleType | None, Query(description="按规则类型筛选")] = None,
    matched_only: bool = Query(True, description="只返回匹配的结果"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """列出项目的推理结果"""
    query = ListReasoningResultsQuery(
        project_id=project_id,
        owner_id=current_user.id,
        rule_id=rule_id,
        rule_type=rule_type,
        matched_only=matched_only,
        limit=limit,
        offset=offset,
    )

    # TODO: 调用服务层处理查询

    return {
        "items": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


# ========== Specific Result Endpoints ==========

@router.get(
    "/results/{job_id}/fraud",
    response_model=list[FraudDetectionResultResponse],
    summary="获取欺诈检测结果",
)
async def get_fraud_detection_results(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取金融欺诈检测的详细结果"""
    # TODO: 实现获取欺诈检测结果

    return []


@router.get(
    "/results/{job_id}/risk-propagation",
    response_model=RiskPropagationResultResponse,
    summary="获取风险传播结果",
)
async def get_risk_propagation_results(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取风险传播分析的详细结果"""
    # TODO: 实现获取风险传播结果

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.get(
    "/results/{job_id}/drug-interactions",
    response_model=list[DrugInteractionResultResponse],
    summary="获取药物相互作用结果",
)
async def get_drug_interaction_results(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取药物相互作用检查的详细结果"""
    # TODO: 实现获取药物相互作用结果

    return []


@router.get(
    "/results/{job_id}/symptom-matches",
    response_model=SymptomDiseaseMatchResponse,
    summary="获取症状-疾病匹配结果",
)
async def get_symptom_match_results(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取症状-疾病匹配的详细结果"""
    # TODO: 实现获取症状-疾病匹配结果

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )


@router.get(
    "/results/{job_id}/diagnosis-compliance",
    response_model=DiagnosisComplianceResponse,
    summary="获取诊疗合规性结果",
)
async def get_diagnosis_compliance_results(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """获取诊疗合规性检查的详细结果"""
    # TODO: 实现获取诊疗合规性结果

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )
