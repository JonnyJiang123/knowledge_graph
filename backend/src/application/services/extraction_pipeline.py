"""抽取管道服务

管理知识抽取的完整流程：文本抽取 -> 实体融合 -> 图谱构建
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.application.commands.extract_knowledge import (
    ExtractKnowledgeCommand,
    ExtractionJob,
    ExtractionStatus,
    KnowledgeExtractor,
    MockKnowledgeExtractor
)
from src.application.commands.build_graph import (
    BuildGraphCommand,
    BuildGraphResult,
    GraphBuilder
)
from src.application.commands.merge_entities import (
    MergeEntitiesCommand,
    EntityMergeService
)
from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """管道配置
    
    Attributes:
        enable_auto_merge: 是否启用自动实体融合
        merge_threshold: 自动融合相似度阈值
        max_concurrent_jobs: 最大并发任务数
        batch_size: 批处理大小
    """
    enable_auto_merge: bool = True
    merge_threshold: float = 0.9
    max_concurrent_jobs: int = 5
    batch_size: int = 100


@dataclass
class ExtractionPipelineResult:
    """抽取管道结果
    
    Attributes:
        job_id: 任务ID
        status: 最终状态
        extraction_result: 抽取结果
        build_result: 构建结果
        processing_time_ms: 总处理时间
        error_message: 错误信息
    """
    job_id: str
    status: ExtractionStatus
    extraction_result: dict[str, Any] = field(default_factory=dict)
    build_result: dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    error_message: str | None = None


class ExtractionPipelineService:
    """抽取管道服务
    
    管理完整的知识抽取流程：
    1. 文本抽取：从各种源抽取实体和关系
    2. 实体融合：识别并合并重复实体
    3. 图谱构建：将结果写入Neo4j
    """
    
    def __init__(
        self,
        config: PipelineConfig | None = None,
        extractor: KnowledgeExtractor | None = None
    ):
        self._config = config or PipelineConfig()
        self._extractor = extractor or MockKnowledgeExtractor()
        self._builder = GraphBuilder()
        self._merge_service = EntityMergeService()
        self._jobs: dict[str, ExtractionJob] = {}
        self._semaphore = asyncio.Semaphore(self._config.max_concurrent_jobs)
    
    async def submit_job(
        self,
        command: ExtractKnowledgeCommand
    ) -> ExtractionJob:
        """提交抽取任务
        
        Args:
            command: 抽取命令
            
        Returns:
            创建的任务
        """
        job = ExtractionJob(
            project_id=command.project_id,
            owner_id=command.owner_id,
            source_type=command.source_type,
            status=ExtractionStatus.PENDING
        )
        
        self._jobs[job.id] = job
        
        # 异步启动任务
        asyncio.create_task(self._run_job(job, command))
        
        return job
    
    async def get_job(self, job_id: str) -> ExtractionJob | None:
        """获取任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务对象，如果不存在返回None
        """
        return self._jobs.get(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """取消任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            是否成功取消
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [ExtractionStatus.PENDING, ExtractionStatus.RUNNING]:
            job.status = ExtractionStatus.CANCELLED
            return True
        
        return False
    
    async def _run_job(
        self,
        job: ExtractionJob,
        command: ExtractKnowledgeCommand
    ) -> None:
        """运行抽取任务"""
        import time
        
        start_time = time.time()
        
        async with self._semaphore:
            try:
                job.status = ExtractionStatus.RUNNING
                job.started_at = datetime.now(UTC)
                job.progress = 10
                
                # 第一步：知识抽取
                logger.info(f"Job {job.id}: Starting knowledge extraction")
                extraction_result = await self._extractor.extract(command)
                job.progress = 40
                
                # 第二步：实体融合（如果启用）
                if self._config.enable_auto_merge:
                    logger.info(f"Job {job.id}: Starting entity merging")
                    extraction_result = await self._auto_merge_entities(
                        command.project_id,
                        extraction_result
                    )
                
                job.progress = 60
                
                # 第三步：图谱构建
                logger.info(f"Job {job.id}: Starting graph building")
                entity_repo = Neo4jGraphRepository()
                
                build_command = BuildGraphCommand(
                    project_id=command.project_id,
                    owner_id=command.owner_id,
                    entities=[
                        {
                            "text": e.text,
                            "entity_type": e.entity_type,
                            "properties": e.properties
                        }
                        for e in extraction_result.entities
                    ],
                    relations=[
                        {
                            "source_text": r.source_text,
                            "target_text": r.target_text,
                            "relation_type": r.relation_type,
                            "properties": r.properties
                        }
                        for r in extraction_result.relations
                    ],
                    merge_duplicates=self._config.enable_auto_merge
                )
                
                build_result = await self._builder.build(build_command, entity_repo)
                job.progress = 100
                
                # 更新任务状态
                job.status = ExtractionStatus.COMPLETED
                job.completed_at = datetime.now(UTC)
                job.result = extraction_result
                
                processing_time = (time.time() - start_time) * 1000
                
                logger.info(
                    f"Job {job.id}: Completed. "
                    f"Entities: {build_result.created_entities}, "
                    f"Relations: {build_result.created_relations}, "
                    f"Time: {processing_time:.2f}ms"
                )
                
            except asyncio.CancelledError:
                job.status = ExtractionStatus.CANCELLED
                logger.info(f"Job {job.id}: Cancelled")
                
            except Exception as e:
                job.status = ExtractionStatus.FAILED
                job.error_message = str(e)
                logger.error(f"Job {job.id}: Failed - {e}")
    
    async def _auto_merge_entities(
        self,
        project_id: str,
        extraction_result: Any
    ) -> Any:
        """自动合并抽取的实体"""
        # 创建实体文本到抽取实体的映射
        entity_map = {}
        merged_entities = []
        
        for entity in extraction_result.entities:
            # 标准化文本
            normalized = entity.text.strip()
            
            # 查找相似实体
            found_match = False
            for existing_text, existing_entity in entity_map.items():
                similarity = self._calculate_similarity(normalized, existing_text)
                if similarity >= self._config.merge_threshold:
                    # 合并属性
                    existing_entity.properties.update(entity.properties)
                    found_match = True
                    break
            
            if not found_match:
                entity_map[normalized] = entity
                merged_entities.append(entity)
        
        # 更新关系中的实体引用
        for relation in extraction_result.relations:
            # 标准化关系中的实体引用
            relation.source_text = relation.source_text.strip()
            relation.target_text = relation.target_text.strip()
        
        extraction_result.entities = merged_entities
        return extraction_result
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        if text1 == text2:
            return 1.0
        
        # 简单字符集合相似度
        set1 = set(text1)
        set2 = set(text2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    async def run_full_pipeline(
        self,
        command: ExtractKnowledgeCommand
    ) -> ExtractionPipelineResult:
        """运行完整管道（同步等待结果）
        
        Args:
            command: 抽取命令
            
        Returns:
            管道结果
        """
        import time
        
        start_time = time.time()
        job = await self.submit_job(command)
        
        # 等待任务完成
        while job.status in [ExtractionStatus.PENDING, ExtractionStatus.RUNNING]:
            await asyncio.sleep(0.5)
            job = await self.get_job(job.id) or job
        
        processing_time = (time.time() - start_time) * 1000
        
        if job.status == ExtractionStatus.COMPLETED:
            return ExtractionPipelineResult(
                job_id=job.id,
                status=job.status,
                extraction_result={
                    "entity_count": len(job.result.entities) if job.result else 0,
                    "relation_count": len(job.result.relations) if job.result else 0,
                    "processing_time_ms": job.result.processing_time_ms if job.result else 0
                },
                build_result={
                    "success": True
                },
                processing_time_ms=processing_time
            )
        else:
            return ExtractionPipelineResult(
                job_id=job.id,
                status=job.status,
                error_message=job.error_message,
                processing_time_ms=processing_time
            )
    
    def list_jobs(
        self,
        project_id: str | None = None,
        status: ExtractionStatus | None = None
    ) -> list[ExtractionJob]:
        """列出任务
        
        Args:
            project_id: 按项目过滤
            status: 按状态过滤
            
        Returns:
            任务列表
        """
        jobs = list(self._jobs.values())
        
        if project_id:
            jobs = [j for j in jobs if j.project_id == project_id]
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        # 按创建时间倒序
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        
        return jobs
    
    def get_statistics(self) -> dict[str, Any]:
        """获取管道统计信息"""
        total = len(self._jobs)
        pending = sum(1 for j in self._jobs.values() if j.status == ExtractionStatus.PENDING)
        running = sum(1 for j in self._jobs.values() if j.status == ExtractionStatus.RUNNING)
        completed = sum(1 for j in self._jobs.values() if j.status == ExtractionStatus.COMPLETED)
        failed = sum(1 for j in self._jobs.values() if j.status == ExtractionStatus.FAILED)
        
        return {
            "total_jobs": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "success_rate": round(completed / total * 100, 2) if total > 0 else 0
        }
