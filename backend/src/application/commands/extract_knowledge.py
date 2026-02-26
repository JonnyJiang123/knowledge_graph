"""知识抽取命令

从文本中抽取实体和关系
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class ExtractionStatus(str, Enum):
    """抽取任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExtractionSourceType(str, Enum):
    """抽取源类型"""
    TEXT = "text"
    FILE = "file"
    URL = "url"


@dataclass
class ExtractedEntity:
    """抽取的实体"""
    text: str
    entity_type: str
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractedRelation:
    """抽取的关系"""
    source_text: str
    target_text: str
    relation_type: str
    confidence: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """抽取结果"""
    entities: list[ExtractedEntity]
    relations: list[ExtractedRelation]
    processing_time_ms: float
    model_name: str


@dataclass
class ExtractKnowledgeCommand:
    """知识抽取命令
    
    Attributes:
        project_id: 目标项目ID
        owner_id: 用户ID
        source_type: 源类型 (text/file/url)
        content: 文本内容 (source_type为text时使用)
        file_path: 文件路径 (source_type为file时使用)
        url: URL地址 (source_type为url时使用)
        language: 文本语言 (zh/en)
        entity_types: 指定抽取的实体类型
        use_ocr: 是否使用OCR（图片/PDF）
        extraction_model: 使用的抽取模型
    """
    project_id: str
    owner_id: str
    source_type: ExtractionSourceType
    content: str | None = None
    file_path: str | None = None
    url: str | None = None
    language: str = "zh"
    entity_types: list[str] = field(default_factory=list)
    use_ocr: bool = False
    extraction_model: str = "default"


@dataclass
class ExtractionJob:
    """抽取任务"""
    id: str = field(default_factory=lambda: str(uuid4()))
    project_id: str = ""
    owner_id: str = ""
    status: ExtractionStatus = ExtractionStatus.PENDING
    source_type: ExtractionSourceType = ExtractionSourceType.TEXT
    progress: int = 0  # 0-100
    result: ExtractionResult | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None


class KnowledgeExtractor:
    """知识抽取器
    
    负责从各种来源抽取实体和关系。
    这是一个抽象基类，具体实现可以是：
    - 基于规则的抽取
    - 基于NLP模型的抽取
    - 基于LLM的抽取
    """
    
    async def extract(self, command: ExtractKnowledgeCommand) -> ExtractionResult:
        """执行知识抽取
        
        Args:
            command: 抽取命令
            
        Returns:
            抽取结果
        """
        raise NotImplementedError("Subclasses must implement extract()")


class MockKnowledgeExtractor(KnowledgeExtractor):
    """模拟知识抽取器（用于开发测试）"""
    
    async def extract(self, command: ExtractKnowledgeCommand) -> ExtractionResult:
        """模拟抽取"""
        import random
        import time
        
        start_time = time.time()
        
        # 模拟处理
        if command.source_type == ExtractionSourceType.TEXT and command.content:
            content = command.content
            # 简单模拟：按行分割作为句子
            sentences = [s.strip() for s in content.split("。") if s.strip()]
            
            entities = []
            relations = []
            
            # 模拟抽取实体
            for i, sentence in enumerate(sentences[:5]):  # 限制处理前5句
                # 简单模拟实体抽取
                if "公司" in sentence or "企业" in sentence:
                    entities.append(ExtractedEntity(
                        text=f"公司{i+1}",
                        entity_type="ENTERPRISE",
                        start_pos=0,
                        end_pos=10,
                        confidence=random.uniform(0.7, 0.95)
                    ))
                if "人" in sentence or "先生" in sentence or "女士" in sentence:
                    entities.append(ExtractedEntity(
                        text=f"人物{i+1}",
                        entity_type="PERSON",
                        start_pos=0,
                        end_pos=10,
                        confidence=random.uniform(0.7, 0.95)
                    ))
            
            # 模拟抽取关系
            if len(entities) >= 2:
                relations.append(ExtractedRelation(
                    source_text=entities[0].text,
                    target_text=entities[1].text,
                    relation_type="OWNS",
                    confidence=random.uniform(0.6, 0.9)
                ))
        
        processing_time = (time.time() - start_time) * 1000
        
        return ExtractionResult(
            entities=entities if 'entities' in dir() else [],
            relations=relations if 'relations' in dir() else [],
            processing_time_ms=processing_time,
            model_name="mock_extractor"
        )
