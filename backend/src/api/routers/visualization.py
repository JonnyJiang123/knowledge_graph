"""可视化路由

提供图可视化数据、中心性分析等功能
"""

from __future__ import annotations

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import get_current_user
from src.api.schemas.visualization import (
    GraphVisualizationResponse,
    GraphData,
    Node,
    Edge,
    CentralityAnalysisResponse,
    CentralityScoreItem,
    CommunityAnalysisResponse,
    CommunityItem,
    CommunityMemberItem,
    GraphStatisticsResponse,
    VisualizationRequest
)
from src.application.queries.get_graph_visualization import (
    GetGraphVisualizationQuery,
    GetGraphVisualizationHandler
)
from src.application.queries.analyze_centrality import (
    AnalyzeCentralityQuery,
    AnalyzeCommunitiesQuery,
    AnalyzeCentralityHandler,
    AnalyzeCommunitiesHandler
)
from src.domain.entities.user import User
from src.infrastructure.persistence.neo4j.graph_algorithms import GraphAlgorithmRunner

router = APIRouter(prefix="/api/visualization", tags=["visualization"])


@router.get("/graph", response_model=GraphVisualizationResponse)
async def get_graph_data(
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    node_limit: int = Query(500, ge=10, le=2000, description="最大节点数"),
    entity_type: str | None = Query(None, description="按实体类型过滤"),
    center_entity_id: str | None = Query(None, description="中心实体ID（ego network）"),
    depth: int = Query(2, ge=1, le=5, description="邻居深度"),
) -> GraphVisualizationResponse:
    """获取图可视化数据
    
    返回适配ECharts的图数据（nodes + edges）
    
    - 不指定center_entity_id时，返回项目子图
    - 指定center_entity_id时，返回以该节点为中心的ego network
    """
    handler = GetGraphVisualizationHandler()
    query = GetGraphVisualizationQuery(
        project_id=project_id,
        owner_id=current_user.id,
        node_limit=node_limit,
        entity_type=entity_type,
        center_entity_id=center_entity_id,
        depth=depth
    )
    
    result = await handler.handle(query)
    
    # 转换为响应格式
    nodes = [
        Node(
            id=n.id,
            name=n.name,
            category=n.category,
            symbolSize=n.symbolSize,
            value=n.value
        )
        for n in result.nodes
    ]
    
    edges = [
        Edge(
            source=e.source,
            target=e.target,
            relation=e.relation,
            value=e.value
        )
        for e in result.edges
    ]
    
    return GraphVisualizationResponse(
        data=GraphData(
            nodes=nodes,
            edges=edges,
            categories=result.categories
        ),
        total_nodes=len(nodes),
        total_edges=len(edges)
    )


@router.post("/graph", response_model=GraphVisualizationResponse)
async def get_graph_data_post(
    payload: VisualizationRequest,
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GraphVisualizationResponse:
    """获取图可视化数据 (POST方法)
    
    支持通过请求体传递更多参数
    """
    handler = GetGraphVisualizationHandler()
    query = GetGraphVisualizationQuery(
        project_id=project_id,
        owner_id=current_user.id,
        node_limit=payload.node_limit,
        entity_type=payload.entity_type,
        center_entity_id=payload.center_entity_id,
        depth=payload.depth
    )
    
    result = await handler.handle(query)
    
    nodes = [
        Node(
            id=n.id,
            name=n.name,
            category=n.category,
            symbolSize=n.symbolSize,
            value=n.value
        )
        for n in result.nodes
    ]
    
    edges = [
        Edge(
            source=e.source,
            target=e.target,
            relation=e.relation,
            value=e.value
        )
        for e in result.edges
    ]
    
    return GraphVisualizationResponse(
        data=GraphData(
            nodes=nodes,
            edges=edges,
            categories=result.categories
        ),
        total_nodes=len(nodes),
        total_edges=len(edges)
    )


@router.get("/centrality", response_model=CentralityAnalysisResponse)
async def analyze_centrality(
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    algorithm: str = Query("pagerank", description="算法: pagerank | betweenness | degree"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
) -> CentralityAnalysisResponse:
    """中心性分析
    
    计算图中节点的中心性分数
    
    - pagerank: PageRank算法，识别重要节点
    - betweenness: Betweenness算法，识别桥梁节点
    - degree: 度中心性，识别连接数多的节点
    """
    if algorithm not in ["pagerank", "betweenness", "degree"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported algorithm: {algorithm}"
        )
    
    handler = AnalyzeCentralityHandler()
    query = AnalyzeCentralityQuery(
        project_id=project_id,
        owner_id=current_user.id,
        algorithm=algorithm,
        limit=limit
    )
    
    result = await handler.handle(query)
    
    scores = [
        CentralityScoreItem(
            entity_id=s.entity_id,
            name=s.name,
            entity_type=s.entity_type,
            score=s.score,
            rank=s.rank
        )
        for s in result.scores
    ]
    
    return CentralityAnalysisResponse(
        algorithm=result.algorithm,
        scores=scores,
        total_entities=result.total_entities,
        execution_time_ms=result.execution_time_ms
    )


@router.get("/communities", response_model=CommunityAnalysisResponse)
async def analyze_communities(
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    algorithm: str = Query("louvain", description="算法: louvain | label_propagation"),
) -> CommunityAnalysisResponse:
    """社区发现分析
    
    识别图中的社区结构（紧密连接的节点群组）
    
    - louvain: Louvain算法，基于模块度优化
    - label_propagation: 标签传播算法
    """
    if algorithm not in ["louvain", "label_propagation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported algorithm: {algorithm}"
        )
    
    handler = AnalyzeCommunitiesHandler()
    query = AnalyzeCommunitiesQuery(
        project_id=project_id,
        owner_id=current_user.id,
        algorithm=algorithm
    )
    
    result = await handler.handle(query)
    
    communities = [
        CommunityItem(
            id=c.id,
            size=c.size,
            members=[
                CommunityMemberItem(
                    entity_id=m.entity_id,
                    name=m.name,
                    entity_type=m.entity_type
                )
                for m in c.members
            ]
        )
        for c in result.communities
    ]
    
    return CommunityAnalysisResponse(
        algorithm=result.algorithm,
        communities=communities,
        total_communities=result.total_communities
    )


@router.get("/statistics", response_model=GraphStatisticsResponse)
async def get_statistics(
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GraphStatisticsResponse:
    """获取图谱统计信息
    
    返回实体数量、关系数量、类型分布等统计信息
    """
    runner = GraphAlgorithmRunner()
    stats = await runner.get_graph_statistics(project_id)
    
    return GraphStatisticsResponse(
        entity_count=stats["entity_count"],
        relation_count=stats["relation_count"],
        entity_types=stats["entity_types"],
        entity_type_distribution=stats["entity_type_distribution"],
        relation_type_distribution=stats["relation_type_distribution"]
    )
