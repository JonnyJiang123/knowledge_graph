"""中心性分析服务 - 识别核心节点"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CentralityScore:
    """中心性分数"""
    entity_id: str
    entity_name: str
    entity_type: str
    degree_centrality: float = 0.0
    betweenness_centrality: float = 0.0
    pagerank: float = 0.0
    overall_score: float = 0.0
    properties: dict[str, Any] = field(default_factory=dict)


class CentralityAnalyzer(ABC):
    """中心性分析器"""

    @abstractmethod
    async def analyze_degree_centrality(
        self,
        project_id: str,
        top_k: int = 10
    ) -> list[CentralityScore]:
        """度中心性分析"""
        ...

    @abstractmethod
    async def analyze_betweenness_centrality(
        self,
        project_id: str,
        top_k: int = 10
    ) -> list[CentralityScore]:
        """中介中心性分析"""
        ...

    @abstractmethod
    async def analyze_pagerank(
        self,
        project_id: str,
        top_k: int = 10
    ) -> list[CentralityScore]:
        """PageRank分析"""
        ...


class NetworkXCentralityAnalyzer(CentralityAnalyzer):
    """基于NetworkX的中心性分析实现"""

    def __init__(self, graph_repository):
        self.graph_repository = graph_repository

    async def analyze_degree_centrality(
        self,
        project_id: str,
        top_k: int = 10
    ) -> list[CentralityScore]:
        """度中心性 - 连接数量"""
        try:
            import networkx as nx

            # 获取子图
            graph_data = await self.graph_repository.get_subgraph(project_id, limit=1000)

            G = nx.DiGraph()
            for node in graph_data.get("nodes", []):
                G.add_node(node["id"], **node.get("properties", {}))
            for edge in graph_data.get("edges", []):
                G.add_edge(edge["source"], edge["target"], **edge.get("properties", {}))

            # 计算度中心性
            centrality = nx.degree_centrality(G)

            # 排序并返回前k个
            sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:top_k]

            scores = []
            for node_id, score in sorted_nodes:
                node_data = G.nodes.get(node_id, {})
                scores.append(CentralityScore(
                    entity_id=node_id,
                    entity_name=node_data.get("name", node_id),
                    entity_type=node_data.get("type", "UNKNOWN"),
                    degree_centrality=score,
                    overall_score=score
                ))

            return scores
        except ImportError:
            return []

    async def analyze_betweenness_centrality(
        self,
        project_id: str,
        top_k: int = 10
    ) -> list[CentralityScore]:
        """中介中心性 - 作为桥梁的重要性"""
        try:
            import networkx as nx

            graph_data = await self.graph_repository.get_subgraph(project_id, limit=1000)

            G = nx.DiGraph()
            for node in graph_data.get("nodes", []):
                G.add_node(node["id"], **node.get("properties", {}))
            for edge in graph_data.get("edges", []):
                G.add_edge(edge["source"], edge["target"])

            centrality = nx.betweenness_centrality(G)
            sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:top_k]

            scores = []
            for node_id, score in sorted_nodes:
                node_data = G.nodes.get(node_id, {})
                scores.append(CentralityScore(
                    entity_id=node_id,
                    entity_name=node_data.get("name", node_id),
                    entity_type=node_data.get("type", "UNKNOWN"),
                    betweenness_centrality=score,
                    overall_score=score
                ))

            return scores
        except ImportError:
            return []

    async def analyze_pagerank(
        self,
        project_id: str,
        top_k: int = 10
    ) -> list[CentralityScore]:
        """PageRank - 节点重要性"""
        try:
            import networkx as nx

            graph_data = await self.graph_repository.get_subgraph(project_id, limit=1000)

            G = nx.DiGraph()
            for node in graph_data.get("nodes", []):
                G.add_node(node["id"], **node.get("properties", {}))
            for edge in graph_data.get("edges", []):
                G.add_edge(edge["source"], edge["target"])

            pagerank = nx.pagerank(G)
            sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_k]

            scores = []
            for node_id, score in sorted_nodes:
                node_data = G.nodes.get(node_id, {})
                scores.append(CentralityScore(
                    entity_id=node_id,
                    entity_name=node_data.get("name", node_id),
                    entity_type=node_data.get("type", "UNKNOWN"),
                    pagerank=score,
                    overall_score=score
                ))

            return scores
        except ImportError:
            return []
