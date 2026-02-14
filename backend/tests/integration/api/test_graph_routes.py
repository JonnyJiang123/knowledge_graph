from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.graph import get_graph_service
from src.application.commands.create_graph_project import CreateGraphProjectCommand
from src.application.services.graph_service import (
    GraphProjectAccessError,
    GraphProjectNotFoundError,
)
from src.domain.entities.entity import Entity
from src.domain.entities.graph_project import GraphProject
from src.domain.entities.relation import Relation
from src.domain.entities.user import User
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.industry import Industry
from src.domain.value_objects.relation_type import RelationType
from src.main import app


class FakeGraphService:
    """Minimal fake service that returns deterministic objects."""

    def __init__(self):
        self.project = GraphProject.new(
            name="Fraud Graph",
            owner_id="user-1",
            industry=Industry.FINANCE,
            metadata={"tier": "gold"},
        )

    async def create_project(self, command: CreateGraphProjectCommand) -> GraphProject:
        return self.project

    async def list_projects(self, owner_id: str) -> list[GraphProject]:
        if owner_id != self.project.owner_id:
            return []
        return [self.project]

    async def get_project(self, project_id: str, owner_id: str) -> GraphProject:
        if project_id != self.project.id:
            raise GraphProjectNotFoundError(project_id)
        if owner_id != self.project.owner_id:
            raise GraphProjectAccessError(project_id)
        return self.project

    async def create_entity(self, command):
        entity = Entity.create(
            project_id=command.project_id,
            external_id=command.external_id,
            type=command.type,
        )
        entity.id = "entity-1"
        return entity

    async def create_relation(self, command):
        relation = Relation.create(
            project_id=command.project_id,
            source_id=command.source_id,
            target_id=command.target_id,
            type=command.type,
        )
        relation.id = "rel-1"
        return relation

    async def list_neighbors(self, query):
        if query.project_id != self.project.id:
            raise GraphProjectAccessError(query.project_id)
        return {
            "entities": [
                {
                    "id": "entity-1",
                    "project_id": self.project.id,
                    "external_id": "acct-1",
                    "type": EntityType.ACCOUNT.value,
                    "labels": ["Account"],
                    "properties": {"balance": 10},
                }
            ],
            "relations": [
                {
                    "id": "rel-1",
                    "project_id": self.project.id,
                    "source_id": "entity-1",
                    "target_id": "entity-2",
                    "type": RelationType.OWNS.value,
                    "properties": {"score": 0.7},
                }
            ],
        }


@pytest.fixture
def fake_graph_service():
    return FakeGraphService()


@pytest.fixture(autouse=True)
def override_graph_dependencies(fake_graph_service: FakeGraphService):
    app.dependency_overrides[get_graph_service] = lambda: fake_graph_service
    app.dependency_overrides[get_current_user] = lambda: User(
        id="user-1",
        username="tester",
        email="tester@example.com",
        hashed_password="x",
    )
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_graph_project(client: AsyncClient):
    payload = {
        "name": "Fraud Graph",
        "industry": Industry.FINANCE.value,
        "metadata": {"tier": "gold"},
    }
    response = await client.post("/api/graph/projects", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Fraud Graph"


@pytest.mark.asyncio
async def test_create_entity_endpoint(client: AsyncClient, fake_graph_service: FakeGraphService):
    payload = {
        "external_id": "acct-1",
        "type": EntityType.ACCOUNT.value,
        "labels": ["Account"],
        "properties": {"status": "ACTIVE"},
    }
    response = await client.post(f"/api/graph/projects/{fake_graph_service.project.id}/entities", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["external_id"] == "acct-1"


@pytest.mark.asyncio
async def test_create_relation_endpoint(client: AsyncClient, fake_graph_service: FakeGraphService):
    payload = {
        "source_id": "entity-1",
        "target_id": "entity-2",
        "type": RelationType.OWNS.value,
        "properties": {"score": 0.8},
    }
    response = await client.post(f"/api/graph/projects/{fake_graph_service.project.id}/relations", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["type"] == RelationType.OWNS.value


@pytest.mark.asyncio
async def test_neighbors_endpoint(client: AsyncClient, fake_graph_service: FakeGraphService):
    fake_project_id = fake_graph_service.project.id
    response = await client.get(
        f"/api/graph/projects/{fake_project_id}/neighbors",
        params={"entity_id": "entity-1", "depth": 2, "limit": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["entities"]) == 1
    assert body["relations"][0]["properties"]["score"] == 0.7


@pytest.mark.asyncio
async def test_neighbors_forbidden_when_not_owner(client: AsyncClient):
    response = await client.get(
        "/api/graph/projects/unauthorized/neighbors",
        params={"entity_id": "entity-1"},
    )
    assert response.status_code == 403
