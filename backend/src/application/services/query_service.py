"""查询服务

路由查询到不同处理器，提供结果缓存和查询日志功能
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Callable, TypeVar

from src.application.queries.search_entities import (
    SearchEntitiesQuery,
    SearchEntitiesResult,
    SearchEntitiesHandler
)
from src.application.queries.find_paths import (
    FindShortestPathQuery,
    FindAllPathsQuery,
    PathResult,
    FindShortestPathHandler,
    FindAllPathsHandler
)
from src.application.queries.get_graph_visualization import (
    GetGraphVisualizationQuery,
    GraphVisualizationResult,
    GetGraphVisualizationHandler
)
from src.application.queries.analyze_centrality import (
    AnalyzeCentralityQuery,
    AnalyzeCommunitiesQuery,
    CentralityAnalysisResult,
    CommunityAnalysisResult,
    AnalyzeCentralityHandler,
    AnalyzeCommunitiesHandler
)
from src.infrastructure.cache.in_memory import InMemoryPreviewCache

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class QueryLog:
    """查询日志"""
    query_id: str
    query_type: str
    project_id: str
    user_id: str
    parameters: dict[str, Any]
    execution_time_ms: float
    result_size: int
    cache_hit: bool
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class QueryServiceError(Exception):
    """查询服务错误"""
    pass


class QueryService:
    """查询服务
    
    功能：
    1. 路由查询到对应的处理器
    2. 结果缓存（Redis/内存）
    3. 查询日志记录
    4. 性能监控
    """
    
    # 缓存时间配置（秒）
    CACHE_TTL = {
        "search_entities": 300,      # 5分钟
        "find_shortest_path": 600,   # 10分钟
        "find_all_paths": 300,       # 5分钟
        "get_visualization": 60,     # 1分钟
        "analyze_centrality": 1800,  # 30分钟
        "analyze_communities": 3600, # 60分钟
    }
    
    def __init__(
        self,
        cache: InMemoryPreviewCache | None = None,
        enable_logging: bool = True
    ):
        self._cache = cache or InMemoryPreviewCache()
        self._enable_logging = enable_logging
        self._query_logs: list[QueryLog] = []
        
        # 初始化处理器
        self._search_handler = SearchEntitiesHandler()
        self._shortest_path_handler = FindShortestPathHandler()
        self._all_paths_handler = FindAllPathsHandler()
        self._visualization_handler = GetGraphVisualizationHandler()
        self._centrality_handler = AnalyzeCentralityHandler()
        self._communities_handler = AnalyzeCommunitiesHandler()
    
    def _generate_cache_key(self, query_type: str, params: dict[str, Any]) -> str:
        """生成缓存键"""
        # 排除某些不需要参与缓存键计算的字段
        exclude_keys = {"owner_id", "user_id", "timestamp"}
        cache_params = {k: v for k, v in params.items() if k not in exclude_keys}
        
        param_str = json.dumps(cache_params, sort_keys=True)
        hash_str = hashlib.md5(f"{query_type}:{param_str}".encode()).hexdigest()
        return f"query:{query_type}:{hash_str}"
    
    async def _get_from_cache(self, cache_key: str) -> Any | None:
        """从缓存获取结果"""
        try:
            return await self._cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    async def _set_to_cache(self, cache_key: str, result: Any, ttl: int) -> None:
        """设置缓存结果"""
        try:
            await self._cache.set(cache_key, result, ttl)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    def _log_query(self, log: QueryLog) -> None:
        """记录查询日志"""
        if not self._enable_logging:
            return
        
        self._query_logs.append(log)
        
        # 保留最近1000条日志
        if len(self._query_logs) > 1000:
            self._query_logs = self._query_logs[-1000:]
        
        # 记录到系统日志
        status = "HIT" if log.cache_hit else "MISS"
        logger.info(
            f"Query[{log.query_type}] {status} | "
            f"Project: {log.project_id} | "
            f"Time: {log.execution_time_ms:.2f}ms | "
            f"Results: {log.result_size}"
        )
    
    async def _execute_with_cache(
        self,
        query_type: str,
        params: dict[str, Any],
        executor: Callable[[], Any]
    ) -> Any:
        """带缓存的查询执行"""
        cache_key = self._generate_cache_key(query_type, params)
        ttl = self.CACHE_TTL.get(query_type, 300)
        
        # 尝试从缓存获取
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result, True
        
        # 执行查询
        start_time = time.time()
        result = await executor()
        execution_time = (time.time() - start_time) * 1000
        
        # 存入缓存
        await self._set_to_cache(cache_key, result, ttl)
        
        return result, False
    
    async def search_entities(
        self,
        query: SearchEntitiesQuery
    ) -> SearchEntitiesResult:
        """搜索实体
        
        Args:
            query: 实体搜索查询
            
        Returns:
            搜索结果
        """
        params = {
            "project_id": query.project_id,
            "keyword": query.keyword,
            "entity_type": query.entity_type,
            "offset": query.offset,
            "limit": query.limit
        }
        
        start_time = time.time()
        result, cache_hit = await self._execute_with_cache(
            "search_entities",
            params,
            lambda: self._search_handler.handle(query)
        )
        execution_time = (time.time() - start_time) * 1000
        
        # 记录日志
        self._log_query(QueryLog(
            query_id=self._generate_cache_key("search_entities", params),
            query_type="search_entities",
            project_id=query.project_id,
            user_id=query.owner_id,
            parameters=params,
            execution_time_ms=execution_time,
            result_size=len(result.entities) if hasattr(result, 'entities') else 0,
            cache_hit=cache_hit
        ))
        
        return result
    
    async def find_shortest_path(
        self,
        query: FindShortestPathQuery
    ) -> PathResult:
        """查找最短路径
        
        Args:
            query: 最短路径查询
            
        Returns:
            路径结果
        """
        params = {
            "project_id": query.project_id,
            "start_id": query.start_id,
            "end_id": query.end_id,
            "max_depth": query.max_depth
        }
        
        start_time = time.time()
        result, cache_hit = await self._execute_with_cache(
            "find_shortest_path",
            params,
            lambda: self._shortest_path_handler.handle(query)
        )
        execution_time = (time.time() - start_time) * 1000
        
        self._log_query(QueryLog(
            query_id=self._generate_cache_key("find_shortest_path", params),
            query_type="find_shortest_path",
            project_id=query.project_id,
            user_id=query.owner_id,
            parameters=params,
            execution_time_ms=execution_time,
            result_size=len(result.nodes) if hasattr(result, 'nodes') else 0,
            cache_hit=cache_hit
        ))
        
        return result
    
    async def find_all_paths(
        self,
        query: FindAllPathsQuery
    ) -> PathResult:
        """查找所有路径
        
        Args:
            query: 所有路径查询
            
        Returns:
            路径结果
        """
        params = {
            "project_id": query.project_id,
            "start_id": query.start_id,
            "end_id": query.end_id,
            "max_depth": query.max_depth,
            "path_limit": query.path_limit
        }
        
        start_time = time.time()
        result, cache_hit = await self._execute_with_cache(
            "find_all_paths",
            params,
            lambda: self._all_paths_handler.handle(query)
        )
        execution_time = (time.time() - start_time) * 1000
        
        self._log_query(QueryLog(
            query_id=self._generate_cache_key("find_all_paths", params),
            query_type="find_all_paths",
            project_id=query.project_id,
            user_id=query.owner_id,
            parameters=params,
            execution_time_ms=execution_time,
            result_size=result.path_count if hasattr(result, 'path_count') else 0,
            cache_hit=cache_hit
        ))
        
        return result
    
    async def get_graph_visualization(
        self,
        query: GetGraphVisualizationQuery
    ) -> GraphVisualizationResult:
        """获取图可视化数据
        
        Args:
            query: 可视化查询
            
        Returns:
            可视化数据
        """
        params = {
            "project_id": query.project_id,
            "node_limit": query.node_limit,
            "entity_type": query.entity_type,
            "center_entity_id": query.center_entity_id,
            "depth": query.depth
        }
        
        start_time = time.time()
        result, cache_hit = await self._execute_with_cache(
            "get_visualization",
            params,
            lambda: self._visualization_handler.handle(query)
        )
        execution_time = (time.time() - start_time) * 1000
        
        self._log_query(QueryLog(
            query_id=self._generate_cache_key("get_visualization", params),
            query_type="get_visualization",
            project_id=query.project_id,
            user_id=query.owner_id,
            parameters=params,
            execution_time_ms=execution_time,
            result_size=len(result.nodes) if hasattr(result, 'nodes') else 0,
            cache_hit=cache_hit
        ))
        
        return result
    
    async def analyze_centrality(
        self,
        query: AnalyzeCentralityQuery
    ) -> CentralityAnalysisResult:
        """分析中心性
        
        Args:
            query: 中心性分析查询
            
        Returns:
            中心性分析结果
        """
        params = {
            "project_id": query.project_id,
            "algorithm": query.algorithm,
            "limit": query.limit
        }
        
        start_time = time.time()
        result, cache_hit = await self._execute_with_cache(
            "analyze_centrality",
            params,
            lambda: self._centrality_handler.handle(query)
        )
        execution_time = (time.time() - start_time) * 1000
        
        # 更新执行时间
        if hasattr(result, 'execution_time_ms') and result.execution_time_ms is None:
            result.execution_time_ms = round(execution_time, 2)
        
        self._log_query(QueryLog(
            query_id=self._generate_cache_key("analyze_centrality", params),
            query_type="analyze_centrality",
            project_id=query.project_id,
            user_id=query.owner_id,
            parameters=params,
            execution_time_ms=execution_time,
            result_size=len(result.scores) if hasattr(result, 'scores') else 0,
            cache_hit=cache_hit
        ))
        
        return result
    
    async def analyze_communities(
        self,
        query: AnalyzeCommunitiesQuery
    ) -> CommunityAnalysisResult:
        """分析社区
        
        Args:
            query: 社区分析查询
            
        Returns:
            社区分析结果
        """
        params = {
            "project_id": query.project_id,
            "algorithm": query.algorithm
        }
        
        start_time = time.time()
        result, cache_hit = await self._execute_with_cache(
            "analyze_communities",
            params,
            lambda: self._communities_handler.handle(query)
        )
        execution_time = (time.time() - start_time) * 1000
        
        self._log_query(QueryLog(
            query_id=self._generate_cache_key("analyze_communities", params),
            query_type="analyze_communities",
            project_id=query.project_id,
            user_id=query.owner_id,
            parameters=params,
            execution_time_ms=execution_time,
            result_size=result.total_communities if hasattr(result, 'total_communities') else 0,
            cache_hit=cache_hit
        ))
        
        return result
    
    def get_query_logs(
        self,
        project_id: str | None = None,
        query_type: str | None = None,
        limit: int = 100
    ) -> list[QueryLog]:
        """获取查询日志
        
        Args:
            project_id: 按项目过滤
            query_type: 按查询类型过滤
            limit: 返回数量限制
            
        Returns:
            查询日志列表
        """
        logs = self._query_logs
        
        if project_id:
            logs = [log for log in logs if log.project_id == project_id]
        
        if query_type:
            logs = [log for log in logs if log.query_type == query_type]
        
        return logs[-limit:]
    
    def get_statistics(self) -> dict[str, Any]:
        """获取查询统计信息"""
        if not self._query_logs:
            return {
                "total_queries": 0,
                "cache_hit_rate": 0,
                "avg_execution_time_ms": 0
            }
        
        total = len(self._query_logs)
        cache_hits = sum(1 for log in self._query_logs if log.cache_hit)
        avg_time = sum(log.execution_time_ms for log in self._query_logs) / total
        
        # 按类型统计
        type_stats = {}
        for log in self._query_logs:
            if log.query_type not in type_stats:
                type_stats[log.query_type] = {"count": 0, "cache_hits": 0}
            type_stats[log.query_type]["count"] += 1
            if log.cache_hit:
                type_stats[log.query_type]["cache_hits"] += 1
        
        return {
            "total_queries": total,
            "cache_hit_rate": round(cache_hits / total * 100, 2),
            "avg_execution_time_ms": round(avg_time, 2),
            "type_statistics": type_stats
        }
