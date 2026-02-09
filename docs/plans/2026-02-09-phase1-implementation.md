# Phase 1: Foundation + First Vertical Slice

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish project foundation with working auth and project CRUD as first vertical slice.

**Architecture:** Pragmatic Hexagonal - domain layer with ports, infrastructure adapters, FastAPI API layer. Vue 3 + Pinia frontend. See `docs/plans/2026-02-09-architecture-design.md` for full details.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy (async), Neo4j, MySQL, Redis, Vue 3, Vite, Pinia, Element Plus, TypeScript

---

## Task 1: Backend Project Scaffolding

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/src/__init__.py`
- Create: `backend/src/main.py`
- Create: `backend/src/config.py`

**Step 1: Create backend directory structure**

```bash
mkdir -p backend/src/{domain/{entities,value_objects,services,ports},application/{commands,queries,services},infrastructure/{persistence/{neo4j,mysql},queue,storage},api/{routers,schemas,middleware,dependencies}}
mkdir -p backend/tests/{unit/{domain,application},integration,e2e}
```

**Step 2: Create pyproject.toml**

Create `backend/pyproject.toml`:

```toml
[project]
name = "knowledge-graph-backend"
version = "0.1.0"
description = "Knowledge Graph Platform Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "asyncmy>=0.2.9",
    "neo4j>=5.17.0",
    "redis>=5.0.1",
    "celery>=5.3.6",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
    "alembic>=1.13.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

**Step 3: Create config.py**

Create `backend/src/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "Knowledge Graph Platform"
    debug: bool = False

    # Database
    mysql_uri: str = "mysql+asyncmy://root:password@localhost:3306/knowledge_graph"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    redis_uri: str = "redis://localhost:6379"

    # Auth
    secret_key: str = "change-this-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Processing
    sync_file_size_limit: int = 5 * 1024 * 1024  # 5MB
    sync_row_limit: int = 10000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

**Step 4: Create main.py**

Create `backend/src/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Step 5: Create __init__.py files**

```bash
touch backend/src/__init__.py
touch backend/src/domain/__init__.py
touch backend/src/domain/entities/__init__.py
touch backend/src/domain/value_objects/__init__.py
touch backend/src/domain/services/__init__.py
touch backend/src/domain/ports/__init__.py
touch backend/src/application/__init__.py
touch backend/src/application/commands/__init__.py
touch backend/src/application/queries/__init__.py
touch backend/src/application/services/__init__.py
touch backend/src/infrastructure/__init__.py
touch backend/src/infrastructure/persistence/__init__.py
touch backend/src/infrastructure/persistence/neo4j/__init__.py
touch backend/src/infrastructure/persistence/mysql/__init__.py
touch backend/src/infrastructure/queue/__init__.py
touch backend/src/infrastructure/storage/__init__.py
touch backend/src/api/__init__.py
touch backend/src/api/routers/__init__.py
touch backend/src/api/schemas/__init__.py
touch backend/src/api/middleware/__init__.py
touch backend/src/api/dependencies/__init__.py
touch backend/tests/__init__.py
```

**Step 6: Verify structure and commit**

```bash
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
# Visit http://localhost:8000/health - expect {"status": "healthy"}
# Visit http://localhost:8000/docs - expect Swagger UI
# Ctrl+C to stop

git add .
git commit -m "feat(backend): scaffold project structure with FastAPI"
```

---

## Task 2: Docker Infrastructure Setup

**Files:**
- Create: `docker/docker-compose.yml`
- Create: `docker/.env.example`

**Step 1: Create docker-compose.yml**

Create `docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: kg-mysql
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: knowledge_graph
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    container_name: kg-neo4j
    environment:
      NEO4J_AUTH: neo4j/password
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: kg-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mysql_data:
  neo4j_data:
  redis_data:
```

**Step 2: Create .env.example**

Create `docker/.env.example`:

```env
# MySQL
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE=knowledge_graph

# Neo4j
NEO4J_AUTH=neo4j/password

# Backend
MYSQL_URI=mysql+asyncmy://root:password@localhost:3306/knowledge_graph
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URI=redis://localhost:6379
SECRET_KEY=change-this-in-production
```

**Step 3: Start infrastructure and verify**

```bash
cd docker
docker-compose up -d
docker-compose ps
# Expected: all 3 services "healthy" or "Up"

# Test MySQL connection
docker exec -it kg-mysql mysql -uroot -ppassword -e "SELECT 1"
# Expected: shows "1"

# Test Neo4j - visit http://localhost:7474 in browser
# Login with neo4j/password

# Test Redis
docker exec -it kg-redis redis-cli ping
# Expected: PONG

git add .
git commit -m "infra: add docker-compose for MySQL, Neo4j, Redis"
```

---

