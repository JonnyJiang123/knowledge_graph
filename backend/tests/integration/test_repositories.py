import pytest
from uuid import uuid4

from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.value_objects.industry import Industry
from src.infrastructure.persistence.mysql.project_repository import MySQLProjectRepository
from src.infrastructure.persistence.mysql.user_repository import MySQLUserRepository


@pytest.mark.asyncio
async def test_create_and_get_user(user_repo: MySQLUserRepository):
    user = User(
        id=str(uuid4()),
        username=f"testuser_{uuid4().hex[:8]}",
        email=f"test_{uuid4().hex[:8]}@example.com",
        hashed_password="hashedpwd",
    )

    created = await user_repo.create(user)
    assert created.id == user.id
    assert created.username == user.username

    fetched = await user_repo.get_by_id(user.id)
    assert fetched is not None
    assert fetched.username == user.username


@pytest.mark.asyncio
async def test_create_and_list_projects(
    user_repo: MySQLUserRepository,
    project_repo: MySQLProjectRepository,
):
    user = User(
        id=str(uuid4()),
        username=f"projowner_{uuid4().hex[:8]}",
        email=f"owner_{uuid4().hex[:8]}@example.com",
        hashed_password="hashedpwd",
    )
    await user_repo.create(user)

    project1 = Project(
        id=str(uuid4()),
        name="Finance Project",
        industry=Industry.FINANCE,
        owner_id=user.id,
    )
    project2 = Project(
        id=str(uuid4()),
        name="Healthcare Project",
        industry=Industry.HEALTHCARE,
        owner_id=user.id,
    )

    await project_repo.create(project1)
    await project_repo.create(project2)

    projects = await project_repo.list_by_owner(user.id)
    assert len(projects) == 2
    names = {p.name for p in projects}
    assert "Finance Project" in names
    assert "Healthcare Project" in names
