"""关系路由

提供关系的CRUD操作
"""

from __future__ import annotations

from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.dependencies.auth import get_current_user
from src.domain.entities.user import User
from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j import cypher_queries as queries

router = APIRouter(prefix="/api/relations", tags=["relations"])


class RelationResponse(BaseModel):
    """关系响应"""
    id: str
    project_id: str
    source_id: str
    target_id: str
    type: str
    properties: dict[str, Any]
    created_at: str | None = None
    updated_at: str | None = None


class BatchRelationCreate(BaseModel):
    """批量创建关系请求"""
    relations: List[dict[str, Any]] = Field(..., description="关系列表")


class BatchRelationResponse(BaseModel):
    """批量操作响应"""
    success: bool
    created_count: int
    failed_count: int
    errors: List[str]


@router.get("", response_model=dict[str, Any])
async def search_relations(
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    relation_type: Annotated[str | None, Query(default=None, description="关系类型")] = None,
    keyword: Annotated[str | None, Query(default=None, description="搜索关键词")] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """搜索关系
    
    支持按类型过滤和关键词搜索
    """
    result = await Neo4jClient.execute_read(
        queries.SEARCH_RELATIONS,
        {
            "project_id": project_id,
            "relation_type": relation_type,
            "keyword": keyword,
            "offset": offset,
            "limit": limit
        }
    )
    
    # 获取总数
    count_result = await Neo4jClient.execute_read(
        queries.COUNT_RELATIONS,
        {"project_id": project_id, "relation_type": relation_type}
    )
    total = count_result[0].get("total", 0) if count_result else 0
    
    # 解析结果
    relations = []
    import json
    for record in result:
        rel_data = dict(record.get("relation", {}))
        rel_data["source_id"] = record.get("source_id", "")
        rel_data["target_id"] = record.get("target_id", "")
        
        # 解析properties_json
        props_json = rel_data.get("properties_json")
        if props_json:
            rel_data["properties"] = json.loads(props_json)
        else:
            rel_data["properties"] = {}
        
        relations.append(rel_data)
    
    return {
        "relations": relations,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + len(relations)) < total
    }


@router.get("/{relation_id}", response_model=dict[str, Any])
async def get_relation(
    relation_id: str,
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """获取关系详情"""
    query = """
    MATCH (:Entity {project_id: $project_id})-[r:RELATION {id: $relation_id}]-(:Entity {project_id: $project_id})
    RETURN r as relation, startNode(r).id as source_id, endNode(r).id as target_id
    """
    
    result = await Neo4jClient.execute_read(
        query,
        {"project_id": project_id, "relation_id": relation_id}
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation not found"
        )
    
    rel_data = dict(result[0].get("relation", {}))
    rel_data["source_id"] = result[0].get("source_id", "")
    rel_data["target_id"] = result[0].get("target_id", "")
    
    # 解析properties_json
    import json
    props_json = rel_data.get("properties_json")
    if props_json:
        rel_data["properties"] = json.loads(props_json)
    else:
        rel_data["properties"] = {}
    
    return rel_data


@router.delete("/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relation(
    relation_id: str,
    project_id: Annotated[str, Query(..., description="项目ID")],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """删除关系"""
    await Neo4jClient.execute_write(
        queries.DELETE_RELATION,
        {"project_id": project_id, "relation_id": relation_id}
    )


@router.post("/batch", response_model=BatchRelationResponse)
async def batch_create_relations(
    project_id: Annotated[str, Query(..., description="项目ID")],
    payload: BatchRelationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> BatchRelationResponse:
    """批量创建关系
    
    批量创建多个关系，每项需要包含：
    - source_id: 源实体ID
    - target_id: 目标实体ID  
    - type: 关系类型
    - properties: 关系属性（可选）
    """
    import json
    from uuid import uuid4
    
    relations = []
    errors = []
    
    for rel_data in payload.relations:
        try:
            relation = {
                "id": rel_data.get("id") or str(uuid4()),
                "source_id": rel_data.get("source_id"),
                "target_id": rel_data.get("target_id"),
                "type": rel_data.get("type", "RELATION"),
                "properties_json": json.dumps(rel_data.get("properties", {}))
            }
            
            if not relation["source_id"] or not relation["target_id"]:
                errors.append(f"Missing source_id or target_id: {rel_data}")
                continue
            
            relations.append(relation)
        except Exception as e:
            errors.append(str(e))
    
    if not relations:
        return BatchRelationResponse(
            success=False,
            created_count=0,
            failed_count=len(payload.relations),
            errors=errors
        )
    
    try:
        result = await Neo4jClient.execute_write(
            queries.BATCH_CREATE_RELATIONS,
            {
                "project_id": project_id,
                "relations": relations
            }
        )
        created_count = result[0].get("created_count", 0) if result else 0
        
        return BatchRelationResponse(
            success=len(errors) == 0,
            created_count=created_count,
            failed_count=len(errors),
            errors=errors
        )
    except Exception as e:
        return BatchRelationResponse(
            success=False,
            created_count=0,
            failed_count=len(relations),
            errors=[str(e)]
        )
