"""抽取路由

配合NLP模块提供知识抽取功能
"""

from __future__ import annotations

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.dependencies.auth import get_current_user
from src.application.commands.extract_knowledge import (
    ExtractKnowledgeCommand,
    ExtractionSourceType,
    ExtractionStatus,
    ExtractionResult,
    ExtractedEntity,
    ExtractedRelation
)
from src.application.commands.merge_entities import (
    FindMergeCandidatesQuery,
    MergeEntitiesCommand,
    EntityMergeService
)
from src.application.services.extraction_pipeline import (
    ExtractionPipelineService,
    ExtractionPipelineResult
)
from src.domain.entities.user import User

router = APIRouter(prefix="/api/extraction", tags=["extraction"])

# 全局管道服务实例
_pipeline_service = ExtractionPipelineService()
_merge_service = EntityMergeService()


class ExtractionJobRequest(BaseModel):
    """抽取任务请求"""
    project_id: str = Field(..., description="目标项目ID")
    source_type: ExtractionSourceType = Field(default=ExtractionSourceType.TEXT)
    content: str | None = Field(default=None, description="文本内容")
    file_path: str | None = Field(default=None, description="文件路径")
    url: str | None = Field(default=None, description="URL地址")
    language: str = Field(default="zh", description="语言: zh | en")
    entity_types: List[str] = Field(default_factory=list)
    use_ocr: bool = Field(default=False, description="是否使用OCR")
    extraction_model: str = Field(default="default")


class ExtractionJobResponse(BaseModel):
    """抽取任务响应"""
    job_id: str
    status: str
    project_id: str
    created_at: str
    message: str


class ExtractionJobStatusResponse(BaseModel):
    """抽取任务状态响应"""
    job_id: str
    status: str
    project_id: str
    source_type: str
    progress: int
    result: dict[str, Any] | None
    error_message: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None


class ExtractionResultItem(BaseModel):
    """抽取结果项"""
    entities: List[dict[str, Any]]
    relations: List[dict[str, Any]]
    processing_time_ms: float
    model_name: str


class EntityMergeRequest(BaseModel):
    """实体融合请求"""
    project_id: str
    target_entity_id: str = Field(..., description="保留的目标实体ID")
    source_entity_ids: List[str] = Field(..., description="要合并的源实体ID列表")
    merge_strategy: str = Field(default="merge_all", description="merge_all | keep_target | keep_newest")


class EntityMergeResponse(BaseModel):
    """实体融合响应"""
    success: bool
    merged_entity_id: str | None
    transferred_relations: int
    deleted_entities: int
    errors: List[str]


class MergeCandidatesResponse(BaseModel):
    """融合候选响应"""
    candidates: List[List[dict[str, Any]]]
    total_groups: int


class PipelineStatisticsResponse(BaseModel):
    """管道统计响应"""
    total_jobs: int
    pending: int
    running: int
    completed: int
    failed: int
    success_rate: float


@router.post("/jobs", response_model=ExtractionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_extraction_job(
    payload: ExtractionJobRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> ExtractionJobResponse:
    """创建抽取任务
    
    异步触发知识抽取任务，返回任务ID用于查询状态
    
    source_type选项:
    - text: 从文本内容抽取，需要提供content字段
    - file: 从文件抽取，需要提供file_path字段
    - url: 从URL抽取，需要提供url字段
    """
    # 验证请求
    if payload.source_type == ExtractionSourceType.TEXT and not payload.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required for text extraction"
        )
    
    if payload.source_type == ExtractionSourceType.FILE and not payload.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File path is required for file extraction"
        )
    
    if payload.source_type == ExtractionSourceType.URL and not payload.url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is required for URL extraction"
        )
    
    command = ExtractKnowledgeCommand(
        project_id=payload.project_id,
        owner_id=current_user.id,
        source_type=payload.source_type,
        content=payload.content,
        file_path=payload.file_path,
        url=payload.url,
        language=payload.language,
        entity_types=payload.entity_types,
        use_ocr=payload.use_ocr,
        extraction_model=payload.extraction_model
    )
    
    job = await _pipeline_service.submit_job(command)
    
    return ExtractionJobResponse(
        job_id=job.id,
        status=job.status.value,
        project_id=job.project_id,
        created_at=job.created_at.isoformat(),
        message="Extraction job submitted successfully"
    )


@router.get("/jobs/{job_id}", response_model=ExtractionJobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> ExtractionJobStatusResponse:
    """查询抽取任务状态
    
    获取任务的当前状态和结果（如果已完成）
    """
    job = await _pipeline_service.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    result_data = None
    if job.result:
        result_data = {
            "entity_count": len(job.result.entities),
            "relation_count": len(job.result.relations),
            "processing_time_ms": job.result.processing_time_ms,
            "model_name": job.result.model_name
        }
    
    return ExtractionJobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        project_id=job.project_id,
        source_type=job.source_type.value,
        progress=job.progress,
        result=result_data,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None
    )


