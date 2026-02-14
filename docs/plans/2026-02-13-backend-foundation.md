# 2026-02-13-backend-foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver the core graph backend foundation¡ªdomain models, repositories, services, and minimal API routes for graph projects/entities per the architecture doc.

**Architecture:** Implement graph domain entities/value objects in the domain layer, back them with MySQL (graph projects) and Neo4j (entities/relations) repositories via hexagonal ports, then expose application services and FastAPI routes. Follow TDD via unit + integration suites using PyTest and Testcontainers.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Alembic, Neo4j driver, PyTest, Testcontainers, Redis (for existing infra).

---

### Task 1: Domain Entities & Value Objects

**Files:**
- Create: ackend/src/domain/entities/graph_project.py
- Create: ackend/src/domain/entities/entity.py
- Create: ackend/src/domain/entities/relation.py
- Create: ackend/src/domain/value_objects/entity_type.py
- Create: ackend/src/domain/value_objects/relation_type.py
- Modify: ackend/src/domain/ports/repositories.py
- Test: ackend/tests/unit/domain/test_graph_domain.py

**Step 1: Write failing tests**
`python
# backend/tests/unit/domain/test_graph_domain.py
# GraphProject adds entities, relations require project-owned nodes, self-loops invalid
`
Run: cd backend && pytest tests/unit/domain/test_graph_domain.py -v ¡ú FAIL.

**Step 2: Implement domain classes**
- dataclass implementations with validation & metadata tracking.
- Update repository ports (GraphProjectRepository, GraphEntityRepository).

**Step 3: Re-run tests**
cd backend && pytest tests/unit/domain/test_graph_domain.py -v
Expected: PASS.

**Step 4: Commit**
git add backend/src/domain backend/tests/unit/domain/test_graph_domain.py
git commit -m "feat(domain): add core graph entities"

---

### Task 2: MySQL Graph Project Repository & Migration

**Files:**
- Modify: ackend/src/infrastructure/persistence/mysql/models.py
- Create: ackend/src/infrastructure/persistence/mysql/repositories/graph_project_repository.py
- Modify: ackend/src/infrastructure/persistence/mysql/database.py
- Create: ackend/alembic/versions/20260213_add_graph_projects.py
- Test: ackend/tests/integration/persistence/test_graph_project_repository.py

**Step 1: Write failing integration tests**
`python
@pytest.mark.asyncio
async def test_create_and_fetch_graph_project(graph_project_repo): ...
`
Run: cd backend && pytest tests/integration/persistence/test_graph_project_repository.py -v ¡ú FAIL.

**Step 2: Implement SQLAlchemy model/repo**
- Add graph_projects table (UUID PK, owner_id FK, status, metadata JSON).
- Repository CRUD + list_by_owner.

**Step 3: Run migration/tests**
`
cd backend
alembic upgrade head
pytest tests/integration/persistence/test_graph_project_repository.py -v
`
Expected: PASS.

**Step 4: Commit**
git add backend/src/infrastructure/persistence/mysql backend/alembic/versions backend/tests/integration/persistence/test_graph_project_repository.py
git commit -m "feat(persistence): add graph project repository"

---

### Task 3: Neo4j Entity/Relation Repository

**Files:**
- Create: ackend/src/infrastructure/persistence/neo4j/graph_repository.py
- Modify: ackend/src/infrastructure/persistence/neo4j/__init__.py
- Modify: ackend/src/domain/ports/repositories.py
- Test: ackend/tests/integration/persistence/test_graph_repository.py

**Step 1: Write failing tests**
`python
@pytest.mark.asyncio
def test_merge_entities_and_relations(neo4j_repo): ...
`
Run: cd backend && pytest tests/integration/persistence/test_graph_repository.py -v ¡ú FAIL.

**Step 2: Implement repo**
- Wrap Neo4j async driver, methods merge_entity, merge_relation, delete, find_neighbors.
- Enforce project scoping, decode node properties.

**Step 3: Re-run tests**
cd backend && pytest tests/integration/persistence/test_graph_repository.py -v
Expected: PASS.

**Step 4: Commit**
git add backend/src/infrastructure/persistence/neo4j backend/tests/integration/persistence/test_graph_repository.py
git commit -m "feat(persistence): add neo4j graph repository"

---

### Task 4: Application Service & FastAPI Endpoints

**Files:**
- Create: ackend/src/application/services/graph_service.py
- Create: ackend/src/application/commands/create_project.py
- Create: ackend/src/application/commands/create_entity.py
- Create: ackend/src/application/commands/create_relation.py
- Modify/Create: ackend/src/api/schemas/project.py, ackend/src/api/schemas/graph.py
- Create/Modify: ackend/src/api/routers/projects.py, ackend/src/api/routers/graph.py
- Test: ackend/tests/unit/application/test_graph_service.py, ackend/tests/integration/api/test_graph_routes.py

**Step 1: Write failing unit tests**
`python
async def test_create_project(graph_service): ...
`
cd backend && pytest tests/unit/application/test_graph_service.py -v ¡ú FAIL.

**Step 2: Implement service/commands**
- GraphService orchestrates repository usage.

**Step 3: Implement FastAPI routes + schemas**
- POST /projects, GET /projects/{id}
- POST /graph/entities, POST /graph/relations, GET /graph/projects/{id}/neighbors

**Step 4: Integration API tests**
cd backend && pytest tests/integration/api/test_graph_routes.py -v
Expected: PASS.

**Step 5: Commit**
git add backend/src/application backend/src/api backend/tests/unit/application backend/tests/integration/api/test_graph_routes.py
git commit -m "feat(api): add graph project and entity routes"

---

### Task 5: Verification & Documentation

**Files:**
- Modify: README.md
- Modify: docs/plans/2026-02-09-architecture-design.md
- Optional: docs/runbooks/backend-graph.md

**Step 1: Run full backend tests**
`
cd backend
pytest tests/unit -v
pytest tests/integration -v
`

**Step 2: Update docs**
- README: mention core graph APIs + dev setup.
- Architecture plan: mark backend foundation progress.

**Step 3: Commit**
git add README.md docs/plans/2026-02-09-architecture-design.md docs/runbooks/backend-graph.md
git commit -m "docs: document backend graph foundation"

---

Plan complete and saved. Execution options:
1. **Subagent-Driven** (this session, already chosen)
2. **Parallel Session** (new session w/ executing-plans)