## Task 3: MySQL Database Setup with Alembic

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/src/infrastructure/persistence/mysql/database.py`
- Create: `backend/src/infrastructure/persistence/mysql/models.py`
- Create: `backend/alembic/env.py`

**Step 1: Initialize Alembic**

```bash
cd backend
alembic init alembic
```

**Step 2: Create database.py**

Create `backend/src/infrastructure/persistence/mysql/database.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.mysql_uri,
    echo=settings.debug,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

**Step 3: Create models.py with User and Project models**

Create `backend/src/infrastructure/persistence/mysql/models.py`:

```python
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.mysql.database import Base


def generate_uuid() -> str:
    return str(uuid4())


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    projects: Mapped[list["ProjectModel"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    industry: Mapped[str] = mapped_column(String(20))  # FINANCE, HEALTHCARE
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["UserModel"] = relationship(back_populates="projects")
```

**Step 4: Update alembic/env.py**

Replace `backend/alembic/env.py`:

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config import settings
from src.infrastructure.persistence.mysql.database import Base
from src.infrastructure.persistence.mysql.models import UserModel, ProjectModel  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.mysql_uri)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Step 5: Update alembic.ini**

Edit `backend/alembic.ini`, change line with `sqlalchemy.url`:

```ini
sqlalchemy.url = mysql+asyncmy://root:password@localhost:3306/knowledge_graph
```

**Step 6: Create initial migration**

```bash
cd backend
alembic revision --autogenerate -m "initial_tables"
alembic upgrade head

# Verify tables exist
docker exec -it kg-mysql mysql -uroot -ppassword knowledge_graph -e "SHOW TABLES"
# Expected: users, projects, alembic_version

git add .
git commit -m "feat(db): add MySQL models and Alembic migrations"
```

---

## Task 4: Neo4j Client Setup

**Files:**
- Create: `backend/src/infrastructure/persistence/neo4j/client.py`
- Create: `backend/tests/integration/test_neo4j.py`

**Step 1: Create Neo4j client**

Create `backend/src/infrastructure/persistence/neo4j/client.py`:

```python
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from src.config import settings


class Neo4jClient:
    _driver: AsyncDriver | None = None

    @classmethod
    async def connect(cls) -> None:
        cls._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        # Verify connectivity
        async with cls._driver.session() as session:
            await session.run("RETURN 1")

    @classmethod
    async def disconnect(cls) -> None:
        if cls._driver:
            await cls._driver.close()
            cls._driver = None

    @classmethod
    @asynccontextmanager
    async def session(cls) -> AsyncGenerator[AsyncSession, None]:
        if not cls._driver:
            raise RuntimeError("Neo4j client not connected")
        async with cls._driver.session() as session:
            yield session

    @classmethod
    async def execute_read(
        cls, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        async with cls.session() as session:
            result = await session.run(query, parameters or {})
            return [dict(record) async for record in result]

    @classmethod
    async def execute_write(
        cls, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        async with cls.session() as session:
            result = await session.run(query, parameters or {})
            return [dict(record) async for record in result]
```

**Step 2: Write integration test**

Create `backend/tests/integration/test_neo4j.py`:

```python
import pytest
from src.infrastructure.persistence.neo4j.client import Neo4jClient


@pytest.fixture
async def neo4j_client():
    await Neo4jClient.connect()
    yield Neo4jClient
    await Neo4jClient.disconnect()


@pytest.mark.asyncio
async def test_neo4j_connection(neo4j_client):
    result = await neo4j_client.execute_read("RETURN 1 as value")
    assert result[0]["value"] == 1


@pytest.mark.asyncio
async def test_neo4j_create_and_query_node(neo4j_client):
    # Create test node
    await neo4j_client.execute_write(
        "CREATE (n:TestNode {name: $name}) RETURN n",
        {"name": "test_node"}
    )

    # Query it back
    result = await neo4j_client.execute_read(
        "MATCH (n:TestNode {name: $name}) RETURN n.name as name",
        {"name": "test_node"}
    )
    assert result[0]["name"] == "test_node"

    # Cleanup
    await neo4j_client.execute_write(
        "MATCH (n:TestNode {name: $name}) DELETE n",
        {"name": "test_node"}
    )
```

**Step 3: Run integration test**

```bash
cd backend
pytest tests/integration/test_neo4j.py -v
# Expected: 2 passed

git add .
git commit -m "feat(neo4j): add Neo4j async client with tests"
```

---

## Task 5: Domain Layer - User and Project Entities

**Files:**
- Create: `backend/src/domain/entities/user.py`
- Create: `backend/src/domain/entities/project.py`
- Create: `backend/src/domain/value_objects/industry.py`
- Create: `backend/src/domain/ports/repositories.py`
- Create: `backend/tests/unit/domain/test_entities.py`

**Step 1: Create Industry value object**

Create `backend/src/domain/value_objects/industry.py`:

```python
from enum import Enum


class Industry(str, Enum):
    FINANCE = "FINANCE"
    HEALTHCARE = "HEALTHCARE"
```

