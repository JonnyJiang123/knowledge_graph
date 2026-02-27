from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.domain.ports.nlp.ner_extractor import NamedEntity


@dataclass
class ExtractedRelation:
    """抽取的关系"""
    source_entity: NamedEntity
    target_entity: NamedEntity
    relation_type: str
    confidence: float = 0.0
    evidence: str = ""  # 关系证据文本
    properties: dict[str, Any] = field(default_factory=dict)


class RelationExtractor(ABC):
    """关系抽取器端口接口"""

    @abstractmethod
    async def extract_relations(
        self,
        text: str,
        entities: list[NamedEntity]
    ) -> list[ExtractedRelation]:
        """从文本中抽取实体间的关系

        Args:
            text: 输入文本
            entities: 已识别的实体列表

        Returns:
            ExtractedRelation列表
        """
        ...

    @abstractmethod
    async def extract_with_patterns(
        self,
        text: str,
        entities: list[NamedEntity],
        patterns: list[dict[str, Any]]
    ) -> list[ExtractedRelation]:
        """使用指定模式抽取关系

        Args:
            text: 输入文本
            entities: 已识别的实体列表
            patterns: 关系模式列表

        Returns:
            ExtractedRelation列表
        """
        ...
