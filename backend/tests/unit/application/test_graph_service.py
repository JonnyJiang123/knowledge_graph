from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.commands.create_entity import CreateEntityCommand
from src.application.commands.create_graph_project import CreateGraphProjectCommand
from src.application.commands.create_relation import CreateRelationCommand
from src.application.queries.list_neighbors import ListNeighborsQuery
from src.application.services.graph_service import (
    GraphProjectAccessError,
    GraphProjectNotFoundError,
    GraphService,
)
from src.domain.entities.graph_project import GraphProject
from src.domain.value_objects.entity_type import EntityType
from src.domain.value_objects.industry import Industry
from src.domain.value_objects.relation_type import RelationType


@pytest.fixture
def graph_project_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def graph_entity_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def graph_service(graph_project_repo, graph_entity_repo):
    return GraphService(graph_project_repo=graph_project_repo, graph_entity_repo=graph_entity_repo)


def _project(owner_id: str, name: str = "Risk Graph") -> GraphProject:
    project = GraphProject.new(
        name=name,
        owner_id=owner_id,
        industry=Industry.FINANCE,
        metadata={"tier": "gold"},
    )
    return project


@pytest.mark.asyncio
async def test_create_project_persists(graph_service: GraphService, graph_project_repo: AsyncMock):
    graph_project_repo.create.return_value = _project("owner-1", name="Fraud Graph")
    command = CreateGraphProjectCommand(
        name="Fraud Graph",
        owner_id="owner-1",
        industry=Industry.FINANCE,
        description="AML baseline",
        metadata={"region": "APAC"},
    )

    project = await graph_service.create_project(command)

    graph_project_repo.create.assert_awaited()
    assert project.name == "Fraud Graph"


@pytest.mark.asyncio
async def test_create_entity_requires_membership(graph_service: GraphService, graph_project_repo: AsyncMock):
    project = _project("owner-1")
    graph_project_repo.get.return_value = project

    command = CreateEntityCommand(
        project_id=project.id,
        owner_id="other-user",
        external_id="acct-1",
        type=EntityType.ACCOUNT,
    )

    with pytest.raises(GraphProjectAccessError):
        await graph_service.create_entity(command)


@pytest.mark.asyncio
async def test_create_relation_merges(graph_service: GraphService, graph_project_repo: AsyncMock, graph_entity_repo: AsyncMock):
    project = _project("owner-1")
    graph_project_repo.get.return_value = project

    graph_entity_repo.merge_relation.return_value = None
    command = CreateRelationCommand(
        project_id=project.id,
        owner_id="owner-1",
        source_id=str(uuid4()),
        target_id=str(uuid4()),
        type=RelationType.OWNS,
        properties={"confidence": 0.8},
    )

    await graph_service.create_relation(command)

    graph_entity_repo.merge_relation.assert_awaited()


@pytest.mark.asyncio
async def test_list_neighbors_clamps_depth_and_limit(
    graph_service: GraphService,
    graph_project_repo: AsyncMock,
    graph_entity_repo: AsyncMock,
):
    project = _project("owner-1")
    graph_project_repo.get.return_value = project
    graph_entity_repo.find_neighbors.return_value = {
        "entities": [{"id": "a"}, {"id": "b"}],
        "relations": [{"id": "r1"}, {"id": "r2"}],
    }

    query = ListNeighborsQuery(
        project_id=project.id,
        owner_id="owner-1",
        entity_id="a",
        depth=5,
        limit=1,
    )
    neighbors = await graph_service.list_neighbors(query)

    graph_entity_repo.find_neighbors.assert_awaited_with(
        project_id=project.id,
        entity_id="a",
        depth=3,
    )
    assert len(neighbors["entities"]) == 1
    assert len(neighbors["relations"]) == 1


@pytest.mark.asyncio
async def test_get_project_not_found(graph_service: GraphService, graph_project_repo: AsyncMock):
    graph_project_repo.get.return_value = None

    with pytest.raises(GraphProjectNotFoundError):
        await graph_service.get_project("missing", owner_id="user-1")
