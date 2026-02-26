"""路径查找查询

支持最短路径查找和所有路径查找
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Type

from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j import cypher_queries as queries


@dataclass(slots=True)
class FindShortestPathQuery:
    """最短路径查找查询参数
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID（用于权限验证）
        start_id: 起始实体ID
        end_id: 目标实体ID
        max_depth: 最大搜索深度
    """
    project_id: str
    owner_id: str
    start_id: str
    end_id: str
    max_depth: int = 5


@dataclass(slots=True)
class FindAllPathsQuery:
    """所有路径查找查询参数
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID（用于权限验证）
        start_id: 起始实体ID
        end_id: 目标实体ID
        max_depth: 最大搜索深度（建议3以内）
        path_limit: 返回路径数量限制
    """
    project_id: str
    owner_id: str
    start_id: str
    end_id: str
    max_depth: int = 3
    path_limit: int = 100


@dataclass(slots=True)
class PathResult:
    """路径查找结果
    
    Attributes:
        nodes: 路径中的节点列表
        relations: 路径中的关系列表
        path_count: 路径数量（所有路径查找时有效）
        found: 是否找到路径
    """
    nodes: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    path_count: int = 1
    found: bool = True


class FindShortestPathHandler:
    """最短路径查找处理器"""
    
    def __init__(self, client: Type[Neo4jClient] = Neo4jClient):
        self._client = client
    
    async def handle(self, query: FindShortestPathQuery) -> PathResult:
        """查找最短路径
        
        Args:
            query: 路径查找参数
            
        Returns:
            路径结果
        """
        query_str = queries.FIND_SHORTEST_PATH.format(max_depth=query.max_depth)
        
        result = await self._client.execute_read(
            query_str,
            {
                "project_id": query.project_id,
                "start_id": query.start_id,
                "end_id": query.end_id
            }
        )
        
        if not result:
            return PathResult(nodes=[], relations=[], found=False)
        
        record = result[0]
        nodes = self._parse_nodes(record.get("nodes", []))
        relations = self._parse_relations(record.get("relations", []))
        
        return PathResult(
            nodes=nodes,
            relations=relations,
            path_count=1,
            found=len(nodes) > 0
        )
    
    def _parse_nodes(self, nodes: list[Any]) -> list[dict[str, Any]]:
        """解析节点数据"""
        parsed = []
        for node in nodes:
            if isinstance(node, dict):
                data = dict(node)
            else:
                # Neo4j Node对象
                data = dict(node)
            
            # 解析properties_json
            props_json = data.get("properties_json")
            if props_json:
                data["properties"] = json.loads(props_json)
            else:
                data["properties"] = {}
            parsed.append(data)
        return parsed
    
    def _parse_relations(self, relations: list[Any]) -> list[dict[str, Any]]:
        """解析关系数据"""
        parsed = []
        for rel in relations:
            if isinstance(rel, dict):
                data = dict(rel)
            else:
                # Neo4j Relationship对象
                data = dict(rel)
                data["type"] = rel.type if hasattr(rel, 'type') else data.get("type")
            
            # 解析properties_json
            props_json = data.get("properties_json")
            if props_json:
                data["properties"] = json.loads(props_json)
            else:
                data["properties"] = {}
            parsed.append(data)
        return parsed


class FindAllPathsHandler:
    """所有路径查找处理器"""
    
    def __init__(self, client: Type[Neo4jClient] = Neo4jClient):
        self._client = client
    
    async def handle(self, query: FindAllPathsQuery) -> PathResult:
        """查找所有路径
        
        Args:
            query: 路径查找参数
            
        Returns:
            路径结果
        """
        query_str = queries.FIND_ALL_PATHS.format(max_depth=query.max_depth)
        
        result = await self._client.execute_read(
            query_str,
            {
                "project_id": query.project_id,
                "start_id": query.start_id,
                "end_id": query.end_id,
                "path_limit": query.path_limit
            }
        )
        
        if not result:
            return PathResult(nodes=[], relations=[], found=False)
        
        # 合并所有路径的节点和关系
        all_nodes = {}
        all_relations = {}
        path_count = len(result)
        
        for record in result:
            nodes = record.get("nodes", [])
            relations = record.get("relations", [])
            
            for node in nodes:
                node_id = node.get("id") if isinstance(node, dict) else node.get("id")
                if node_id and node_id not in all_nodes:
                    all_nodes[node_id] = self._parse_node(node)
            
            for rel in relations:
                rel_id = rel.get("id") if isinstance(rel, dict) else rel.get("id")
                if rel_id and rel_id not in all_relations:
                    all_relations[rel_id] = self._parse_relation(rel)
        
        return PathResult(
            nodes=list(all_nodes.values()),
            relations=list(all_relations.values()),
            path_count=path_count,
            found=len(all_nodes) > 0
        )
    
    def _parse_node(self, node: Any) -> dict[str, Any]:
        """解析单个节点"""
        if isinstance(node, dict):
            data = dict(node)
        else:
            data = dict(node)
        
        props_json = data.get("properties_json")
        if props_json:
            import json
            data["properties"] = json.loads(props_json)
        else:
            data["properties"] = {}
        return data
    
    def _parse_relation(self, rel: Any) -> dict[str, Any]:
        """解析单个关系"""
        if isinstance(rel, dict):
            data = dict(rel)
        else:
            data = dict(rel)
            data["type"] = rel.type if hasattr(rel, 'type') else data.get("type")
        
        props_json = data.get("properties_json")
        if props_json:
            import json
            data["properties"] = json.loads(props_json)
        else:
            data["properties"] = {}
        return data