**Step 2: Create User entity**

Create `backend/src/domain/entities/user.py`:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def can_manage_project(self, project: "Project") -> bool:
        return self.is_superuser or project.owner_id == self.id
```

**Step 3: Create Project entity**

Create `backend/src/domain/entities/project.py`:

```python
from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.industry import Industry


@dataclass
class Project:
    id: str
    name: str
    industry: Industry
    owner_id: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        if isinstance(self.industry, str):
            self.industry = Industry(self.industry)
```

**Step 4: Create repository ports (interfaces)**

Create `backend/src/domain/ports/repositories.py`:

```python
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User
from src.domain.entities.project import Project


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        pass

    @abstractmethod
    async def list_by_owner(self, owner_id: str) -> list[Project]:
        pass

    @abstractmethod
    async def update(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def delete(self, project_id: str) -> None:
        pass
```

**Step 5: Write unit tests for domain entities**

Create `backend/tests/unit/domain/test_entities.py`:

```python
import pytest
from src.domain.entities.user import User
from src.domain.entities.project import Project
from src.domain.value_objects.industry import Industry


def test_user_can_manage_own_project():
    user = User(
        id="user-1",
        username="testuser",
        email="test@example.com",
        hashed_password="hash",
    )
    project = Project(
        id="proj-1",
        name="My Project",
        industry=Industry.FINANCE,
        owner_id="user-1",
    )

    assert user.can_manage_project(project) is True


def test_user_cannot_manage_other_project():
    user = User(
        id="user-1",
        username="testuser",
        email="test@example.com",
        hashed_password="hash",
    )
    project = Project(
        id="proj-1",
        name="Other Project",
        industry=Industry.FINANCE,
        owner_id="user-2",
    )

    assert user.can_manage_project(project) is False


def test_superuser_can_manage_any_project():
    superuser = User(
        id="admin-1",
        username="admin",
        email="admin@example.com",
        hashed_password="hash",
        is_superuser=True,
    )
    project = Project(
        id="proj-1",
        name="Other Project",
        industry=Industry.HEALTHCARE,
        owner_id="user-2",
    )

    assert superuser.can_manage_project(project) is True


def test_project_industry_string_conversion():
    project = Project(
        id="proj-1",
        name="Test",
        industry="FINANCE",  # string, not enum
        owner_id="user-1",
    )

    assert project.industry == Industry.FINANCE
    assert isinstance(project.industry, Industry)
```

**Step 6: Run tests and commit**

```bash
cd backend
pytest tests/unit/domain/test_entities.py -v
# Expected: 4 passed

git add .
git commit -m "feat(domain): add User, Project entities and repository ports"
```

---

## Task 6: Infrastructure - Repository Implementations

**Files:**
- Create: `backend/src/infrastructure/persistence/mysql/user_repository.py`
- Create: `backend/src/infrastructure/persistence/mysql/project_repository.py`
- Create: `backend/tests/integration/test_repositories.py`

**Step 1: Create UserRepository implementation**

Create `backend/src/infrastructure/persistence/mysql/user_repository.py`:

```python
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.ports.repositories import UserRepository
from src.infrastructure.persistence.mysql.models import UserModel


class MySQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            email=entity.email,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
```

**Step 2: Create ProjectRepository implementation**

Create `backend/src/infrastructure/persistence/mysql/project_repository.py`:

```python
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project import Project
from src.domain.ports.repositories import ProjectRepository
from src.infrastructure.persistence.mysql.models import ProjectModel


class MySQLProjectRepository(ProjectRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            industry=model.industry,
            owner_id=model.owner_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            industry=entity.industry.value if hasattr(entity.industry, 'value') else entity.industry,
            owner_id=entity.owner_id,
        )

    async def create(self, project: Project) -> Project:
        model = self._to_model(project)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_owner(self, owner_id: str) -> list[Project]:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.owner_id == owner_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, project: Project) -> Project:
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.name = project.name
            model.description = project.description
            model.industry = project.industry.value if hasattr(project.industry, 'value') else project.industry
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Project {project.id} not found")

    async def delete(self, project_id: str) -> None:
        await self.session.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )
        await self.session.commit()
```

**Step 3: Write integration tests**

Create `backend/tests/integration/test_repositories.py`:

```python
import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.entities.project import Project
from src.domain.value_objects.industry import Industry
from src.infrastructure.persistence.mysql.database import async_session_maker
from src.infrastructure.persistence.mysql.user_repository import MySQLUserRepository
from src.infrastructure.persistence.mysql.project_repository import MySQLProjectRepository


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
    project_repo: MySQLProjectRepository
):
    # Create user first
    user = User(
        id=str(uuid4()),
        username=f"projowner_{uuid4().hex[:8]}",
        email=f"owner_{uuid4().hex[:8]}@example.com",
        hashed_password="hashedpwd",
    )
    await user_repo.create(user)

    # Create projects
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

    # List projects
    projects = await project_repo.list_by_owner(user.id)
    assert len(projects) == 2
    names = {p.name for p in projects}
    assert "Finance Project" in names
    assert "Healthcare Project" in names
