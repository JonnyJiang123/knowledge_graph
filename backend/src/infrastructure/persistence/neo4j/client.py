from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from src.config import settings


class Neo4jClient:
    """Neo4j 异步客户端"""
    _driver: AsyncDriver | None = None

    @classmethod
    async def connect(cls) -> None:
        """连接到 Neo4j 数据库"""
        cls._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        # 验证连接
        async with cls._driver.session() as session:
            await session.run("RETURN 1")

    @classmethod
    async def disconnect(cls) -> None:
        """断开 Neo4j 连接"""
        if cls._driver:
            await cls._driver.close()
            cls._driver = None

    @classmethod
    @asynccontextmanager
    async def session(cls) -> AsyncGenerator[AsyncSession, None]:
        """获取 Neo4j 会话"""
        if not cls._driver:
            raise RuntimeError("Neo4j client not connected")
        async with cls._driver.session() as session:
            yield session

    @classmethod
    async def execute_read(
        cls, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """执行读取查询"""
        async with cls.session() as session:
            result = await session.run(query, parameters or {})
            return [dict(record) async for record in result]

    @classmethod
    async def execute_write(
        cls, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """执行写入查询"""
        async with cls.session() as session:
            result = await session.run(query, parameters or {})
            return [dict(record) async for record in result]
