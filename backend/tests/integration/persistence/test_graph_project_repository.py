import pytest

from src.domain.entities.graph_project import GraphProject
from src.domain.entities.user import User
from src.domain.value_objects.industry import Industry
from src.infrastructure.persistence.mysql.repositories.graph_project_repository import (
    MySQLGraphProjectRepository,
)


@pytest.mark.asyncio
async def test_create_and_get_graph_project(
    owner: User,
    graph_project_repo: MySQLGraphProjectRepository,
):
    project = GraphProject.new(
        name="AML Graph",
        owner_id=owner.id,
        industry=Industry.FINANCE,
        metadata={"region": "APAC"},
    )

    saved = await graph_project_repo.create(project)
    fetched = await graph_project_repo.get(saved.id)

    assert fetched is not None
    assert fetched.name == "AML Graph"
    assert fetched.metadata.get("region") == "APAC"


@pytest.mark.asyncio
async def test_list_by_owner_and_update_status(
    owner: User,
    graph_project_repo: MySQLGraphProjectRepository,
):
    project_one = GraphProject.new(
        name="Fraud Graph",
        owner_id=owner.id,
        industry=Industry.FINANCE,
    )
    project_two = GraphProject.new(
        name="Pharma Graph",
        owner_id=owner.id,
        industry=Industry.HEALTHCARE,
    )

    await graph_project_repo.create(project_one)
    await graph_project_repo.create(project_two)

    await graph_project_repo.update_status(project_one.id, "ARCHIVED")

    archived = await graph_project_repo.get(project_one.id)
    assert archived is not None
    assert archived.status == "ARCHIVED"

    projects = await graph_project_repo.list_by_owner(owner.id)
    ids = {p.id for p in projects}
    assert project_one.id in ids
    assert project_two.id in ids
