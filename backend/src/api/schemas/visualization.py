"""可视化DTO

定义图可视化相关的请求和响应模型，适配ECharts格式
"""

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Node(BaseModel):
    """图节点 (ECharts格式)
    
    ECharts graph series data format:
    {
        id: string,
        name: string,
        category: number,
        symbolSize: number,
        value: any,
        x?: number,
        y?: number,
        fixed?: boolean
    }
    """
    id: str = Field(..., description="节点唯一标识")
    name: str = Field(..., description="节点显示名称")
    category: int = Field(default=0, description="节点分类索引，用于ECharts颜色区分")
    symbolSize: int = Field(default=40, description="节点大小")
    value: dict[str, Any] = Field(default_factory=dict, description="附加数据")
    x: Optional[float] = Field(default=None, description="X坐标（力引导布局时使用）")
    y: Optional[float] = Field(default=None, description="Y坐标（力引导布局时使用）")
    fixed: Optional[bool] = Field(default=None, description="是否固定位置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ent-123",
                "name": "ABC科技有限公司",
                "category": 0,
                "symbolSize": 50,
                "value": {
                    "type": "ENTERPRISE",
                    "properties": {"registered_capital": "1000万"}
                }
            }
        }


class Edge(BaseModel):
    """图边 (ECharts格式)
    
    ECharts graph series links format:
    {
        source: string,
        target: string,
        value?: any
    }
    """
    source: str = Field(..., description="源节点ID")
    target: str = Field(..., description="目标节点ID")
    relation: str = Field(default="RELATION", description="关系类型名称")
    value: dict[str, Any] = Field(default_factory=dict, description="附加数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "ent-123",
                "target": "ent-456",
                "relation": "OWNS",
                "value": {"id": "rel-789", "properties": {}}
            }
        }


class Category(BaseModel):
    """节点分类"""
    name: str = Field(..., description="分类名称")
    itemStyle: Optional[dict[str, Any]] = Field(default=None, description="ECharts样式配置")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ENTERPRISE",
                "itemStyle": {"color": "#5470c6"}
            }
        }


class GraphData(BaseModel):
    """图数据
    
    完整的ECharts graph series数据格式
    """
    nodes: List[Node] = Field(default_factory=list, description="节点列表")
    edges: List[Edge] = Field(default_factory=list, description="边列表")
    categories: List[str] = Field(default_factory=list, description="分类名称列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"id": "ent-1", "name": "公司A", "category": 0, "symbolSize": 50, "value": {}}
                ],
                "edges": [
                    {"source": "ent-1", "target": "ent-2", "relation": "OWNS", "value": {}}
                ],
                "categories": ["ENTERPRISE", "PERSON"]
            }
        }


class VisualizationRequest(BaseModel):
    """可视化请求"""
    node_limit: int = Field(default=500, ge=10, le=2000, description="最大节点数")
    entity_type: Optional[str] = Field(default=None, description="按实体类型过滤")
    center_entity_id: Optional[str] = Field(default=None, description="中心实体ID（ego network）")
    depth: int = Field(default=2, ge=1, le=5, description="邻居深度")


class GraphVisualizationResponse(BaseModel):
    """图可视化响应"""
    data: GraphData
    total_nodes: int = Field(description="节点总数")
    total_edges: int = Field(description="边总数")


class CentralityScoreItem(BaseModel):
    """中心性分数项"""
    entity_id: str
    name: str
    entity_type: str
    score: float
    rank: int


class CentralityAnalysisResponse(BaseModel):
    """中心性分析响应"""
    algorithm: str
    scores: List[CentralityScoreItem]
    total_entities: int
    execution_time_ms: Optional[float] = None


class CommunityMemberItem(BaseModel):
    """社区成员项"""
    entity_id: str
    name: str
    entity_type: str


class CommunityItem(BaseModel):
    """社区项"""
    id: int
    size: int
    members: List[CommunityMemberItem]


class CommunityAnalysisResponse(BaseModel):
    """社区分析响应"""
    algorithm: str
    communities: List[CommunityItem]
    total_communities: int


class PathNode(BaseModel):
    """路径节点"""
    id: str
    name: str
    type: str
    properties: dict[str, Any]


class PathEdge(BaseModel):
    """路径边"""
    id: str
    source: str
    target: str
    type: str
    properties: dict[str, Any]


class PathVisualizationResponse(BaseModel):
    """路径可视化响应"""
    nodes: List[PathNode]
    edges: List[PathEdge]
    path_count: int
    found: bool


class GraphStatisticsResponse(BaseModel):
    """图谱统计响应"""
    entity_count: int
    relation_count: int
    entity_types: List[str]
    entity_type_distribution: List[dict[str, Any]]
    relation_type_distribution: List[dict[str, Any]]
