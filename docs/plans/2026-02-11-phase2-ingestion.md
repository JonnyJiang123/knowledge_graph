# Phase 2 - Data Ingestion & Preprocessing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.  
> **Save to:** `docs/plans/2026-02-11-phase2-ingestion.md`

**Goal:** Deliver the ingestion & preprocessing slice: accept file/MySQL sources, apply configurable cleaning rules, preview results, and kick off hybrid sync/async processing tied to projects.

**Architecture:** Extend the existing hexagonal backend with ingestion domain entities, repositories, and Celery tasks; store raw/clean artifacts on disk with metadata in MySQL; expose FastAPI routers plus Vue wizard pages powered by new Pinia stores; reuse Redis/Celery for async jobs and Element Plus for workflow UI.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Alembic, Celery, Redis, pandas, aiofiles, PyPDF2, python-docx, Cryptography/Fernet, Vue 3, Pinia, Element Plus, Vite, Vitest.

---

## Summary
- Model ingestion primitives (data sources, uploads, jobs, cleaning rules) in the domain and relational schema so every project can manage multiple artifacts.
- Provide storage + parsing adapters for CSV/Excel/TXT/PDF/Word files and a MySQL connector, generating profiles, sample rows, and cleaning rule applications.
- Build FastAPI endpoints for source management, uploads, previews, and job status with hybrid sync (≤5 MB or ≤10 k rows) vs async (Celery) execution.
- Ship a front-end ingestion wizard (source selection → field mapping → cleaning rules → preview → submit) plus job list/progress UI, tied to new API clients/stores.
- Update infrastructure (Docker, config, scripts) and add backend/frontend automated tests plus manual verification steps.

## API / Interface Changes
- **New REST endpoints (`/ingestion/...`)**: source CRUD/test, file upload, preview, job status/logs.
- **Domain interfaces**: `DataSourceRepository`, `IngestionJobRepository`, `FileStoragePort`, `PreviewCachePort`, `TaskQueuePort`.
- **Celery tasks**: `ingestion.run_async_job` for large workloads, `ingestion.refresh_preview`.
- **DB schema**: tables `data_sources`, `upload_artifacts`, `cleaning_rules`, `ingestion_jobs`.
- **Front-end routes/components**: `/ingestion/wizard`, `/ingestion/jobs`, ingestion Pinia store and Element Plus wizard components.
- **Config/env**: `UPLOAD_BASE_DIR`, `TMP_DIR`, `ENCRYPTION_KEY`, `PREVIEW_ROW_LIMIT`.

## Test Matrix
- Backend unit tests for ingestion domain entities, cleaning rule evaluation, ingestion service business logic.
- Backend integration tests covering repository CRUD, file storage adapter, file upload API (httpx) with sync + async job paths.
- Celery task tests using `celery_app.conf.task_always_eager=True`.
- Frontend unit tests (Vitest + Vue Test Utils) for wizard components and Pinia ingestion store actions.
- Manual QA checklist: upload small/large files, configure MySQL source, apply cleaning rules, monitor job progress, ensure artifacts stored and statuses update.

## Assumptions
- Raw files and cleaned exports live under `storage/uploads/<project_id>/...`; this directory is writable on all dev/prod nodes and mounted in Docker.
- Only CSV, Excel (`.xlsx`), TXT, PDF, Word, and MySQL table imports are in-scope for Phase 2; other DBs/APIs deferred.
- Sensitive connector credentials are encrypted with Fernet using `settings.encryption_key` before saving in MySQL.
- Redis already runs (from Phase 1) and is reused for Celery broker/result backend plus preview cache entries (store JSON snapshots for 15 minutes).
- Frontend testing stack will use Vitest; no Cypress/E2E automation in this phase.

---

### Task 1: Backend Dependencies & Configuration Baseline
**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/src/config.py`
- Create: `backend/src/settings_types.py` (optional helper)
- Modify: `docker/.env.example`, `docker/docker-compose.yml`
- Modify: `backend/.env.example` (if present)

**Step 1: Update dependencies**
```toml
[project]
dependencies = [
  # existing …
  "pandas>=2.2.0",
  "openpyxl>=3.1.2",
  "python-docx>=1.0.0",
  "pypdf2>=3.0.1",
  "aiofiles>=24.1.0",
  "cryptography>=43.0.0",
  "sqlalchemy-utils>=0.41.2"
]

