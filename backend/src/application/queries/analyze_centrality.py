"""中心性分析查询

调用GDS算法计算节点中心性分数
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Type

from src.infrastructure.persistence.neo4j.graph_algorithms import (
    GraphAlgorithmRunner,
    GraphAlgorithmError
)


@dataclass(slots=True)
class AnalyzeCentralityQuery:
    """中心性分析查询参数
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID（用于权限验证）
        algorithm: 算法类型 (pagerank, betweenness, degree)
        limit: 返回结果数量
    """
    project_id: str
    owner_id: str
    algorithm: str = "pagerank"  # pagerank, betweenness, degree
    limit: int = 100


@dataclass(slots=True)
class CentralityScore:
    """中心性分数
    
    Attributes:
        entity_id: 实体ID
        name: 实体名称
        entity_type: 实体类型
        score: 中心性分数
        rank: 排名
    """
    entity_id: str
    name: str
    entity_type: str
    score: float
    rank: int


@dataclass(slots=True)
class CentralityAnalysisResult:
    """中心性分析结果
    
    Attributes:
        algorithm: 使用的算法
        scores: 中心性分数列表
        total_entities: 分析的实体总数
        execution_time_ms: 执行时间（毫秒）
    """
    algorithm: str
    scores: list[CentralityScore]
    total_entities: int
    execution_time_ms: float | None = None


class AnalyzeCentralityHandler:
    """中心性分析处理器"""
    
    SUPPORTED_ALGORITHMS = ["pagerank", "betweenness", "degree"]
    
    def __init__(self, runner: GraphAlgorithmRunner | None = None):
        self._runner = runner or GraphAlgorithmRunner()
    
    async def handle(self, query: AnalyzeCentralityQuery) -> CentralityAnalysisResult:
        """执行中心性分析
        
        Args:
            query: 分析查询参数
            
        Returns:
            中心性分析结果
        """
        import time
        
        if query.algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm: {query.algorithm}. "
                f"Supported: {self.SUPPORTED_ALGORITHMS}"
            )
        
        start_time = time.time()
        
        try:
            if query.algorithm == "pagerank":
                raw_scores = await self._runner.run_pagerank(
                    project_id=query.project_id,
                    limit=query.limit
                )
            elif query.algorithm == "betweenness":
                raw_scores = await self._runner.run_betweenness(
                    project_id=query.project_id,
                    limit=query.limit
                )
            else:  # degree
                from src.infrastructure.persistence.neo4j.client import Neo4jClient
                from src.infrastructure.persistence.neo4j import cypher_queries as queries
                
                raw_scores = await Neo4jClient.execute_read(
                    queries.DEGREE_CENTRALITY,
                    {"project_id": query.project_id, "limit": query.limit}
                )
            
            execution_time = (time.time() - start_time) * 1000
            
            # 转换为标准格式
            scores = []
            for rank, record in enumerate(raw_scores, 1):
                score = CentralityScore(
                    entity_id=record.get("entity_id", ""),
                    name=record.get("name", ""),
                    entity_type=record.get("entity_type", "OTHER"),
                    score=float(record.get("score", 0)),
                    rank=rank
                )
                scores.append(score)
            
            return CentralityAnalysisResult(
                algorithm=query.algorithm,
                scores=scores,
                total_entities=len(scores),
                execution_time_ms=round(execution_time, 2)
            )
            
        except GraphAlgorithmError as e:
            # 算法错误（如GDS未安装）
            if "GDS" in str(e) or "not available" in str(e).lower():
                # 降级到degree centrality
                return await self._fallback_to_degree(query)
            raise
    
    async def _fallback_to_degree(
        self,
        query: AnalyzeCentralityQuery
    ) -> CentralityAnalysisResult:
        """降级到degree centrality"""
        import time
        from src.infrastructure.persistence.neo4j.client import Neo4jClient
        from src.infrastructure.persistence.neo4j import cypher_queries as queries
        
        start_time = time.time()
        
        raw_scores = await Neo4jClient.execute_read(
            queries.DEGREE_CENTRALITY,
            {"project_id": query.project_id, "limit": query.limit}
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        scores = []
        for rank, record in enumerate(raw_scores, 1):
            score = CentralityScore(
                entity_id=record.get("entity_id", ""),
                name=record.get("name", ""),
                entity_type=record.get("entity_type", "OTHER"),
                score=float(record.get("score", 0)),
                rank=rank
            )
            scores.append(score)
        
        return CentralityAnalysisResult(
            algorithm="degree (fallback)",
            scores=scores,
            total_entities=len(scores),
            execution_time_ms=round(execution_time, 2)
        )


@dataclass(slots=True)
class AnalyzeCommunitiesQuery:
    """社区发现查询参数
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID（用于权限验证）
        algorithm: 算法类型 (louvain, label_propagation)
    """
    project_id: str
    owner_id: str
    algorithm: str = "louvain"


@dataclass(slots=True)
class CommunityMember:
    """社区成员"""
    entity_id: str
    name: str
    entity_type: str


@dataclass(slots=True)
class Community:
    """社区"""
    id: int
    size: int
    members: list[CommunityMember]


@dataclass(slots=True)
class CommunityAnalysisResult:
    """社区分析结果"""
    algorithm: str
    communities: list[Community]
    total_communities: int


class AnalyzeCommunitiesHandler:
    """社区发现处理器"""
    
    def __init__(self, runner: GraphAlgorithmRunner | None = None):
        self._runner = runner or GraphAlgorithmRunner()
    
    async def handle(self, query: AnalyzeCommunitiesQuery) -> CommunityAnalysisResult:
        """执行社区发现分析
        
        Args:
            query: 社区分析查询参数
            
        Returns:
            社区分析结果
        """
        try:
            if query.algorithm == "louvain":
                raw_results = await self._runner.run_louvain(
                    project_id=query.project_id
                )
            else:
                raise ValueError(f"Unsupported community algorithm: {query.algorithm}")
            
            # 按社区ID分组
            community_map = {}
            for record in raw_results:
                comm_id = record.get("community_id", 0)
                member = CommunityMember(
                    entity_id=record.get("entity_id", ""),
                    name=record.get("name", ""),
                    entity_type=record.get("entity_type", "OTHER")
                )
                
                if comm_id not in community_map:
                    community_map[comm_id] = []
                community_map[comm_id].append(member)
            
            # 构建社区列表
            communities = []
            for comm_id, members in community_map.items():
                communities.append(Community(
                    id=comm_id,
                    size=len(members),
                    members=members[:50]  # 限制每个社区返回的成员数
                ))
            
            # 按大小排序
            communities.sort(key=lambda c: c.size, reverse=True)
            
            return CommunityAnalysisResult(
                algorithm=query.algorithm,
                communities=communities,
                total_communities=len(communities)
            )
            
        except GraphAlgorithmError:
            # GDS不可用，返回空结果
            return CommunityAnalysisResult(
                algorithm=query.algorithm,
                communities=[],
                total_communities=0
            )