```

**Step 4: Run tests and commit**

```bash
cd backend
pytest tests/integration/test_repositories.py -v
# Expected: 2 passed

git add .
git commit -m "feat(infra): implement MySQL repositories for User and Project"
```

---

## Task 7: Authentication System

**Files:**
- Create: `backend/src/domain/services/auth_service.py`
- Create: `backend/src/api/schemas/auth.py`
- Create: `backend/src/api/routers/auth.py`
- Create: `backend/src/api/dependencies/auth.py`
- Create: `backend/tests/unit/domain/test_auth_service.py`

**Step 1: Create auth service in domain**

Create `backend/src/domain/services/auth_service.py`:

```python
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config import settings
from src.domain.entities.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode = {
            "sub": user_id,
            "exp": expire,
        }
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def decode_access_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
```

**Step 2: Create auth schemas**

Create `backend/src/api/schemas/auth.py`:

```python
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True
```

**Step 3: Create auth dependencies**

Create `backend/src/api/dependencies/auth.py`:

```python
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.services.auth_service import AuthService
from src.infrastructure.persistence.mysql.database import get_db
from src.infrastructure.persistence.mysql.user_repository import MySQLUserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = AuthService.decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user_repo = MySQLUserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
```

**Step 4: Create auth router**

Create `backend/src/api/routers/auth.py`:

```python
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.services.auth_service import AuthService
from src.infrastructure.persistence.mysql.database import get_db
from src.infrastructure.persistence.mysql.user_repository import MySQLUserRepository
from src.api.schemas.auth import UserCreate, Token, UserResponse
from src.api.dependencies.auth import get_current_user


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = MySQLUserRepository(db)

    # Check if username exists
    existing = await user_repo.get_by_username(user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    existing = await user_repo.get_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        id=str(uuid4()),
        username=user_data.username,
        email=user_data.email,
        hashed_password=AuthService.hash_password(user_data.password),
    )
    created = await user_repo.create(user)
    return created


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_repo = MySQLUserRepository(db)
    user = await user_repo.get_by_username(form_data.username)

    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
```

**Step 5: Write unit tests for auth service**

Create `backend/tests/unit/domain/test_auth_service.py`:

```python
import pytest
from datetime import timedelta
from src.domain.services.auth_service import AuthService


def test_hash_and_verify_password():
    password = "mysecretpassword"
    hashed = AuthService.hash_password(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed) is True
    assert AuthService.verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    user_id = "user-123"
    token = AuthService.create_access_token(user_id)

    decoded_id = AuthService.decode_access_token(token)
    assert decoded_id == user_id


def test_decode_invalid_token():
    decoded = AuthService.decode_access_token("invalid.token.here")
    assert decoded is None


def test_token_expiration():
    user_id = "user-123"
    # Create token that expires immediately (negative delta)
    token = AuthService.create_access_token(user_id, expires_delta=timedelta(seconds=-1))

    decoded = AuthService.decode_access_token(token)
    assert decoded is None  # Expired token should return None
```

**Step 6: Update main.py to include router**

Update `backend/src/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Step 7: Run tests and verify API**

```bash
cd backend
pytest tests/unit/domain/test_auth_service.py -v
# Expected: 4 passed

# Start server and test manually
uvicorn src.main:app --reload --port 8000
# Visit http://localhost:8000/docs
# Test POST /api/auth/register with body:
# {"username": "testuser", "email": "test@example.com", "password": "testpass123"}
# Expected: 201 Created with user response

# Test POST /api/auth/login (use form data, not JSON):
# username=testuser, password=testpass123
# Expected: {"access_token": "...", "token_type": "bearer"}

git add .
git commit -m "feat(auth): implement JWT authentication with register/login"
```

---

## Task 8: Project CRUD API

**Files:**
- Create: `backend/src/api/schemas/project.py`
- Create: `backend/src/api/routers/projects.py`
- Create: `backend/tests/e2e/test_projects_api.py`

**Step 1: Create project schemas**

Create `backend/src/api/schemas/project.py`:

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.value_objects.industry import Industry


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Industry


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[Industry] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    industry: Industry
    owner_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
```

**Step 2: Create projects router**

Create `backend/src/api/routers/projects.py`:

```python
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.entities.project import Project
from src.domain.value_objects.industry import Industry
from src.infrastructure.persistence.mysql.database import get_db
from src.infrastructure.persistence.mysql.project_repository import MySQLProjectRepository
from src.api.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from src.api.dependencies.auth import get_current_user