[project.optional-dependencies.dev]
dev = [
  # existing …
  "pytest-mock>=3.12.0",
  "pytest-celery>=1.0.0"
]
```
Run: `cd backend && pip install -e ".[dev]"`. Expected: succeeds.

**Step 2: Extend config**
Add to `Settings`:
```python
from pathlib import Path
from cryptography.fernet import Fernet

class Settings(BaseSettings):
    upload_base_dir: Path = Path("storage/uploads")
    temp_dir: Path = Path("storage/tmp")
    preview_row_limit: int = 50
    encryption_key: str = "generate-with-fernet"
```
Ensure directories are created at startup via `Settings` property or application lifespan.

**Step 3: Document env vars**
Update `.env.example` / `docker/.env.example` with the new keys and comments (paths relative to repo, Fernet key instructions).

**Step 4: Docker volume**
In `docker/docker-compose.yml`, mount a named volume to `/app/storage/uploads` for backend + worker services, and expose `UPLOAD_BASE_DIR=/app/storage/uploads`.

**Step 5: Smoke test config**
Run `cd backend && pytest tests/unit/domain/test_entities.py -v` to ensure existing suites still pass.

---

### Task 2: Domain Modeling for Ingestion
**Files:**
- Create: `backend/src/domain/entities/data_source.py`
- Create: `backend/src/domain/entities/ingestion_job.py`
- Create: `backend/src/domain/value_objects/ingestion.py`
- Modify: `backend/src/domain/services/__init__.py` (export)
- Create: `backend/src/domain/services/cleaning_rule_engine.py`
- Modify: `backend/src/domain/ports/repositories.py` (add new interfaces)
- Create: `backend/tests/unit/domain/test_ingestion_entities.py`

**Step 1: Write failing domain tests**
`backend/tests/unit/domain/test_ingestion_entities.py`:
```python
def test_data_source_masks_secret():
    src = DataSource.create_mysql(
        project_id="proj-1",
        name="CRM",
        host="localhost",
        port=3306,
        database="crm",
        username="crm_user",
        password="plain"
    )
    assert src.safe_summary()["password"] == "********"

def test_ingestion_job_transitions():
    job = IngestionJob.new(file_artifact_id="file-1", total_rows=12000)
    with pytest.raises(ValueError):
        job.complete(processed_rows=100, result_path=None)
```
Run: `cd backend && pytest tests/unit/domain/test_ingestion_entities.py -v` → FAIL.

**Step 2: Implement value objects**
`value_objects/ingestion.py`:
```python
class DataSourceType(str, Enum): FILE = "FILE"; MYSQL = "MYSQL"
class FileFormat(str, Enum): CSV="CSV"; XLSX="XLSX"; TXT="TXT"; PDF="PDF"; DOCX="DOCX"
class CleaningRuleType(str, Enum): NOT_NULL="NOT_NULL"; RANGE="RANGE"; REGEX="REGEX"; DEDUPE="DEDUPE"
class JobStatus(str, Enum): PENDING="PENDING"; RUNNING="RUNNING"; COMPLETED="COMPLETED"; FAILED="FAILED"
class ProcessingMode(str, Enum): SYNC="SYNC"; ASYNC="ASYNC"
```

**Step 3: Implement entities/services**
- `entities/data_source.py`: dataclass with factory methods for file/mysql, encryption placeholders.
- `entities/ingestion_job.py`: includes status transitions, progress calculations.
- `services/cleaning_rule_engine.py`: class with `apply(record: dict, rules: list[CleaningRule]) -> dict` and rule validation.

**Step 4: Extend ports**
Add interfaces:
```python
class DataSourceRepository(ABC):
    async def create(self, source: DataSource) -> DataSource: ...
    async def list(self, project_id: str) -> list[DataSource]: ...
    async def get(self, source_id: str) -> DataSource | None: ...

class IngestionJobRepository(ABC):
    async def create(self, job: IngestionJob) -> IngestionJob: ...
    async def update_status(...): ...
