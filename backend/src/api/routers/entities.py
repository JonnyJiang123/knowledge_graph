"""实体路由

提供实体的CRUD操作
"""

from __future__ import annotations

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import get_current_user
from src.api.schemas.graph import GraphEntityCreate, GraphEntityResponse
from src.application.commands.create_entity import CreateEntityCommand
from src.application.queries.search_entities import (
    SearchEntitiesQuery,
    SearchEntitiesHandler
)
from src.application.services.graph_service import GraphService
from src.domain.entities.user import User
from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j import cypher_queries as queries

router = APIRouter(prefix="/api/entities", tags=["entities"])


class EntityUpdateRequest(GraphEntityCreate):
    """实体更新请求"""
    pass


class BatchEntityOperation(BaseModel):
    """批量实体操作请求"""
    operation: str  # create, update, delete
    entities: List[dict[str, Any]]


class BatchOperationResponse(BaseModel):
    """批量操作响应"""
    success: bool
    processed_count: int
    failed_count: int
    errors: List[str]


from pydantic import BaseModel


@router.get("", response_model=dict[str, Any])
async def search_entities(
    project_id: Annotated[str, Query(..., description="项目ID")],
    keyword: Annotated[str | None, Query(default=None, description="搜索关键词")],
    entity_type: Annotated[str | None, Query(default=None, description="实体类型")],
    current_user: Annotated[User, Depends(get_current_user)],
    offset: int = Query(0, ge=0, description="分页偏移量"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
) -> dict[str, Any]:
    """搜索实体
    
    支持关键词搜索和类型过滤，返回分页结果
    """
    handler = SearchEntitiesHandler()
    query = SearchEntitiesQuery(
        project_id=project_id,
        owner_id=current_user.id,
        keyword=keyword,
        entity_type=entity_type,
        offset=offset,
        limit=limit
    )
    
    result = await handler.handle(query)
    
    return {
        "entities": result.entities,
        "total": result.total,
        "offset": result.offset,
        "limit": result.limit,
        "has_more": result.has_more
    }


@router.get("/{entity_id}", response_model=dict[str, Any])
async def get_entity(
    entity_id: str,
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """获取实体详情
    
    返回实体的完整信息，包括属性、标签等
    """
    result = await Neo4jClient.execute_read(
        queries.GET_ENTITY_BY_ID,
        {"project_id": project_id, "entity_id": entity_id}
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    entity_data = result[0].get("entity", {})
    
    # 解析properties_json
    import json
    props_json = entity_data.get("properties_json")
    if props_json:
        entity_data["properties"] = json.loads(props_json)
    else:
        entity_data["properties"] = {}
    
    return entity_data


@router.put("/{entity_id}", response_model=dict[str, Any])
async def update_entity(
    entity_id: str,
    project_id: Annotated[str, Query(..., description="项目ID")],
    payload: EntityUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """更新实体
    
    更新实体的标签和属性
    """
    import json
    
    result = await Neo4jClient.execute_write(
        queries.UPDATE_ENTITY,
        {
            "project_id": project_id,
            "entity_id": entity_id,
            "labels": payload.labels,
            "properties_json": json.dumps(payload.properties)
        }
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    entity_data = result[0].get("entity", {})
    props_json = entity_data.get("properties_json")
    if props_json:
        entity_data["properties"] = json.loads(props_json)
    else:
        entity_data["properties"] = {}
    
    return entity_data


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: str,
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """删除实体
    
    删除实体及其所有关系
    """
    await Neo4jClient.execute_write(
        queries.DELETE_ENTITY,
        {"project_id": project_id, "entity_id": entity_id}
    )


@router.post("/batch", response_model=BatchOperationResponse)
async def batch_operation(
    project_id: Annotated[str, Query(..., description="项目ID")],
    payload: BatchEntityOperation,
    current_user: Annotated[User, Depends(get_current_user)],
) -> BatchOperationResponse:
    """批量实体操作
    
    支持批量创建、更新、删除实体
    
    - operation: create | update | delete
    - entities: 实体列表，每项包含id, external_id, type, labels, properties等
    """
    import json
    
    processed = 0
    failed = 0
    errors = []
    
    if payload.operation == "create":
        # 批量创建
        for entity_data in payload.entities:
            try:
                entity_data["id"] = entity_data.get("id") or str(__import__('uuid').uuid4())
                entity_data["properties_json"] = json.dumps(entity_data.get("properties", {}))
            except Exception as e:
                failed += 1
                errors.append(str(e))
        
        if payload.entities:
            try:
                result = await Neo4jClient.execute_write(
                    queries.BATCH_CREATE_ENTITIES,
                    {
                        "project_id": project_id,
                        "entities": payload.entities
                    }
                )
                processed = result[0].get("created_count", 0) if result else 0
            except Exception as e:
                errors.append(str(e))
                failed = len(payload.entities)
    
    elif payload.operation == "update":
        # 批量更新
        for entity_data in payload.entities:
            try:
                entity_id = entity_data.get("id")
                if not entity_id:
                    failed += 1
                    errors.append("Entity ID is required for update")
                    continue
                
                await Neo4jClient.execute_write(
                    queries.UPDATE_ENTITY,
                    {
                        "project_id": project_id,
                        "entity_id": entity_id,
                        "labels": entity_data.get("labels", []),
                        "properties_json": json.dumps(entity_data.get("properties", {}))
                    }
                )
                processed += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))
    
    elif payload.operation == "delete":
        # 批量删除
        for entity_data in payload.entities:
            try:
                entity_id = entity_data.get("id")
                if not entity_id:
                    failed += 1
                    continue
                
                await Neo4jClient.execute_write(
                    queries.DELETE_ENTITY,
                    {"project_id": project_id, "entity_id": entity_id}
                )
                processed += 1
            except Exception as e:
                failed += 1
                errors.append(str(e))
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported operation: {payload.operation}"
        )
    
    return BatchOperationResponse(
        success=len(errors) == 0,
        processed_count=processed,
        failed_count=failed,
        errors=errors
    )
