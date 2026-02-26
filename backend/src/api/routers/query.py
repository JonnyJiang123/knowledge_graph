"""查询路由

提供高级查询功能：条件搜索、路径查找
"""

from __future__ import annotations

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.dependencies.auth import get_current_user
from src.api.schemas.visualization import PathVisualizationResponse, PathNode, PathEdge
from src.application.queries.find_paths import (
    FindShortestPathQuery,
    FindAllPathsQuery,
    FindShortestPathHandler,
    FindAllPathsHandler
)
from src.application.queries.search_entities import (
    SearchEntitiesQuery,
    SearchEntitiesHandler
)
from src.domain.entities.user import User

router = APIRouter(prefix="/api/query", tags=["query"])


class SearchRequest(BaseModel):
    """搜索请求"""
    project_id: str = Field(..., description="项目ID")
    keyword: str | None = Field(default=None, description="搜索关键词")
    entity_type: str | None = Field(default=None, description="实体类型过滤")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class SearchResponse(BaseModel):
    """搜索响应"""
    entities: List[dict[str, Any]]
    total: int
    offset: int
    limit: int
    has_more: bool


class PathSearchRequest(BaseModel):
    """路径搜索请求"""
    project_id: str = Field(..., description="项目ID")
    start_id: str = Field(..., description="起始实体ID")
    end_id: str = Field(..., description="目标实体ID")
    max_depth: int = Field(default=5, ge=1, le=10, description="最大深度")
    algorithm: str = Field(default="shortest", description="算法: shortest | all")
    path_limit: int = Field(default=100, ge=1, le=500, description="路径数量限制（仅all算法）")


@router.post("/search", response_model=SearchResponse)
async def advanced_search(
    payload: SearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> SearchResponse:
    """高级搜索
    
    支持关键词和类型过滤的条件搜索
    """
    handler = SearchEntitiesHandler()
    query = SearchEntitiesQuery(
        project_id=payload.project_id,
        owner_id=current_user.id,
        keyword=payload.keyword,
        entity_type=payload.entity_type,
        offset=payload.offset,
        limit=payload.limit
    )
    
    result = await handler.handle(query)
    
    return SearchResponse(
        entities=result.entities,
        total=result.total,
        offset=result.offset,
        limit=result.limit,
        has_more=result.has_more
    )


@router.post("/paths", response_model=PathVisualizationResponse)
async def find_paths(
    payload: PathSearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> PathVisualizationResponse:
    """路径查找
    
    查找两个实体之间的路径
    
    - shortest: 最短路径算法，返回一条最短路径
    - all: 所有路径算法，返回所有可能的路径（最多path_limit条）
    """
    if payload.algorithm == "shortest":
        handler = FindShortestPathHandler()
        query = FindShortestPathQuery(
            project_id=payload.project_id,
            owner_id=current_user.id,
            start_id=payload.start_id,
            end_id=payload.end_id,
            max_depth=payload.max_depth
        )
        result = await handler.handle(query)
    
    elif payload.algorithm == "all":
        handler = FindAllPathsHandler()
        query = FindAllPathsQuery(
            project_id=payload.project_id,
            owner_id=current_user.id,
            start_id=payload.start_id,
            end_id=payload.end_id,
            max_depth=min(payload.max_depth, 3),  # 限制深度避免性能问题
            path_limit=payload.path_limit
        )
        result = await handler.handle(query)
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported algorithm: {payload.algorithm}. Use 'shortest' or 'all'"
        )
    
    # 转换为响应格式
    nodes = []
    for node_data in result.nodes:
        nodes.append(PathNode(
            id=node_data.get("id", ""),
            name=node_data.get("external_id", node_data.get("id", "")),
            type=node_data.get("type", "UNKNOWN"),
            properties=node_data.get("properties", {})
        ))
    
    edges = []
    for edge_data in result.relations:
        edges.append(PathEdge(
            id=edge_data.get("id", ""),
            source=edge_data.get("source_id", ""),
            target=edge_data.get("target_id", ""),
            type=edge_data.get("type", "RELATION"),
            properties=edge_data.get("properties", {})
        ))
    
    return PathVisualizationResponse(
        nodes=nodes,
        edges=edges,
        path_count=result.path_count,
        found=result.found
    )


@router.get("/neighbors")
async def get_neighbors(
    project_id: Annotated[str, Query(..., description="项目ID")],
    entity_id: Annotated[str, Query(..., description="实体ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    depth: int = Query(1, ge=1, le=3, description="邻居深度"),
    limit: int = Query(50, ge=1, le=200, description="最大返回数量"),
) -> dict[str, Any]:
    """获取邻居节点
    
    获取指定实体的N度邻居
    """
    from src.infrastructure.persistence.neo4j import cypher_queries as queries
    from src.infrastructure.persistence.neo4j.client import Neo4jClient
    
    query = queries.FIND_N_DEGREE_NEIGHBORS.format(depth=depth)
    
    result = await Neo4jClient.execute_read(
        query,
        {
            "project_id": project_id,
            "start_id": entity_id,
            "offset": 0,
            "limit": limit
        }
    )
    
    neighbors = []
    import json
    for record in result:
        entity_data = dict(record.get("entity", {}))
        entity_data["distance"] = record.get("distance", 0)
        
        # 解析properties_json
        props_json = entity_data.get("properties_json")
        if props_json:
            entity_data["properties"] = json.loads(props_json)
        else:
            entity_data["properties"] = {}
        
        neighbors.append(entity_data)
    
    return {
        "entity_id": entity_id,
        "depth": depth,
        "neighbors": neighbors,
        "total": len(neighbors)
    }
