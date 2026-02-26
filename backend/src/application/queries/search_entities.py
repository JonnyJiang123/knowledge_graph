"""实体搜索查询

支持关键词搜索、类型过滤和分页
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Type

from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j import cypher_queries as queries


@dataclass(slots=True)
class SearchEntitiesQuery:
    """实体搜索查询参数
    
    Attributes:
        project_id: 项目ID
        owner_id: 用户ID（用于权限验证）
        keyword: 搜索关键词（可选）
        entity_type: 实体类型过滤（可选）
        offset: 分页偏移量
        limit: 每页数量
    """
    project_id: str
    owner_id: str
    keyword: str | None = None
    entity_type: str | None = None
    offset: int = 0
    limit: int = 20


@dataclass(slots=True)
class SearchEntitiesResult:
    """实体搜索结果
    
    Attributes:
        entities: 实体列表
        total: 总数量
        offset: 当前偏移量
        limit: 每页数量
        has_more: 是否还有更多结果
    """
    entities: list[dict[str, Any]]
    total: int
    offset: int
    limit: int
    has_more: bool


class SearchEntitiesHandler:
    """实体搜索查询处理器"""
    
    def __init__(self, client: Type[Neo4jClient] = Neo4jClient):
        self._client = client
    
    async def handle(self, query: SearchEntitiesQuery) -> SearchEntitiesResult:
        """执行实体搜索
        
        Args:
            query: 搜索查询参数
            
        Returns:
            搜索结果
        """
        # 构建查询参数
        search_keyword = query.keyword or ""
        
        # 获取总数
        count_result = await self._client.execute_read(
            queries.COUNT_ENTITIES,
            {
                "project_id": query.project_id,
                "keyword": search_keyword if search_keyword else None,
                "entity_type": query.entity_type
            }
        )
        total = count_result[0].get("total", 0) if count_result else 0
        
        # 执行搜索
        if query.entity_type:
            # 带类型过滤的搜索
            results = await self._client.execute_read(
                queries.SEARCH_ENTITIES_BY_TYPE,
                {
                    "project_id": query.project_id,
                    "keyword": search_keyword,
                    "entity_type": query.entity_type,
                    "offset": query.offset,
                    "limit": query.limit
                }
            )
        else:
            # 通用搜索
            results = await self._client.execute_read(
                queries.SEARCH_ENTITIES,
                {
                    "project_id": query.project_id,
                    "keyword": search_keyword,
                    "offset": query.offset,
                    "limit": query.limit
                }
            )
        
        # 提取实体数据
        entities = []
        for record in results:
            entity_data = record.get("entity", {})
            # 解析properties_json
            import json
            props_json = entity_data.get("properties_json")
            if props_json:
                entity_data["properties"] = json.loads(props_json)
            else:
                entity_data["properties"] = {}
            entities.append(entity_data)
        
        has_more = (query.offset + len(entities)) < total
        
        return SearchEntitiesResult(
            entities=entities,
            total=total,
            offset=query.offset,
            limit=query.limit,
            has_more=has_more
        )
