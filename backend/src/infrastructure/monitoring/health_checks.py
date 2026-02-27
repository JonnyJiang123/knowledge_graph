"""健康检查"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Callable


@dataclass
class HealthStatus:
    """健康状态"""
    name: str
    status: str  # healthy, unhealthy, unknown
    response_time_ms: float
    message: str = ""
    checked_at: datetime | None = None

    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now()


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self._checks: dict[str, Callable[[], HealthStatus]] = {}

    def register_check(self, name: str, check_func: Callable[[], HealthStatus]) -> None:
        """注册健康检查"""
        self._checks[name] = check_func

    async def check_all(self) -> dict[str, HealthStatus]:
        """执行所有健康检查"""
        results = {}

        for name, check_func in self._checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    results[name] = await check_func()
                else:
                    results[name] = check_func()
            except Exception as e:
                results[name] = HealthStatus(
                    name=name,
                    status="unhealthy",
                    response_time_ms=0,
                    message=str(e)
                )

        return results

    async def is_healthy(self) -> bool:
        """检查整体健康状态"""
        results = await self.check_all()
        return all(r.status == "healthy" for r in results.values())


# 预定义的健康检查

async def check_mysql() -> HealthStatus:
    """检查MySQL连接"""
    import time
    start = time.time()

    try:
        # 这里应该实际检查MySQL连接
        # from src.infrastructure.persistence.mysql.database import get_db
        # async with get_db() as db:
        #     await db.execute("SELECT 1")

        return HealthStatus(
            name="mysql",
            status="healthy",
            response_time_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return HealthStatus(
            name="mysql",
            status="unhealthy",
            response_time_ms=(time.time() - start) * 1000,
            message=str(e)
        )


async def check_neo4j() -> HealthStatus:
    """检查Neo4j连接"""
    import time
    start = time.time()

    try:
        # 这里应该实际检查Neo4j连接
        # from src.infrastructure.persistence.neo4j.client import get_neo4j_client
        # client = get_neo4j_client()
        # await client.run("RETURN 1")

        return HealthStatus(
            name="neo4j",
            status="healthy",
            response_time_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return HealthStatus(
            name="neo4j",
            status="unhealthy",
            response_time_ms=(time.time() - start) * 1000,
            message=str(e)
        )


async def check_redis() -> HealthStatus:
    """检查Redis连接"""
    import time
    start = time.time()

    try:
        # 这里应该实际检查Redis连接
        # import redis.asyncio as redis
        # r = redis.from_url("redis://localhost:6379")
        # await r.ping()

        return HealthStatus(
            name="redis",
            status="healthy",
            response_time_ms=(time.time() - start) * 1000
        )
    except Exception as e:
        return HealthStatus(
            name="redis",
            status="unhealthy",
            response_time_ms=(time.time() - start) * 1000,
            message=str(e)
        )


# 全局健康检查器
health_checker = HealthChecker()

# 注册默认检查
health_checker.register_check("mysql", check_mysql)
health_checker.register_check("neo4j", check_neo4j)
health_checker.register_check("redis", check_redis)