```
Add `FileStoragePort` and `PreviewCachePort` definitions.

**Step 5: Re-run tests**
`cd backend && pytest tests/unit/domain/test_ingestion_entities.py -v` → PASS.

---

### Task 3: Persistence, Storage & Alembic
**Files:**
- Modify/Create: `backend/src/infrastructure/persistence/mysql/models.py` (extend) or split to `models_ingestion.py`
- Create: `backend/src/infrastructure/persistence/mysql/repositories/data_source_repository.py`
- Create: `backend/src/infrastructure/persistence/mysql/repositories/ingestion_job_repository.py`
- Create: `backend/src/infrastructure/storage/local_storage.py`
- Modify: `backend/src/infrastructure/persistence/mysql/database.py` (session helpers if needed)
- Create Alembic revision under `backend/alembic/versions/*.py`
- Tests: `backend/tests/integration/persistence/test_data_source_repo.py`, `test_ingestion_job_repo.py`, `test_local_storage.py`

**Step 1: Write repository tests (failing)**
Example `test_data_source_repo.py`:
```python
@pytest.mark.asyncio
async def test_create_and_list_sources(db_session, data_source_repo):
    source = DataSource.create_mysql(...)
    saved = await data_source_repo.create(source)
    assert saved.id is not None
    items = await data_source_repo.list(project_id="proj-1")
    assert len(items) == 1
```
Command: `cd backend && pytest tests/integration/persistence/test_data_source_repo.py::test_create_and_list_sources -v` → FAIL.

**Step 2: Implement SQLAlchemy models**
Add tables:
```python
class DataSourceModel(Base):
    __tablename__ = "data_sources"
    id = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id = mapped_column(String(36), ForeignKey("projects.id"))
    type = mapped_column(String(20))
    name = mapped_column(String(100))
    config = mapped_column(JSON)
    status = mapped_column(String(20), default="ACTIVE")
    last_used_at = mapped_column(DateTime)

class UploadArtifactModel(Base):
    __tablename__ = "upload_artifacts"
    # fields: project_id, source_id, file_format, stored_path, size_bytes, row_count, checksum, created_by

class CleaningRuleModel(Base):
    # project_id, name, target_field, rule_type, params JSON, severity, created_by

class IngestionJobModel(Base):
    # project_id, artifact_id, source_id, mode, status, total_rows, processed_rows, error_message, result_path
```

**Step 3: Alembic migration**
`alembic revision -m "add ingestion tables"` with `upgrade()` creating the above tables (plus indexes on `project_id`, `status`). Run `alembic upgrade head`.

**Step 4: Implement repositories/storage**
- `data_source_repository.py`: map between entity <-> model, encrypt/decrypt credentials using `Fernet(settings.encryption_key)`.
- `ingestion_job_repository.py`: update status/progress columns.
- `local_storage.py`: implement `save_file(project_id, filename, file: UploadFile) -> StoredArtifact`, `open_stream`, `delete_path`.

**Step 5: Re-run integration tests**
`cd backend && pytest tests/integration/persistence -v` → PASS.

---

### Task 4: Application Services & Commands
**Files:**
- Create: `backend/src/application/services/ingestion_service.py`
- Create: `backend/src/application/commands/start_ingestion.py`
- Create: `backend/src/application/commands/register_data_source.py`
- Create: `backend/src/application/commands/apply_cleaning_preview.py`
- Create: `backend/src/application/queries/list_data_sources.py`, `get_job_status.py`
- Tests: `backend/tests/unit/application/test_ingestion_service.py`, `test_cleaning_preview.py`

**Step 1: Tests first**
Example snippet:
```python
async def test_sync_file_under_threshold(mocker, ingestion_service):
    file = UploadFile(filename="small.csv", ...)
    job = await ingestion_service.handle_file_upload(project_id="proj", user_id="user", upload=file, rules=[])
    assert job.status == JobStatus.COMPLETED
    storage.save_file.assert_called_once()
```
Run: `cd backend && pytest tests/unit/application/test_ingestion_service.py::test_sync_file_under_threshold -v` → FAIL.

**Step 2: Implement command modules**
- `register_data_source.py`: orchestrates validation + repository call.
- `start_ingestion.py`: inspects file size/row count, decides sync vs async, records job.
- `apply_cleaning_preview.py`: uses `CleaningRuleEngine` + pandas profiling for sample rows stored in Redis.

**Step 3: Build `IngestionService`**
Responsibilities:
1. Accept file uploads, store artifacts, compute schema/profile via pandas.
2. Determine processing path:
   - Sync: run pipeline inline, produce cleaned parquet/JSON stored via `local_storage`.
   - Async: create job + enqueue Celery task.
3. Support MySQL ingestion by connecting via SQLAlchemy text query (limit 10k rows for preview) and streaming results to storage.
4. Provide preview + cleaning operations.

Ensure service depends only on domain ports.

**Step 4: Wire query handlers** for listing sources and job status (pull from repos, map to DTOs).

**Step 5: Tests pass**
`cd backend && pytest tests/unit/application -v` → PASS.

---

### Task 5: FastAPI Schemas & Routers
**Files:**
- Create: `backend/src/api/schemas/ingestion.py`
- Create: `backend/src/api/routers/ingestion.py`
- Modify: `backend/src/api/dependencies/__init__.py` (export ingestion deps)
- Modify: `backend/src/main.py` (include router)
- Tests: `backend/tests/integration/api/test_ingestion_routes.py`

**Step 1: Define schemas**
`schemas/ingestion.py` includes:
```python
class FileUploadResponse(BaseModel):
    artifact_id: str
    job_id: str | None
    mode: ProcessingMode
    status: JobStatus
    preview_rows: list[dict[str, Any]] | None

class DataSourceRequest(BaseModel):
    project_id: str
    name: str
    type: Literal["FILE","MYSQL"]
    mysql: Optional[MySQLConfig] = None

class CleaningRuleTemplate(BaseModel):
    key: str
    label: str
    description: str
```

**Step 2: Implement router**
Endpoints (all require auth & project membership):
- `GET /ingestion/templates/cleaning` → static rule templates.
- `POST /ingestion/sources/mysql/test` → attempt connection.
- `POST /ingestion/sources` / `GET /ingestion/sources`.
- `POST /ingestion/upload/file` (multipart) -> uses `IngestionService.handle_file_upload`.
- `POST /ingestion/preview` -> apply rules to sample rows.
- `POST /ingestion/mysql/import` -> start job from saved source.
- `GET /ingestion/jobs`, `GET /ingestion/jobs/{job_id}`, `GET /ingestion/jobs/{job_id}/logs`.

Include dependency `get_current_user` and `ProjectAccessGuard`.

**Step 3: Integration tests**
Use `httpx.AsyncClient`:
```python
async def test_file_upload_small_dataset(authenticated_client, tmp_path):
    resp = await authenticated_client.post("/ingestion/upload/file", files={"file": ("small.csv", csv_bytes, "text/csv")}, data={"project_id": project.id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "SYNC"
```
Run: `cd backend && pytest tests/integration/api/test_ingestion_routes.py -k upload -v`.

**Step 4: Update main router registration**
`app.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])`.

---

### Task 6: Celery Integration & Async Jobs
**Files:**
- Create: `backend/src/infrastructure/queue/celery_app.py`
- Create: `backend/src/infrastructure/queue/tasks/__init__.py`
- Create: `backend/src/infrastructure/queue/tasks/ingestion_task.py`
- Modify: `docker/docker-compose.yml` (ensure worker service uses same env + volume)
- Tests: `backend/tests/unit/queue/test_ingestion_task.py`
- Scripts: `scripts/dev-start.ps1` (ensure worker started)

**Step 1: Celery app**
`celery_app.py`:
```python
celery_app = Celery("kg")
celery_app.conf.update(
    broker_url=settings.redis_uri,
    result_backend=settings.redis_uri,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)
```

**Step 2: Tasks**
`ingestion_task.run_async_job(job_id: str)`:
- Fetch job + artifact.
- Stream file in chunks, apply cleaning rules, write cleaned output, update progress in DB at every 5%.
- On success: mark COMPLETED; on exception: mark FAILED and save error.

**Step 3: Unit tests**
Use Celery eager mode:
```python
@celery_app.task()
def run_async_job(job_id): ...

def test_run_async_job_updates_status(mocker):
    mock_repo.get.return_value = job
    run_async_job.delay("job-1")
    mock_repo.update_status.assert_called_with(...)
```
Run: `cd backend && pytest tests/unit/queue/test_ingestion_task.py -v`.

**Step 4: Docker worker command**
```
worker:
  command: celery -A src.infrastructure.queue.celery_app.celery_app worker -Q ingestion -l info
  volumes:
    - uploads_data:/app/storage/uploads
```

**Step 5: Manual verification script**
Document `scripts/dev-start.ps1` to start backend + worker simultaneously.

---

### Task 7: Frontend Wizard, Stores & APIs
**Files:**
- Modify: `frontend/package.json` (add vitest, scripts)
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/types/ingestion.ts`
- Create: `frontend/src/api/ingestion.ts`
- Create: `frontend/src/stores/ingestion.ts`
- Create components under `frontend/src/components/ingestion/`:
  - `SourceSelector.vue`
  - `MySQLConnectorForm.vue`
  - `FileUploadStep.vue`
  - `FieldMappingStep.vue`
  - `CleaningRuleBuilder.vue`
  - `PreviewTable.vue`
  - `JobProgress.vue`
- Create pages `frontend/src/pages/ingestion/IngestionWizard.vue`, `frontend/src/pages/ingestion/JobList.vue`
- Modify: `frontend/src/router/index.ts`, `frontend/src/layouts/DefaultLayout.vue` (sidebar link)
- Styles: optional SCSS module `frontend/src/styles/ingestion.scss`
- Tests: `frontend/src/components/ingestion/__tests__/*.spec.ts`, `frontend/src/stores/__tests__/ingestion.spec.ts`

**Step 1: Add tooling**
`package.json`:
```json
"scripts": {
  "dev": "vite",
  "build": "vue-tsc -b && vite build",
  "preview": "vite preview",
  "test:unit": "vitest run",
  "test:unit:watch": "vitest"
},
"devDependencies": {
  "...": "...",
  "vitest": "^2.1.4",
  "@vue/test-utils": "^2.4.6"
}
```
`vitest.config.ts` to integrate Vue plugin.

**Step 2: Define types/API client**
`types/ingestion.ts`:
```ts
export interface CleaningRuleTemplate { key: string; label: string; description: string; params: Record<string, any>; }
export interface UploadArtifact { id: string; originalFilename: string; fileFormat: string; rowCount: number; createdAt: string; }
export interface IngestionJob { id: string; status: 'PENDING'|'RUNNING'|'COMPLETED'|'FAILED'; progress: number; mode: 'SYNC'|'ASYNC'; }
```
`api/ingestion.ts` uses Axios client for each endpoint.

**Step 3: Pinia store**
`useIngestionStore` with state: sources, templates, wizard form, currentPreview, jobs. Actions: `fetchTemplates`, `testMySQL`, `saveSource`, `uploadFile`, `preview`, `submitJob`, `pollJob`.

Unit test verifying state transitions using Vitest.

**Step 4: Components & pages**
- `IngestionWizard.vue`: `<el-steps>` with slots, composes steps components, ties into store actions.
- `JobList.vue`: table showing job status with `<el-progress>` bars.
- `CleaningRuleBuilder.vue`: allows adding rule cards using templates + ad-hoc fields.
- `FileUploadStep.vue`: uses `<el-upload drag>` for file selection, displays profile summary.

Add menu entry in `DefaultLayout` sidebar: `el-menu-item index="/ingestion/wizard"`.

**Step 5: Router & tests**
`router/index.ts` add children:
```ts
{
  path: 'ingestion',
  children: [
    { path: 'wizard', name: 'IngestionWizard', component: () => import('@/pages/ingestion/IngestionWizard.vue') },
    { path: 'jobs', name: 'IngestionJobs', component: () => import('@/pages/ingestion/JobList.vue') },
  ]
}
```
Vitest specs for components verifying emitted events, rule builder validation, store interactions (use `vi.mock('@/api/ingestion')`).

Run: `cd frontend && npm install && npm run test:unit`.

---

### Task 8: Verification & Documentation
**Files:**
- Modify: `docs/README.md` or `README` ingestion section
- Modify: `CLAUDE.md` (update workflow instructions)
- Create: `docs/runbooks/ingestion.md` (optional)
- Update: `scripts/dev-start.ps1`, `scripts/dev-reset.ps1` for new services

**Step 1: Document workflow**
Add doc covering:
1. Setting `ENCRYPTION_KEY`.
2. Starting Docker infra.
3. Running backend + worker + frontend.
4. Upload/preview steps.

**Step 2: Backend verification**
Run:
```
cd backend
pytest tests/unit -v
pytest tests/integration -v
PYTEST_ADDOPTS="--maxfail=1" pytest tests/unit/application/test_ingestion_service.py -k sync
```
Expected: all pass.

**Step 3: Frontend build/test**
```
cd frontend
npm run test:unit
npm run build
```

**Step 4: Manual QA checklist**
- Upload `sample_small.csv` (<1 MB) → expect immediate preview + completed job.
- Upload `sample_large.xlsx` (~15 MB) → job status transitions PENDING → RUNNING → COMPLETED; file stored under `storage/uploads/<project_id>/clean/`.
- Configure MySQL connector (use docker MySQL) and import table; verify cleaned dataset path exists.
- Apply NOT_NULL + RANGE rules and ensure preview highlights dropped rows.
- Refresh job list page ensures polling.

**Step 5: Final instructions**
After verification, prepare commit message `feat(ingestion): add data ingestion and preprocessing module`.

---

## Next-Step Options
Plan complete. Execution choices once ready:
1. Subagent-Driven (this session) — use superpowers:subagent-driven-development per task.
2. Parallel Session — open new session in a worktree, follow superpowers:executing-plans.

