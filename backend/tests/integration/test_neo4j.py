import pytest
from src.infrastructure.persistence.neo4j.client import Neo4jClient


@pytest.fixture
async def neo4j_client():
    """Neo4j 客户端 fixture"""
    await Neo4jClient.connect()
    yield Neo4jClient
    await Neo4jClient.disconnect()


@pytest.mark.asyncio
async def test_neo4j_connection(neo4j_client):
    """测试 Neo4j 连接"""
    result = await neo4j_client.execute_read("RETURN 1 as value")
    assert result[0]["value"] == 1


@pytest.mark.asyncio
async def test_neo4j_create_and_query_node(neo4j_client):
    """测试创建和查询节点"""
    # 创建测试节点
    await neo4j_client.execute_write(
        "CREATE (n:TestNode {name: $name}) RETURN n",
        {"name": "test_node"}
    )

    # 查询节点
    result = await neo4j_client.execute_read(
        "MATCH (n:TestNode {name: $name}) RETURN n.name as name",
        {"name": "test_node"}
    )
    assert result[0]["name"] == "test_node"

    # 清理测试数据
    await neo4j_client.execute_write(
        "MATCH (n:TestNode {name: $name}) DELETE n",
        {"name": "test_node"}
    )
