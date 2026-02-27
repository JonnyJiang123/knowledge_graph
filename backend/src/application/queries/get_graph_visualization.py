"""可视化数据获取查询

返回适配ECharts的 nodes + edges 格式数据
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Type

from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j import cypher_queries as queries


@dataclass(slots=True)
class GetGraphVisualizationQuery:
    """可视化数据查询参数
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID（用于权限验证）
        node_limit: 节点数量限制
        entity_type: 实体类型过滤（可选）
        center_entity_id: 中心实体ID（获取 ego network）
        depth: 当指定中心实体时的邻居深度
    """
    project_id: str
    owner_id: str
    node_limit: int = 500
    entity_type: str | None = None
    center_entity_id: str | None = None
    depth: int = 2


@dataclass(slots=True)
class VisualizationNode:
    """可视化节点 (ECharts格式)
    
    Attributes:
        id: 节点唯一标识
        name: 显示名称
        category: 节点分类索引（用于ECharts颜色区分）
        symbolSize: 节点大小
        value: 附加数据
    """
    id: str
    name: str
    category: int
    symbolSize: int
    value: dict[str, Any]


@dataclass(slots=True)
class VisualizationEdge:
    """可视化边 (ECharts格式)
    
    Attributes:
        source: 源节点ID
        target: 目标节点ID
        relation: 关系类型名称
        value: 附加数据
    """
    source: str
    target: str
    relation: str
    value: dict[str, Any]


@dataclass(slots=True)
class GraphVisualizationResult:
    """图可视化结果
    
    Attributes:
        nodes: 节点列表
        edges: 边列表
        categories: 分类名称列表（对应节点的category索引）
    """
    nodes: list[VisualizationNode]
    edges: list[VisualizationEdge]
    categories: list[str]


class GetGraphVisualizationHandler:
    """图可视化数据处理器"""
    
    # 实体类型到分类索引的映射
    ENTITY_TYPE_CATEGORIES = [
        "ENTERPRISE",      # 企业
        "PERSON",          # 人物
        "ACCOUNT",         # 账户
        "TRANSACTION",     # 交易
        "SUPPLIER",        # 供应商
        "DRUG",            # 药品
        "OTHER"            # 其他
    ]
    
    # 分类颜色配置 (供前端参考)
    CATEGORY_COLORS = {
        "ENTERPRISE": "#5470c6",
        "PERSON": "#91cc75",
        "ACCOUNT": "#fac858",
        "TRANSACTION": "#ee6666",
        "SUPPLIER": "#73c0de",
        "DRUG": "#3ba272",
        "OTHER": "#9a60b4"
    }
    
    def __init__(self, client: Type[Neo4jClient] = Neo4jClient):
        self._client = client
    
    async def handle(self, query: GetGraphVisualizationQuery) -> GraphVisualizationResult:
        """获取可视化数据
        
        Args:
            query: 可视化查询参数
            
        Returns:
            图可视化数据
        """
        # 根据参数选择查询策略
        if query.center_entity_id:
            # 获取以某节点为中心的 ego network
            result = await self._get_ego_network(query)
        else:
            # 获取项目子图
            result = await self._get_subgraph(query)
        
        return result
    
    async def _get_subgraph(
        self,
        query: GetGraphVisualizationQuery
    ) -> GraphVisualizationResult:
        """获取项目子图"""
        # 使用社区子图查询
        cypher_result = await self._client.execute_read(
            queries.GET_COMMUNITY_SUBGRAPH,
            {
                "project_id": query.project_id,
                "entity_type": query.entity_type,
                "label": None,
                "node_limit": query.node_limit
            }
        )
        
        if not cypher_result:
            return GraphVisualizationResult(nodes=[], edges=[], categories=[])
        
        record = cypher_result[0]
        nodes = record.get("nodes", [])
        relations = record.get("relations", [])
        
        return self._convert_to_visualization_format(nodes, relations)
    
    async def _get_ego_network(
        self,
        query: GetGraphVisualizationQuery
    ) -> GraphVisualizationResult:
        """获取以某节点为中心的 ego network"""
        query_str = queries.GET_EGO_NETWORK.format(
            depth=query.depth,
            limit=query.node_limit - 1  # 减去中心节点
        )
        
        cypher_result = await self._client.execute_read(
            query_str,
            {
                "entity_id": query.center_entity_id,
                "project_id": query.project_id
            }
        )
        
        if not cypher_result:
            return GraphVisualizationResult(nodes=[], edges=[], categories=[])
        
        record = cypher_result[0]
        nodes = record.get("nodes", [])
        relations = record.get("relations", [])
        
        return self._convert_to_visualization_format(nodes, relations)
    
    def _convert_to_visualization_format(
        self,
        nodes: list[Any],
        relations: list[Any]
    ) -> GraphVisualizationResult:
        """将Neo4j结果转换为ECharts可视化格式"""
        # 收集所有实体类型
        entity_types = set()
        node_map = {}  # 用于快速查找
        
        # 处理节点
        vis_nodes = []
        for node in nodes:
            if not node:
                continue
            
            node_data = self._parse_node(node)
            entity_type = node_data.get("type", "OTHER")
            entity_types.add(entity_type)
            
            category = self._get_category_index(entity_type)
            
            # 计算节点大小（基于连接数）
            symbol_size = self._calculate_node_size(node_data)
            
            vis_node = VisualizationNode(
                id=node_data.get("id", ""),
                name=node_data.get("external_id", node_data.get("id", "Unknown")),
                category=category,
                symbolSize=symbol_size,
                value={
                    "type": entity_type,
                    "labels": node_data.get("labels", []),
                    "properties": node_data.get("properties", {}),
                    "version": node_data.get("version", 1)
                }
            )
            vis_nodes.append(vis_node)
            node_map[vis_node.id] = vis_node
        
        # 处理边
        vis_edges = []
        for rel in relations:
            if not rel:
                continue
            
            rel_data = self._parse_relation(rel)
            source_id = rel_data.get("source_id", "")
            target_id = rel_data.get("target_id", "")
            
            # 只添加两个端点都在节点列表中的边
            if source_id in node_map and target_id in node_map:
                vis_edge = VisualizationEdge(
                    source=source_id,
                    target=target_id,
                    relation=rel_data.get("type", "RELATION"),
                    value={
                        "id": rel_data.get("id", ""),
                        "properties": rel_data.get("properties", {})
                    }
                )
                vis_edges.append(vis_edge)
        
        # 构建分类列表
        categories = sorted(entity_types) if entity_types else ["OTHER"]
        # 确保OTHER在最后
        if "OTHER" in categories:
            categories.remove("OTHER")
            categories.append("OTHER")
        
        return GraphVisualizationResult(
            nodes=vis_nodes,
            edges=vis_edges,
            categories=categories
        )
    
    def _parse_node(self, node: Any) -> dict[str, Any]:
        """解析节点数据"""
        if isinstance(node, dict):
            data = dict(node)
        else:
            data = dict(node)
        
        # 解析properties_json
        props_json = data.get("properties_json")
        if props_json:
            data["properties"] = json.loads(props_json)
        else:
            data["properties"] = {}
        return data
    
    def _parse_relation(self, rel: Any) -> dict[str, Any]:
        """解析关系数据"""
        if isinstance(rel, dict):
            data = dict(rel)
        else:
            data = dict(rel)
            data["type"] = rel.type if hasattr(rel, 'type') else data.get("type")
        
        # 解析properties_json
        props_json = data.get("properties_json")
        if props_json:
            data["properties"] = json.loads(props_json)
        else:
            data["properties"] = {}
        return data
    
    def _get_category_index(self, entity_type: str) -> int:
        """获取实体类型对应的分类索引"""
        try:
            return self.ENTITY_TYPE_CATEGORIES.index(entity_type)
        except ValueError:
            return len(self.ENTITY_TYPE_CATEGORIES) - 1  # OTHER
    
    def _calculate_node_size(self, node_data: dict[str, Any]) -> int:
        """计算节点大小
        
        基础大小 + 根据属性动态调整
        """
        base_size = 40
        entity_type = node_data.get("type", "")
        
        # 不同类型不同基础大小
        type_size_map = {
            "ENTERPRISE": 50,
            "PERSON": 45,
            "ACCOUNT": 35,
            "TRANSACTION": 30,
            "SUPPLIER": 40,
            "DRUG": 40,
        }
        
        size = type_size_map.get(entity_type, base_size)
        
        # 根据某些属性调整大小（如注册资本）
        props = node_data.get("properties", {})
        if "registered_capital" in props:
            try:
                capital = float(props["registered_capital"])
                if capital > 10000:  # 大额资本
                    size += 10
            except (ValueError, TypeError):
                pass
        
        return min(size, 80)  # 最大80
