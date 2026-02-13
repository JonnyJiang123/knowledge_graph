# Knowledge Graph Platform

A full-stack knowledge graph workbench for finance and healthcare teams. It ingests messy files or MySQL tables, cleans and profiles data, runs NLP/graph reasoning, and surfaces insights through a Vue 3 UI.

## Product Overview
- Built for mid-market financial + healthcare orgs that need low-cost graph intelligence tooling (see [知识图谱prd.md](知识图谱prd.md) for the full PRD in Chinese).
- Focuses on rapid multi-source ingestion, configurable cleaning, graph modeling, and visualization without large engineering teams.
- Ships opinionated artifacts for liquidity/risk (finance) and symptom/drug reasoning (healthcare) while staying extensible for other industries.

## System Architecture
- **Hexagonal backend** (FastAPI + SQLAlchemy) keeps domain logic isolated from infrastructure. Ports cover repositories, storage, queue, and preview cache as outlined in [2026-02-09-architecture-design.md](docs/plans/2026-02-09-architecture-design.md).
- **Dual data stores**: MySQL holds projects, ingestion metadata, cleaning rules, and file manifests; Neo4j 5.x stores the final knowledge graph. Redis powers both Celery and preview caching.
- **Hybrid processing**: The ingestion service inspects payload size/row counts to decide between sync (≤5 MB or ≤10k rows) and async (Celery) paths. Async jobs reuse the Redis broker/result backend defined in `docker/docker-compose.yml`.
- **Frontend**: Vue 3 + Vite + Pinia + Element Plus deliver the ingestion wizard, project dashboards, and graph visualization (details in the same architecture doc).

## Backend Highlights
- `backend/src/application/services/ingestion_service.py` orchestrates uploads, profiling, cleaning rule evaluation, and MySQL imports. It delegates to Celery when work exceeds the thresholds described in [2026-02-11-phase2-ingestion.md](docs/plans/2026-02-11-phase2-ingestion.md).
- Domain entities (`DataSource`, `IngestionJob`, cleaning rules) live under `backend/src/domain/`. Ports describe repositories, storage, preview cache, and task queues to keep adapters swappable.
- Persistence adapters use SQLAlchemy models for `data_sources`, `upload_artifacts`, `cleaning_rules`, and `ingestion_jobs`, with Fernet-encrypted connector secrets.
- Celery worker command (used both locally and in Docker):
  ```bash
  celery -A src.infrastructure.queue.celery_app.celery_app worker -Q ingestion -l info
  ```
- File artifacts and cleaned exports live under `storage/uploads/<project_id>/...` (mounted via the `uploads_data` volume in Docker).

### Required Environment Variables
Set these in `backend/.env` or `docker/.env` before running services:
- `MYSQL_URI` – e.g. `mysql+asyncmy://knowledge_graph:<password>@127.0.0.1:2881/knowledge_graph`
- `NEO4J_URI` – e.g. `neo4j://localhost:7687`
- `NEO4J_USER` / `NEO4J_PASSWORD` – defaults to `neo4j` / `12345678` in local dev
- `REDIS_URI` – default `redis://localhost:6379/0`
- `UPLOAD_BASE_DIR`, `TMP_DIR`, `PREVIEW_ROW_LIMIT`, `ENCRYPTION_KEY` – see `backend/src/config.py` and `.env.example` for defaults (generate Fernet keys with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).

## Frontend Experience
- Vue 3 wizard guides users through **source selection → field mapping → cleaning rules → preview → submission**.
- Pinia stores coordinate API calls, job polling, and Element Plus stepper state; components live in `frontend/src/components/ingestion/`.
- Vitest + Vue Test Utils cover wizard logic; run `npm run test:unit` inside `frontend/`.

## Data Ingestion Flows
- **File uploads** (CSV/XLSX/TXT/PDF/Word): stored via the file storage adapter, profiled with pandas, then processed either inline or via Celery. Preview caches (~50 rows) sit in Redis.
- **MySQL ingestion**: configure connectors via the `/ingestion/sources` endpoints; credentials are encrypted with Fernet before persisting. Preview queries cap at 10k rows, with async jobs streaming to disk before extraction.
- Cleaning rules (NOT_NULL, RANGE, REGEX, DEDUPE) are reusable templates. The README companion plan in [2026-02-11-phase2-ingestion.md](docs/plans/2026-02-11-phase2-ingestion.md) documents the rule engine and job states.

## Local Development Workflow
1. **Install deps**
   ```powershell
   cd backend
   pip install -e .[dev]
   cd ../frontend
   npm install
   ```
2. **Start services (Docker)**
   ```powershell
   cd docker
   docker compose up -d
   ```
   This launches MySQL, Neo4j, Redis, backend API (`uvicorn`), and the Celery worker with the shared `uploads_data` volume.
3. **Run everything manually (alternative)**
   ```powershell
   scripts/dev-start.ps1          # spins up backend + worker + frontend watchers
   # or individually
   cd backend; uvicorn src.main:app --reload
   celery -A src.infrastructure.queue.celery_app.celery_app worker -Q ingestion -l info
   cd ../frontend; npm run dev
   ```
4. **Populate sample data** – configure `.env` with the MySQL/Neo4j credentials above, then use the ingestion wizard to upload sample CSVs or run MySQL imports.

## Testing
- Backend unit tests: `cd backend && pytest tests/unit -v`
- Backend integration tests (requires Docker services): `cd backend && pytest tests/integration -v`
- Celery task unit tests (eager mode): `cd backend && pytest tests/unit/queue/test_ingestion_task.py -v`
- Frontend tests: `cd frontend && npm run test:unit`

## Documentation Map
- Product brief / personas: [知识图谱prd.md](知识图谱prd.md)
- Platform architecture: [2026-02-09-architecture-design.md](docs/plans/2026-02-09-architecture-design.md)
- Phase 1 backend delivery notes: [2026-02-09-phase1-implementation.md](docs/plans/2026-02-09-phase1-implementation.md)
- Ingestion slice details: [2026-02-11-phase2-ingestion.md](docs/plans/2026-02-11-phase2-ingestion.md)
- This README refresh plan: [2026-02-13-readme-update.md](docs/plans/2026-02-13-readme-update.md)