@router.get("/jobs", response_model=List[ExtractionJobStatusResponse])
async def list_jobs(
    project_id: Annotated[str | None, Query(default=None, description="项目ID")],
    status: Annotated[str | None, Query(default=None, description="状态过滤")],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(50, ge=1, le=100),
) -> List[ExtractionJobStatusResponse]:
    """列出抽取任务
    
    按项目和状态过滤任务列表
    """
    status_enum = None
    if status:
        try:
            status_enum = ExtractionStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    jobs = _pipeline_service.list_jobs(
        project_id=project_id,
        status=status_enum
    )
    
    return [
        ExtractionJobStatusResponse(
            job_id=j.id,
            status=j.status.value,
            project_id=j.project_id,
            source_type=j.source_type.value,
            progress=j.progress,
            result=None,
            error_message=j.error_message,
            created_at=j.created_at.isoformat(),
            started_at=j.started_at.isoformat() if j.started_at else None,
            completed_at=j.completed_at.isoformat() if j.completed_at else None
        )
        for j in jobs[:limit]
    ]


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """取消抽取任务"""
    success = await _pipeline_service.cancel_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job cannot be cancelled (not found or already completed)"
        )
    
    return {"success": True, "message": "Job cancelled"}


@router.post("/entities/merge", response_model=EntityMergeResponse)
async def merge_entities(
    payload: EntityMergeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> EntityMergeResponse:
    """实体融合
    
    将多个相似实体合并为一个，保留所有关系
    
    merge_strategy:
    - merge_all: 合并所有属性，冲突时保留目标实体
    - keep_target: 只保留目标实体的属性
    - keep_newest: 保留最新的属性
    """
    from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository
    
    command = MergeEntitiesCommand(
        project_id=payload.project_id,
        owner_id=current_user.id,
        target_entity_id=payload.target_entity_id,
        source_entity_ids=payload.source_entity_ids,
        merge_strategy=payload.merge_strategy
    )
    
    entity_repo = Neo4jGraphRepository()
    result = await _merge_service.merge(command, entity_repo)
    
    return EntityMergeResponse(
        success=result.success,
        merged_entity_id=result.merged_entity_id,
        transferred_relations=result.transferred_relations,
        deleted_entities=result.deleted_entities,
        errors=result.errors
    )


@router.get("/entities/merge-candidates", response_model=MergeCandidatesResponse)
async def get_merge_candidates(
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    entity_type: str | None = Query(None, description="实体类型过滤"),
    similarity_threshold: float = Query(0.8, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=500),
) -> MergeCandidatesResponse:
    """获取实体融合候选
    
    基于文本相似度自动识别可能重复的实体
    """
    from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository
    
    query = FindMergeCandidatesQuery(
        project_id=project_id,
        owner_id=current_user.id,
        entity_type=entity_type,
        similarity_threshold=similarity_threshold,
        limit=limit
    )
    
    entity_repo = Neo4jGraphRepository()
    result = await _merge_service.find_candidates(query, entity_repo)
    
    candidates = [
        [
            {
                "entity_id": c.entity_id,
                "entity_text": c.entity_text,
                "entity_type": c.entity_type,
                "similarity": c.similarity
            }
            for c in group
        ]
        for group in result.candidates
    ]
    
    return MergeCandidatesResponse(
        candidates=candidates,
        total_groups=len(candidates)
    )


@router.get("/statistics", response_model=PipelineStatisticsResponse)
async def get_pipeline_statistics(
    current_user: Annotated[User, Depends(get_current_user)],
) -> PipelineStatisticsResponse:
    """获取抽取管道统计信息"""
    stats = _pipeline_service.get_statistics()
    
    return PipelineStatisticsResponse(
        total_jobs=stats["total_jobs"],
        pending=stats["pending"],
        running=stats["running"],
        completed=stats["completed"],
        failed=stats["failed"],
        success_rate=stats["success_rate"]
    )


@router.post("/extract-sync", response_model=ExtractionResultItem)
async def extract_sync(
    payload: ExtractionJobRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> ExtractionResultItem:
    """同步抽取（立即返回结果）
    
    适用于小文本的快速抽取，不创建异步任务
    """
    command = ExtractKnowledgeCommand(
        project_id=payload.project_id,
        owner_id=current_user.id,
        source_type=payload.source_type,
        content=payload.content,
        file_path=payload.file_path,
        url=payload.url,
        language=payload.language,
        entity_types=payload.entity_types,
        use_ocr=payload.use_ocr,
        extraction_model=payload.extraction_model
    )
    
    result = await _pipeline_service.run_full_pipeline(command)
    
    if result.status == ExtractionStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.error_message or "Extraction failed"
        )
    
    return ExtractionResultItem(
        entities=[
            {
                "text": e.text,
                "entity_type": e.entity_type,
                "confidence": e.confidence,
                "properties": e.properties
            }
            for e in result.extraction_result.get("entities", [])
        ],
        relations=[
            {
                "source_text": r.source_text,
                "target_text": r.target_text,
                "relation_type": r.relation_type,
                "confidence": r.confidence
            }
            for r in result.extraction_result.get("relations", [])
        ],
        processing_time_ms=result.processing_time_ms,
        model_name="mock_extractor"
    )
