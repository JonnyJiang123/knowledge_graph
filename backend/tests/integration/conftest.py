import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.value_objects.industry import Industry
from src.infrastructure.persistence.mysql.database import async_session_maker
from src.infrastructure.persistence.mysql.repositories.data_source_repository import MySQLDataSourceRepository
from src.infrastructure.persistence.mysql.repositories.graph_project_repository import (
    MySQLGraphProjectRepository,
)
from src.infrastructure.persistence.mysql.repositories.ingestion_job_repository import MySQLIngestionJobRepository
from src.infrastructure.persistence.mysql.user_repository import MySQLUserRepository
from src.infrastructure.persistence.mysql.project_repository import MySQLProjectRepository
from src.infrastructure.persistence.neo4j.client import Neo4jClient
from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository


@pytest.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def user_repo(db_session: AsyncSession):
    return MySQLUserRepository(db_session)


@pytest.fixture
async def project_repo(db_session: AsyncSession):
    return MySQLProjectRepository(db_session)


@pytest.fixture
async def data_source_repo(db_session: AsyncSession):
    return MySQLDataSourceRepository(db_session)


@pytest.fixture
async def graph_project_repo(db_session: AsyncSession):
    return MySQLGraphProjectRepository(db_session)


@pytest.fixture
async def ingestion_job_repo(db_session: AsyncSession):
    return MySQLIngestionJobRepository(db_session)


@pytest_asyncio.fixture
async def neo4j_client():
    await Neo4jClient.connect()
    yield Neo4jClient
    await Neo4jClient.disconnect()


@pytest_asyncio.fixture
async def neo4j_repo(neo4j_client) -> Neo4jGraphRepository:
    async with neo4j_client.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    return Neo4jGraphRepository()


@pytest.fixture
async def owner(user_repo: MySQLUserRepository):
    user = User(
        id=str(uuid4()),
        username=f"user_{uuid4().hex[:8]}",
        email=f"{uuid4().hex[:8]}@example.com",
        hashed_password="hashedpwd",
    )
    await user_repo.create(user)
    return user


@pytest.fixture
async def project(
    owner: User,
    project_repo: MySQLProjectRepository,
) -> Project:
    project = Project(
        id=str(uuid4()),
        name="Test Project",
        industry=Industry.FINANCE,
        owner_id=owner.id,
    )
    await project_repo.create(project)
    return project
