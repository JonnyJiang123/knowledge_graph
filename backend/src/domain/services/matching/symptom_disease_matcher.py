"""症状-疾病匹配服务"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Symptom:
    """症状"""
    id: str
    name: str
    category: str  # 全身、呼吸、消化等
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Disease:
    """疾病"""
    id: str
    name: str
    icd_code: str  # ICD-10编码
    symptoms: list[str]  # 相关症状ID列表
    departments: list[str]  # 推荐科室
    severity: str  # HIGH, MEDIUM, LOW
    description: str = ""


@dataclass
class MatchResult:
    """匹配结果"""
    disease: Disease
    match_score: float  # 0-1匹配度
    matched_symptoms: list[str]  # 匹配上的症状
    missing_symptoms: list[str]  # 未匹配的典型症状


class SymptomDiseaseMatcher(ABC):
    """症状-疾病匹配器"""

    @abstractmethod
    async def match(
        self,
        symptoms: list[str],
        top_k: int = 5
    ) -> list[MatchResult]:
        """根据症状匹配可能的疾病

        Args:
            symptoms: 症状ID列表
            top_k: 返回前k个最可能的疾病

        Returns:
            匹配结果列表
        """
        ...

    @abstractmethod
    async def get_related_symptoms(
        self,
        symptom_ids: list[str]
    ) -> list[Symptom]:
        """获取相关症状

        Args:
            symptom_ids: 当前症状ID列表

        Returns:
            可能相关的其他症状
        """
        ...


class GraphBasedSymptomMatcher(SymptomDiseaseMatcher):
    """基于知识图谱的症状匹配器"""

    def __init__(self, graph_repository):
        self.graph_repository = graph_repository
        self._symptom_cache: dict[str, Symptom] = {}
        self._disease_cache: dict[str, Disease] = {}

    async def match(
        self,
        symptoms: list[str],
        top_k: int = 5
    ) -> list[MatchResult]:
        """基于图谱的症状-疾病匹配"""
        # 查询图谱中与症状相关的疾病
        query = """
        MATCH (s:Symptom)-[:SYMPTOM_OF]->(d:Disease)
        WHERE s.id IN $symptom_ids
        RETURN d, collect(s.id) as matched_symptoms,
               count(s) as symptom_count
        ORDER BY symptom_count DESC
        LIMIT $top_k
        """

        # 这里应该调用图谱查询
        # 简化实现：基于缓存数据计算
        results = []

        for disease_id, disease in self._disease_cache.items():
            matched = set(symptoms) & set(disease.symptoms)
            if matched:
                score = len(matched) / len(disease.symptoms)
                results.append(MatchResult(
                    disease=disease,
                    match_score=score,
                    matched_symptoms=list(matched),
                    missing_symptoms=list(set(disease.symptoms) - matched)
                ))

        # 按匹配分数排序
        results.sort(key=lambda x: x.match_score, reverse=True)
        return results[:top_k]

    async def get_related_symptoms(
        self,
        symptom_ids: list[str]
    ) -> list[Symptom]:
        """获取可能相关的其他症状"""
        # 查询图谱中常与这些症状同时出现的其他症状
        query = """
        MATCH (s1:Symptom)-[:CO_OCCURS_WITH]->(s2:Symptom)
        WHERE s1.id IN $symptom_ids AND NOT s2.id IN $symptom_ids
        RETURN s2, count(*) as frequency
        ORDER BY frequency DESC
        LIMIT 10
        """

        return []

    def add_symptom(self, symptom: Symptom) -> None:
        """添加症状到缓存"""
        self._symptom_cache[symptom.id] = symptom

    def add_disease(self, disease: Disease) -> None:
        """添加疾病到缓存"""
        self._disease_cache[disease.id] = disease
