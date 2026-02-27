"""Neo4j GDS图算法封装

提供PageRank、Betweenness、Louvain等图算法的便捷接口
"""

from __future__ import annotations

import logging
from typing import Any, Type

from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j import cypher_queries as queries

logger = logging.getLogger(__name__)


class GraphAlgorithmError(Exception):
    """图算法执行错误"""
    pass


class GraphProjectionError(GraphAlgorithmError):
    """图投影创建/管理错误"""
    pass


class GraphAlgorithmRunner:
    """Neo4j GDS图算法运行器
    
    封装了常用的图分析算法，包括：
    - 中心性分析：PageRank, Betweenness
    - 社区发现：Louvain
    - 路径查找：最短路径、所有路径
    """
    
    def __init__(self, client: Type[Neo4jClient] = Neo4jClient):
        self._client = client
    
    def _get_graph_name(self, project_id: str) -> str:
        """生成图投影名称"""
        return f"graph_{project_id.replace('-', '_')}"
    
    async def _ensure_graph_projection(
        self,
        project_id: str,
        weight_property: str | None = None
    ) -> str:
        """确保图投影存在，如果不存在则创建
        
        Args:
            project_id: 项目ID
            weight_property: 关系权重属性名
            
        Returns:
            图投影名称
        """
        graph_name = self._get_graph_name(project_id)
        
        # 检查投影是否存在
        exists_result = await self._client.execute_read(
            queries.CHECK_GRAPH_EXISTS,
            {"graph_name": graph_name}
        )
        
        exists = exists_result[0].get("exists", False) if exists_result else False
        
        if not exists:
            # 创建新投影
            try:
                weight_prop = weight_property if weight_property else None
                await self._client.execute_write(
                    queries.CREATE_GRAPH_PROJECTION,
                    {
                        "graph_name": graph_name,
                        "weight_property": weight_prop
                    }
                )
                logger.info(f"Created graph projection: {graph_name}")
            except Exception as e:
                error_msg = str(e)
                # 检查是否是GDS未安装的错误
                if "gds" in error_msg.lower() or "procedure" in error_msg.lower():
                    raise GraphProjectionError(
                        f"GDS plugin not installed or not available. "
                        f"Please install Neo4j Graph Data Science library. Error: {e}"
                    )
                raise GraphProjectionError(f"Failed to create graph projection: {e}")
        
        return graph_name
    
    async def drop_graph_projection(self, project_id: str) -> bool:
        """删除图投影
        
        Args:
            project_id: 项目ID
            
        Returns:
            是否成功删除
        """
        graph_name = self._get_graph_name(project_id)
        
        try:
            await self._client.execute_write(
                queries.DROP_GRAPH_PROJECTION,
                {"graph_name": graph_name}
            )
            logger.info(f"Dropped graph projection: {graph_name}")
            return True
        except Exception as e:
            if "not found" in str(e).lower():
                return False
            logger.warning(f"Failed to drop graph projection {graph_name}: {e}")
            return False
    
    async def run_pagerank(
        self,
        project_id: str,
        limit: int = 100,
        max_iterations: int = 20,
        damping_factor: float = 0.85,
        weight_property: str | None = None
    ) -> list[dict[str, Any]]:
        """运行PageRank中心性算法
        
        PageRank是一种链接分析算法，用于衡量图中节点的重要性。
        常用于识别关键实体（如关键企业、关键人物等）。
        
        Args:
            project_id: 项目ID
            limit: 返回结果数量限制
            max_iterations: 最大迭代次数
            damping_factor: 阻尼系数（通常为0.85）
            weight_property: 关系权重属性名
            
        Returns:
            节点PageRank分数列表，按分数降序排列
            
        Example:
            >>> runner = GraphAlgorithmRunner()
            >>> results = await runner.run_pagerank("proj-123", limit=10)
            >>> # [{"entity_id": "...", "name": "公司A", "entity_type": "ENTERPRISE", "score": 0.0523}, ...]
        """
        try:
            graph_name = await self._ensure_graph_projection(project_id, weight_property)
            
            result = await self._client.execute_read(
                queries.PAGERANK,
                {
                    "graph_name": graph_name,
                    "limit": limit,
                    "max_iterations": max_iterations,
                    "damping_factor": damping_factor,
                    "weight_property": weight_property
                }
            )
            return result
        except GraphProjectionError:
            # GDS不可用，使用简单的degree centrality作为替代
            logger.warning("GDS not available, falling back to degree centrality")
            return await self._client.execute_read(
                queries.DEGREE_CENTRALITY,
                {"project_id": project_id, "limit": limit}
            )
        except Exception as e:
            raise GraphAlgorithmError(f"PageRank calculation failed: {e}")
    
    async def run_betweenness(
        self,
        project_id: str,
        limit: int = 100,
        sampling_size: int = 10000,
        sampling_seed: int | None = None
    ) -> list[dict[str, Any]]:
        """运行Betweenness中心性算法
        
        Betweenness中心性衡量一个节点作为图中其他节点之间桥梁的程度。
        高betweenness的节点通常是信息流动的关键中介。
        
        Args:
            project_id: 项目ID
            limit: 返回结果数量限制
            sampling_size: 采样大小（用于近似计算，提高效率）
            sampling_seed: 采样随机种子（用于结果可复现）
            
        Returns:
            节点Betweenness分数列表，按分数降序排列
        """
        try:
            graph_name = await self._ensure_graph_projection(project_id)
            
            params = {
                "graph_name": graph_name,
                "limit": limit,
                "sampling_size": sampling_size,
                "sampling_seed": sampling_seed
            }
            
            result = await self._client.execute_read(queries.BETWEENNESS, params)
            return result
        except GraphProjectionError:
            logger.warning("GDS not available, betweenness calculation skipped")
            return []
        except Exception as e:
            raise GraphAlgorithmError(f"Betweenness calculation failed: {e}")
    
    async def run_louvain(
        self,
        project_id: str,
        max_levels: int = 10,
        max_iterations: int = 100,
        tolerance: float = 0.0001,
        weight_property: str | None = None
    ) -> list[dict[str, Any]]:
        """运行Louvain社区发现算法
        
        Louvain算法是一种基于模块度的社区发现算法，
        能够识别图中紧密连接的节点群组（社区）。
        
        Args:
            project_id: 项目ID
            max_levels: 最大层级数
            max_iterations: 每层最大迭代次数
            tolerance: 收敛容忍度
            weight_property: 关系权重属性名
            
        Returns:
            节点社区归属列表
        """
        try:
            graph_name = await self._ensure_graph_projection(project_id, weight_property)
            
            result = await self._client.execute_read(
                queries.LOUVAIN_COMMUNITY,
                {
                    "graph_name": graph_name,
                    "max_levels": max_levels,
                    "max_iterations": max_iterations,
                    "tolerance": tolerance,
                    "weight_property": weight_property
                }
            )
            return result
        except GraphProjectionError:
            logger.warning("GDS not available, Louvain community detection skipped")
            return []
        except Exception as e:
            raise GraphAlgorithmError(f"Louvain community detection failed: {e}")
    
    async def find_shortest_paths(
        self,
        project_id: str,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> dict[str, list[Any]]:
        """查找两个实体之间的最短路径
        
        使用Neo4j内置的shortestPath算法，找到连接两个实体的最短关系链。
        
        Args:
            project_id: 项目ID
            start_id: 起始实体ID
            end_id: 目标实体ID
            max_depth: 最大搜索深度
            
        Returns:
            包含nodes和relations的字典
            
        Example:
            >>> result = await runner.find_shortest_paths("proj-123", "ent-1", "ent-10")
            >>> # {"nodes": [{...}, {...}], "relations": [{...}, {...}]}
        """
        query = queries.FIND_SHORTEST_PATH.format(max_depth=max_depth)
        
        result = await self._client.execute_read(
            query,
            {
                "project_id": project_id,
                "start_id": start_id,
                "end_id": end_id
            }
        )
        
        if not result:
            return {"nodes": [], "relations": []}
        
        record = result[0]
        return {
            "nodes": record.get("nodes", []),
            "relations": record.get("relations", [])
        }
    
    async def find_all_paths(
        self,
        project_id: str,
        start_id: str,
        end_id: str,
        max_depth: int = 3,
        path_limit: int = 100
    ) -> dict[str, list[Any]]:
        """查找两个实体之间的所有路径
        
        找到连接两个实体的所有可能路径，适用于小范围子图分析。
        
        Args:
            project_id: 项目ID
            start_id: 起始实体ID
            end_id: 目标实体ID
            max_depth: 最大搜索深度（建议3以内，避免计算爆炸）
            path_limit: 返回路径数量限制
            
        Returns:
            包含nodes和relations的字典
        """
        query = queries.FIND_ALL_PATHS.format(max_depth=max_depth)
        
        result = await self._client.execute_read(
            query,
            {
                "project_id": project_id,
                "start_id": start_id,
                "end_id": end_id,
                "path_limit": path_limit
            }
        )
        
        if not result:
            return {"nodes": [], "relations": []}
        
        # 合并所有路径的节点和关系
        all_nodes = []
        all_relations = []
        seen_node_ids = set()
        seen_rel_ids = set()
        
        for record in result:
            for node in record.get("nodes", []):
                node_id = node.get("id")
                if node_id and node_id not in seen_node_ids:
                    seen_node_ids.add(node_id)
                    all_nodes.append(node)
            
            for rel in record.get("relations", []):
                rel_id = rel.get("id")
                if rel_id and rel_id not in seen_rel_ids:
                    seen_rel_ids.add(rel_id)
                    all_relations.append(rel)
        
        return {
            "nodes": all_nodes,
            "relations": all_relations
        }
    
    async def get_graph_statistics(self, project_id: str) -> dict[str, Any]:
        """获取图谱统计信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            包含实体数量、关系数量、实体类型分布等的字典
        """
        # 获取基本统计
        stats_result = await self._client.execute_read(
            queries.GET_PROJECT_STATS,
            {"project_id": project_id}
        )
        
        # 获取实体类型分布
        type_dist = await self._client.execute_read(
            queries.GET_ENTITY_TYPE_DISTRIBUTION,
            {"project_id": project_id}
        )
        
        # 获取关系类型分布
        rel_dist = await self._client.execute_read(
            queries.GET_RELATION_TYPE_DISTRIBUTION,
            {"project_id": project_id}
        )
        
        stats = stats_result[0] if stats_result else {}
        
        return {
            "entity_count": stats.get("entity_count", 0),
            "relation_count": stats.get("relation_count", 0),
            "entity_types": stats.get("entity_types", []),
            "entity_type_distribution": type_dist,
            "relation_type_distribution": rel_dist
        }