router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_repo = MySQLProjectRepository(db)

    project = Project(
        id=str(uuid4()),
        name=project_data.name,
        description=project_data.description,
        industry=project_data.industry,
        owner_id=current_user.id,
    )

    created = await project_repo.create(project)
    return created


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_repo = MySQLProjectRepository(db)
    projects = await project_repo.list_by_owner(current_user.id)

    return ProjectListResponse(
        items=projects,
        total=len(projects),
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_repo = MySQLProjectRepository(db)
    project = await project_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not current_user.can_manage_project(project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )

    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_repo = MySQLProjectRepository(db)
    project = await project_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not current_user.can_manage_project(project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this project",
        )

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.industry is not None:
        project.industry = project_data.industry

    updated = await project_repo.update(project)
    return updated


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project_repo = MySQLProjectRepository(db)
    project = await project_repo.get_by_id(project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if not current_user.can_manage_project(project):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project",
        )

    await project_repo.delete(project_id)
```

**Step 3: Update main.py to include projects router**

Update `backend/src/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.routers import auth, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(projects.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Step 4: Write E2E tests**

Create `backend/tests/e2e/test_projects_api.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4

from src.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient):
    # Register a test user
    username = f"testuser_{uuid4().hex[:8]}"
    await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpass123",
        },
    )

    # Login to get token
    response = await client.post(
        "/api/auth/login",
        data={"username": username, "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers: dict):
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
    # Create two projects
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

    # List projects
    response = await client.get("/api/projects", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, auth_headers: dict):
    # Create a project
    create_response = await client.post(
        "/api/projects",
        json={"name": "Get Test Project", "industry": "HEALTHCARE"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    # Get the project
    response = await client.get(f"/api/projects/{project_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Get Test Project"


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, auth_headers: dict):
    # Create a project
    create_response = await client.post(
        "/api/projects",
        json={"name": "Update Test", "industry": "FINANCE"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    # Update it
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
    # Create a project
    create_response = await client.post(
        "/api/projects",
        json={"name": "Delete Test", "industry": "FINANCE"},
        headers=auth_headers,
    )
    project_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(f"/api/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/projects")
    assert response.status_code == 401
```

**Step 5: Run E2E tests and commit**

```bash
cd backend
pytest tests/e2e/test_projects_api.py -v
# Expected: 6 passed

git add .
git commit -m "feat(api): implement project CRUD endpoints with E2E tests"
```

---

## Task 9: Frontend Project Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`

**Step 1: Initialize frontend project**

```bash
cd ..  # back to project root
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install -D @types/node
```

**Step 2: Install dependencies**

```bash
npm install vue-router@4 pinia @vueuse/core axios element-plus @element-plus/icons-vue
npm install -D unplugin-auto-import unplugin-vue-components sass
```

**Step 3: Update vite.config.ts**

Replace `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

**Step 4: Update tsconfig.json**

Replace `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 5: Create directory structure**

```bash
mkdir -p src/{api,assets,components/{common,graph,extraction,query},composables,layouts,pages/{auth,projects,system},router,stores,types,utils}
```

**Step 6: Create types**

Create `frontend/src/types/index.ts`:

```typescript
export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  is_superuser: boolean
}

export interface Project {
  id: string
  name: string
  description?: string
  industry: 'FINANCE' | 'HEALTHCARE'
  owner_id: string
  created_at?: string
  updated_at?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface ProjectCreate {
  name: string
  description?: string
  industry: 'FINANCE' | 'HEALTHCARE'
}

export interface ProjectUpdate {
  name?: string
  description?: string
  industry?: 'FINANCE' | 'HEALTHCARE'
}

export interface ProjectListResponse {
  items: Project[]
  total: number
}
```

**Step 7: Verify frontend builds**

```bash
cd frontend
npm run build
# Expected: no errors, dist folder created

npm run dev
# Visit http://localhost:3000 - expect Vite + Vue default page

git add .
git commit -m "feat(frontend): scaffold Vue 3 + Vite + TypeScript project"
```

---

## Task 10: Frontend API Client and Stores

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/projects.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/stores/project.ts`

**Step 1: Create API client**

Create `frontend/src/api/client.ts`:

```typescript
import axios, { AxiosError, type AxiosInstance } from 'axios'

const client: AxiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle 401
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default client
```

**Step 2: Create auth API**

Create `frontend/src/api/auth.ts`:

```typescript
import client from './client'
import type { User, LoginRequest, RegisterRequest, TokenResponse } from '@/types'

export const authApi = {
  async register(data: RegisterRequest): Promise<User> {
    const response = await client.post<User>('/auth/register', data)
    return response.data
  },

  async login(data: LoginRequest): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await client.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  async getMe(): Promise<User> {
    const response = await client.get<User>('/auth/me')
    return response.data
  },
}
```

**Step 3: Create projects API**

Create `frontend/src/api/projects.ts`:

```typescript
import client from './client'
import type { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '@/types'

export const projectsApi = {
  async create(data: ProjectCreate): Promise<Project> {
    const response = await client.post<Project>('/projects', data)
    return response.data
  },

  async list(): Promise<ProjectListResponse> {
    const response = await client.get<ProjectListResponse>('/projects')
    return response.data
  },

  async get(id: string): Promise<Project> {
    const response = await client.get<Project>(`/projects/${id}`)
    return response.data
  },

  async update(id: string, data: ProjectUpdate): Promise<Project> {
    const response = await client.patch<Project>(`/projects/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await client.delete(`/projects/${id}`)
  },
}
```

**Step 4: Create auth store**

Create `frontend/src/stores/auth.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  async function register(data: RegisterRequest): Promise<User> {
    const newUser = await authApi.register(data)
    return newUser
  }

  async function login(data: LoginRequest): Promise<void> {
    const response = await authApi.login(data)
    token.value = response.access_token
    localStorage.setItem('access_token', response.access_token)
    await fetchUser()
  }

  async function fetchUser(): Promise<void> {
    if (!token.value) return
    try {
      user.value = await authApi.getMe()
    } catch {
      logout()
    }
  }

  function logout(): void {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    isSuperuser,
    register,
    login,
    fetchUser,
    logout,
  }
})
```

**Step 5: Create project store**

Create `frontend/src/stores/project.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types'
import { projectsApi } from '@/api/projects'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProjects(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await projectsApi.list()
      projects.value = response.items
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch projects'
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentProject.value = await projectsApi.get(id)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch project'
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: ProjectCreate): Promise<Project> {
    loading.value = true
    error.value = null
    try {
      const project = await projectsApi.create(data)
      projects.value.push(project)
      return project
    } catch (e: any) {
      error.value = e.message || 'Failed to create project'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateProject(id: string, data: ProjectUpdate): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await projectsApi.update(id, data)
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        projects.value[index] = updated
      }
      if (currentProject.value?.id === id) {
        currentProject.value = updated
      }
    } catch (e: any) {
      error.value = e.message || 'Failed to update project'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteProject(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await projectsApi.delete(id)
      projects.value = projects.value.filter((p) => p.id !== id)
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } catch (e: any) {
      error.value = e.message || 'Failed to delete project'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    currentProject,
    loading,
    error,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
  }
})
```

**Step 6: Commit**

```bash
cd frontend
git add .
git commit -m "feat(frontend): add API client, auth store, and project store"
```

---

## Task 11: Frontend Router and Auth Pages

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/pages/auth/Login.vue`
- Create: `frontend/src/pages/auth/Register.vue`
- Create: `frontend/src/layouts/DefaultLayout.vue`
- Update: `frontend/src/App.vue`
- Update: `frontend/src/main.ts`

**Step 1: Create router**

Create `frontend/src/router/index.ts`:

```typescript
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/pages/projects/ProjectList.vue'),
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/pages/projects/ProjectDetail.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Try to fetch user if we have a token but no user
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
```

**Step 2: Create Login page**

Create `frontend/src/pages/auth/Login.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
})
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(form.value)
    ElMessage.success('Login successful')
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>Knowledge Graph Platform</h2>
      </template>

      <el-form
        :model="form"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="Username">
          <el-input v-model="form.username" placeholder="Enter username" />
        </el-form-item>

        <el-form-item label="Password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="Enter password"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            style="width: 100%"
          >
            Login
          </el-button>
        </el-form-item>

        <div class="login-links">
          <router-link to="/register">Don't have an account? Register</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.login-card {
  width: 400px;

  h2 {
    margin: 0;
    text-align: center;
  }
}

.login-links {
  text-align: center;
  margin-top: 16px;

  a {
    color: #409eff;
    text-decoration: none;
  }
}
</style>
```

**Step 3: Create Register page**

Create `frontend/src/pages/auth/Register.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})
const loading = ref(false)

async function handleRegister() {
  if (form.value.password !== form.value.confirmPassword) {
    ElMessage.error('Passwords do not match')
    return
  }

  loading.value = true
  try {
    await authStore.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
    })
    ElMessage.success('Registration successful! Please login.')
    router.push('/login')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>Create Account</h2>
      </template>

      <el-form
        :model="form"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="Username">
          <el-input v-model="form.username" placeholder="Choose a username" />
        </el-form-item>

        <el-form-item label="Email">
          <el-input v-model="form.email" type="email" placeholder="Enter email" />
        </el-form-item>

        <el-form-item label="Password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="Create password"
            show-password
          />
        </el-form-item>

        <el-form-item label="Confirm Password">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="Confirm password"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            style="width: 100%"
          >
            Register
          </el-button>
        </el-form-item>

        <div class="register-links">
          <router-link to="/login">Already have an account? Login</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.register-card {
  width: 400px;

  h2 {
    margin: 0;
    text-align: center;
  }
}

.register-links {
  text-align: center;
  margin-top: 16px;

  a {
    color: #409eff;
    text-decoration: none;
  }
}
</style>
```

**Step 4: Create DefaultLayout**

Create `frontend/src/layouts/DefaultLayout.vue`:

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <el-header class="layout-header">
      <div class="header-left">
        <router-link to="/" class="logo">Knowledge Graph Platform</router-link>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click">
          <span class="user-dropdown">
            {{ authStore.user?.username }}
            <el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">Logout</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container>
      <el-aside width="200px" class="layout-aside">
        <el-menu
          router
          :default-active="$route.path"
        >
          <el-menu-item index="/">
            <el-icon><home-filled /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="/projects">
            <el-icon><folder /></el-icon>
            <span>Projects</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped lang="scss">
.layout-container {
  min-height: 100vh;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #001529;
  color: white;
  padding: 0 24px;
}

.header-left .logo {
  color: white;
  text-decoration: none;
  font-size: 18px;
  font-weight: bold;
}

.user-dropdown {
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.layout-aside {
  background: #fff;
  border-right: 1px solid #e6e6e6;
}

.layout-main {
  background: #f5f7fa;
  padding: 24px;
}
</style>
```

**Step 5: Create Dashboard page**

Create `frontend/src/pages/Dashboard.vue`:

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'

const authStore = useAuthStore()
const projectStore = useProjectStore()

onMounted(() => {
  projectStore.fetchProjects()
})
</script>

<template>
  <div class="dashboard">
    <h1>Welcome, {{ authStore.user?.username }}!</h1>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>Projects</template>
          <div class="stat-value">{{ projectStore.projects.length }}</div>
          <router-link to="/projects">View all projects →</router-link>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.dashboard h1 {
  margin-bottom: 24px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}
</style>
```

**Step 6: Update main.ts**

Replace `frontend/src/main.ts`:

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// Register all Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

**Step 7: Update App.vue**

Replace `frontend/src/App.vue`:

```vue
<template>
  <router-view />
</template>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
```

**Step 8: Verify and commit**

```bash
cd frontend
npm run dev
# Visit http://localhost:3000 - should redirect to /login
# Create account, login, see dashboard

git add .
git commit -m "feat(frontend): add router, auth pages, and layout"
```

---

## Task 12: Frontend Project Pages

**Files:**
- Create: `frontend/src/pages/projects/ProjectList.vue`
- Create: `frontend/src/pages/projects/ProjectDetail.vue`
- Create: `frontend/src/components/projects/CreateProjectDialog.vue`

**Step 1: Create CreateProjectDialog component**

Create `frontend/src/components/projects/CreateProjectDialog.vue`:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import type { ProjectCreate } from '@/types'

const emit = defineEmits<{
  (e: 'created'): void
}>()

const projectStore = useProjectStore()

const visible = ref(false)
const form = ref<ProjectCreate>({
  name: '',
  description: '',
  industry: 'FINANCE',
})

function show() {
  visible.value = true
  form.value = {
    name: '',
    description: '',
    industry: 'FINANCE',
  }
}

async function handleCreate() {
  try {
    await projectStore.createProject(form.value)
    ElMessage.success('Project created successfully')
    visible.value = false
    emit('created')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'Failed to create project')
  }
}

defineExpose({ show })
</script>

<template>
  <el-dialog v-model="visible" title="Create New Project" width="500px">
    <el-form :model="form" label-position="top">
      <el-form-item label="Project Name" required>
        <el-input v-model="form.name" placeholder="Enter project name" />
      </el-form-item>

      <el-form-item label="Description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="Enter project description"
        />
      </el-form-item>

      <el-form-item label="Industry" required>
        <el-select v-model="form.industry" style="width: 100%">
          <el-option label="Finance" value="FINANCE" />
          <el-option label="Healthcare" value="HEALTHCARE" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">Cancel</el-button>
      <el-button
        type="primary"
        :loading="projectStore.loading"
        @click="handleCreate"
      >
        Create
      </el-button>
    </template>
  </el-dialog>
</template>
```

**Step 2: Create ProjectList page**

Create `frontend/src/pages/projects/ProjectList.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import CreateProjectDialog from '@/components/projects/CreateProjectDialog.vue'

const router = useRouter()
const projectStore = useProjectStore()
const createDialog = ref<InstanceType<typeof CreateProjectDialog>>()

onMounted(() => {
  projectStore.fetchProjects()
})

function handleCreate() {
  createDialog.value?.show()
}

function handleView(id: string) {
  router.push(`/projects/${id}`)
}

async function handleDelete(id: string, name: string) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete project "${name}"?`,
      'Delete Project',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )

    await projectStore.deleteProject(id)
    ElMessage.success('Project deleted successfully')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || 'Failed to delete project')
    }
  }
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="project-list">
    <div class="page-header">
      <h1>Projects</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><plus /></el-icon>
        Create Project
      </el-button>
    </div>

    <el-table
      v-loading="projectStore.loading"
      :data="projectStore.projects"
      style="width: 100%"
    >
      <el-table-column prop="name" label="Name" min-width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="handleView(row.id)">
            {{ row.name }}
          </el-link>
        </template>
      </el-table-column>

      <el-table-column prop="industry" label="Industry" width="120">
        <template #default="{ row }">
          <el-tag :type="row.industry === 'FINANCE' ? 'warning' : 'success'">
            {{ row.industry }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="description" label="Description" min-width="200" />

      <el-table-column prop="created_at" label="Created" width="120">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row.id)">View</el-button>
          <el-button
            size="small"
            type="danger"
            @click="handleDelete(row.id, row.name)"
          >
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <CreateProjectDialog ref="createDialog" @created="projectStore.fetchProjects" />
  </div>
