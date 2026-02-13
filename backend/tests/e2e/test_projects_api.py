import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


@pytest.fixture
async def client():
    """HTTP客户端 fixture"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient):
    """认证头 fixture - 注册并登录测试用户"""
    username = f"testuser_{uuid4().hex[:8]}"
    await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpass123",
        },
    )

    response = await client.post(
        "/api/auth/login",
        data={"username": username, "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers: dict):
    """测试创建项目"""
    response = await client.post(
        "/api/projects",
        json={
            "name": "Test Finance Project",
            "description": "A test project for finance",
            "industry": "FINANCE",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Finance Project"
    assert data["industry"] == "FINANCE"


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, auth_headers: dict):
    """测试列出项目"""
    # 创建两个项目
    await client.post(
        "/api/projects",
        json={"name": "Project 1", "industry": "FINANCE"},
        headers=auth_headers,
    )
    await client.post(
        "/api/projects",
        json={"name": "Project 2", "industry": "HEALTHCARE"},
        headers=auth_headers,
    )

    # 列出项目
    response = await client.get("/api/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, auth_headers: dict):
    """测试获取单个项目"""
    # 创建项目
    create_response = await client.post(
        "/api/projects",
        json={"name": "Get Test Project", "industry": "HEALTHCARE"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    # 获取项目
    response = await client.get(f"/api/projects/{project_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Get Test Project"


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, auth_headers: dict):
    """测试更新项目"""
    # 创建项目
    create_response = await client.post(
        "/api/projects",
        json={"name": "Update Test", "industry": "FINANCE"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    # 更新项目
    response = await client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Updated Name", "description": "New description"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "New description"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient, auth_headers: dict):
    """测试删除项目"""
    # 创建项目
    create_response = await client.post(
        "/api/projects",
        json={"name": "Delete Test", "industry": "FINANCE"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    # 删除项目
    response = await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204

    # 验证已删除
    get_response = await client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """测试未授权访问"""
    response = await client.get("/api/projects")
    assert response.status_code == 401