</template>

<style scoped lang="scss">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    margin: 0;
  }
}
</style>
```

**Step 3: Create ProjectDetail page**

Create `frontend/src/pages/projects/ProjectDetail.vue`:

```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import type { ProjectUpdate } from '@/types'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const editing = ref(false)
const editForm = ref<ProjectUpdate>({})

onMounted(() => {
  const id = route.params.id as string
  projectStore.fetchProject(id)
})

function startEdit() {
  if (projectStore.currentProject) {
    editForm.value = {
      name: projectStore.currentProject.name,
      description: projectStore.currentProject.description,
      industry: projectStore.currentProject.industry,
    }
    editing.value = true
  }
}

async function saveEdit() {
  const id = route.params.id as string
  try {
    await projectStore.updateProject(id, editForm.value)
    ElMessage.success('Project updated successfully')
    editing.value = false
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'Failed to update project')
  }
}

function cancelEdit() {
  editing.value = false
}
</script>

<template>
  <div v-loading="projectStore.loading" class="project-detail">
    <div class="page-header">
      <el-button @click="router.push('/projects')">
        <el-icon><arrow-left /></el-icon>
        Back to Projects
      </el-button>
    </div>

    <el-card v-if="projectStore.currentProject">
      <template #header>
        <div class="card-header">
          <span v-if="!editing">{{ projectStore.currentProject.name }}</span>
          <el-input v-else v-model="editForm.name" style="width: 300px" />

          <div class="card-actions">
            <template v-if="!editing">
              <el-button type="primary" @click="startEdit">Edit</el-button>
            </template>
            <template v-else>
              <el-button @click="cancelEdit">Cancel</el-button>
              <el-button type="primary" @click="saveEdit">Save</el-button>
            </template>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="Industry">
          <template v-if="!editing">
            <el-tag :type="projectStore.currentProject.industry === 'FINANCE' ? 'warning' : 'success'">
              {{ projectStore.currentProject.industry }}
            </el-tag>
          </template>
          <template v-else>
            <el-select v-model="editForm.industry">
              <el-option label="Finance" value="FINANCE" />
              <el-option label="Healthcare" value="HEALTHCARE" />
            </el-select>
          </template>
        </el-descriptions-item>

        <el-descriptions-item label="Created">
          {{ projectStore.currentProject.created_at }}
        </el-descriptions-item>

        <el-descriptions-item label="Description" :span="2">
          <template v-if="!editing">
            {{ projectStore.currentProject.description || '-' }}
          </template>
          <template v-else>
            <el-input
              v-model="editForm.description"
              type="textarea"
              :rows="3"
            />
          </template>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>Graph Data</h3>
      <el-empty description="No graph data yet. Start by importing data." />
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.page-header {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
```

**Step 4: Verify everything works end-to-end**

```bash
# Ensure Docker services are running
cd docker && docker-compose up -d

# Start backend
cd ../backend
uvicorn src.main:app --reload --port 8000

# In another terminal, start frontend
cd frontend
npm run dev

# Visit http://localhost:3000
# 1. Register a new account
# 2. Login
# 3. Go to Projects page
# 4. Create a new project (Finance or Healthcare)
# 5. View project details
# 6. Edit project
# 7. Delete project

git add .
git commit -m "feat(frontend): implement project CRUD pages"
```

---

## Task 13: Final Integration Test

**Step 1: Run all tests**

```bash
cd backend
pytest tests/ -v --tb=short
# Expected: all tests passing

cd ../frontend
npm run build
# Expected: no errors
```

**Step 2: Final commit**

```bash
cd ..
git add .
git commit -m "chore: complete Phase 1 - foundation with auth and project CRUD"
```

---

## Summary

Phase 1 is complete. You now have:

- **Backend**: FastAPI with Hexagonal architecture, MySQL + Neo4j connections, JWT auth, Project CRUD
- **Frontend**: Vue 3 + Pinia + Element Plus, auth flow, project management pages
- **Infrastructure**: Docker Compose for MySQL, Neo4j, Redis
- **Tests**: Unit tests for domain, integration tests for repositories, E2E tests for API

**Next Phase** would add:
- Data ingestion and preprocessing
- Knowledge extraction (NLP)
- Graph visualization
- Industry-specific modules
