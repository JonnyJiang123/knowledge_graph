# Knowledge Graph Platform - Architecture Design

**Date:** 2026-02-09
**Status:** Approved
**Version:** 1.0

## Design Decisions Summary

| Decision | Choice |
|----------|--------|
| Priority | Foundation-first (invest upfront for V1.5/V2.0) |
| Backend structure | Monolith with clear module boundaries |
| Architecture pattern | Pragmatic Hexagonal (ports for key infra only) |
| Frontend state | Pinia with domain stores |
| NLP processing | Hybrid sync/async (small files immediate, large files queued) |
| Queue | Celery + Redis |
| Databases | Neo4j 5.x (graph) + MySQL 8.0 (relational) |
| Testing | Unit (domain) + Integration (testcontainers) + E2E |

## 1. High-Level Structure

```
knowledge-graph-platform/
├── frontend/                 # Vue 3 application
├── backend/                  # FastAPI application
├── shared/                   # Shared types/contracts (OpenAPI generated)
├── docker/                   # Docker configs
├── docs/                     # Documentation
└── scripts/                  # Dev/deploy scripts
```

### Backend Hexagonal Layers

```
backend/
├── src/
│   ├── domain/              # Pure business logic, zero external deps
│   │   ├── entities/        # Enterprise, Drug, Symptom, Relation...
│   │   ├── value_objects/   # EntityType, RiskLevel, MatchScore...
│   │   ├── services/        # Domain services (reasoning, matching)
│   │   └── ports/           # Interfaces (repositories, NLP, queue)
│   │
│   ├── application/         # Use cases, orchestration
│   │   ├── commands/        # Write operations (ingest, extract, build)
│   │   ├── queries/         # Read operations (search, path, analyze)
│   │   └── services/        # Application services coordinating domain
│   │
│   ├── infrastructure/      # Adapters implementing ports
│   │   ├── persistence/     # Neo4j, MySQL repositories
│   │   ├── nlp/             # Jieba, HanLP, spaCy adapters
│   │   ├── queue/           # Celery/RQ task queue
│   │   └── storage/         # File system, OSS adapters
│   │
│   └── api/                  # FastAPI routers, DTOs, middleware
│       ├── routers/
│       ├── schemas/          # Pydantic request/response models
│       └── dependencies/     # DI container, auth
```

**Key principle**: Domain layer imports nothing from infrastructure. All external tools (Neo4j, NLP libs, file parsers) are behind port interfaces.

## 2. Domain Layer - Entities & Value Objects

### Core Entities (shared across industries)

```python
# domain/entities/
├── entity.py          # Knowledge graph node (base class)
├── relation.py        # Knowledge graph edge
├── graph_project.py   # Container for a knowledge graph project
├── extraction_job.py  # Tracks data ingestion/extraction progress
└── rule.py            # Reasoning rule definition
```

### Value Objects (immutable, identity-less)

```python
# domain/value_objects/
├── entity_type.py     # Enum: ENTERPRISE, PERSON, DRUG, SYMPTOM...
├── relation_type.py   # Enum: HOLDS_STOCK, GUARANTEES, TREATS...
├── risk_level.py      # Enum: LOW, MEDIUM, HIGH
├── match_score.py     # Float 0-1 with validation
├── path_result.py     # Immutable path query result
└── industry.py        # Enum: FINANCE, HEALTHCARE
```

### Industry-Specific Domain Services

```python
# domain/services/
├── extraction/
│   └── knowledge_extractor.py      # Orchestrates NER + relation extraction
├── reasoning/
│   ├── rule_engine.py              # Base rule evaluation
│   ├── finance_rules.py            # Fraud detection, risk propagation
│   └── healthcare_rules.py         # Drug interaction, symptom matching
├── analysis/
│   └── centrality_analyzer.py      # Core node identification
└── matching/
    └── symptom_disease_matcher.py  # Healthcare-specific matching
```

### Ports (interfaces that infrastructure implements)

```python
# domain/ports/
├── repositories/
│   ├── entity_repository.py        # Abstract graph storage
│   ├── project_repository.py       # Project metadata storage
│   └── user_repository.py          # User/auth storage
├── nlp/
│   ├── tokenizer.py                # Segmentation interface
│   └── ner_extractor.py            # Named entity recognition interface
└── queue/
    └── task_queue.py               # Background job interface
```

## 3. Application Layer - Use Cases

Using Command/Query separation (not full CQRS, but clear intent).

### Commands (write operations)

```python
# application/commands/
├── ingest_data.py           # Upload file/connect DB → preprocess → store raw
├── extract_knowledge.py     # Run NER + relation extraction on raw data
├── build_graph.py           # Finalize entities/relations → persist to Neo4j
├── merge_entities.py        # Entity disambiguation/fusion
├── create_rule.py           # Add custom reasoning rule
├── run_reasoning.py         # Execute rules against graph
└── backup_project.py        # Trigger project backup
```

### Queries (read operations)

```python
# application/queries/
├── search_entities.py       # Keyword/condition search
├── natural_language_query.py   # NL → Cypher translation
├── find_paths.py            # N-degree path finding
├── get_graph_visualization.py  # Fetch nodes/edges for rendering
├── analyze_centrality.py    # Compute core nodes
├── match_symptoms.py        # Healthcare: symptom → disease matching
├── analyze_enterprise.py    # Finance: company association analysis
└── check_drug_interaction.py   # Healthcare: drug compatibility
```

### Application Services (coordinate complex flows)

```python
# application/services/
├── ingestion_service.py     # Hybrid sync/async file processing logic
├── extraction_pipeline.py   # Orchestrates tokenize → NER → relation → fusion
├── query_service.py         # Routes queries, caches results
└── project_service.py       # CRUD for graph projects
```

### Example Flow - Data Ingestion

```
API receives file
  → ingestion_service checks file size
  → small file: execute extract_knowledge command directly
  → large file: push to task_queue port, return job_id
  → worker picks up job, runs extraction_pipeline
  → emits progress events for frontend polling
```

## 4. Infrastructure Layer - Adapters

### Persistence Adapters

```python
# infrastructure/persistence/
├── neo4j/
│   ├── neo4j_client.py              # Connection pool, session management
│   ├── entity_repository_impl.py    # Implements EntityRepository port
│   ├── cypher_queries.py            # Reusable Cypher query templates
│   └── graph_algorithms.py          # Centrality, path finding via Neo4j GDS
├── mysql/
│   ├── database.py                  # SQLAlchemy async engine
│   ├── models.py                    # ORM models (User, Project, Log, Job)
│   ├── user_repository_impl.py      # Implements UserRepository port
│   └── project_repository_impl.py   # Implements ProjectRepository port
└── migrations/                      # Alembic migrations for MySQL
```

### NLP Adapters

```python
# infrastructure/nlp/
├── jieba_tokenizer.py        # Implements Tokenizer port
├── hanlp_ner.py              # Implements NERExtractor port (primary)
├── spacy_ner.py              # Implements NERExtractor port (alternative)
└── relation_extractor.py     # Pattern-based + dependency parsing
```

### Queue Adapters (for hybrid sync/async)

```python
# infrastructure/queue/
├── celery_config.py          # Celery + Redis setup
├── celery_queue.py           # Implements TaskQueue port
├── tasks/
│   ├── extraction_task.py    # Background knowledge extraction
│   ├── reasoning_task.py     # Background rule execution
│   └── backup_task.py        # Background project backup
└── sync_executor.py          # Direct execution for small files
```

### Storage Adapters

```python
# infrastructure/storage/
├── local_storage.py          # Local filesystem adapter
├── aliyun_oss.py             # Optional cloud storage
└── file_parsers/
    ├── excel_parser.py       # xlsx/csv parsing
    ├── pdf_parser.py         # PyPDF2 adapter
    └── word_parser.py        # python-docx adapter
```

### Dependency Injection

```python
# api/dependencies/container.py
# Using dependency-injector or simple factory pattern
# Swappable adapters for testing (mock Neo4j, in-memory queue)
```

## 5. API Layer - FastAPI Structure

### Router Organization (mirrors PRD modules)

```python
# api/routers/
├── auth.py                  # Login, logout, token refresh
├── users.py                 # User/role CRUD (admin only)
├── projects.py              # Graph project CRUD
├── ingestion.py             # File upload, DB connect, data preview
├── extraction.py            # Trigger extraction, check job status
├── entities.py              # Entity CRUD, batch operations
├── relations.py             # Relation CRUD, batch operations
├── query.py                 # Search, NL query, path finding
├── visualization.py         # Graph data for frontend rendering
├── reasoning.py             # Rules CRUD, trigger reasoning
├── finance/                 # Finance-specific endpoints
│   ├── association.py       # Enterprise association analysis
│   ├── fraud.py             # Anti-fraud detection
│   └── risk.py              # Credit risk assessment
├── healthcare/              # Healthcare-specific endpoints
│   ├── diagnosis.py         # Symptom-disease matching
│   ├── drugs.py             # Drug interaction queries
│   └── medical_records.py   # Medical record QC
├── system/                  # System management
│   ├── monitoring.py        # Health, metrics
│   ├── logs.py              # Operation logs
│   └── backup.py            # Backup/restore triggers
└── jobs.py                  # Background job status polling
```

### Schemas (Pydantic DTOs)

```python
# api/schemas/
├── common.py                # Pagination, error responses
├── auth.py                  # LoginRequest, TokenResponse
├── entity.py                # EntityCreate, EntityResponse, EntityBatch
├── query.py                 # SearchRequest, PathRequest, NLQueryRequest
├── visualization.py         # GraphData (nodes + edges for ECharts)
├── job.py                   # JobStatus, JobProgress
└── industry/
    ├── finance.py           # RiskReport, FraudAlert, AssociationGraph
    └── healthcare.py        # DiagnosisResult, DrugInteraction, QCReport
```

### Middleware & Dependencies

```python
# api/
├── middleware/
│   ├── auth.py              # JWT validation
│   ├── logging.py           # Request/response logging
│   └── error_handler.py     # Global exception → JSON response
└── dependencies/
    ├── auth.py              # get_current_user, require_role
    ├── container.py         # DI container access
    └── pagination.py        # Common pagination params
```

## 6. Frontend - Vue 3 Structure

### Top-Level Organization

```
frontend/
├── src/
│   ├── api/                 # API client layer
│   ├── assets/              # Static assets, industry themes
│   ├── components/          # Reusable UI components
│   ├── composables/         # Shared logic (useAuth, usePolling)
│   ├── layouts/             # Page layouts (default, auth, dashboard)
│   ├── pages/               # Route-level views
│   ├── router/              # Vue Router config
│   ├── stores/              # Pinia domain stores
│   ├── types/               # TypeScript interfaces
│   └── utils/               # Helpers (formatters, validators)
├── public/
└── vite.config.ts
```

### Pinia Domain Stores

```typescript
// stores/
├── auth.ts              // User session, permissions
├── project.ts           // Current project, project list
├── graph.ts             // Nodes, edges, selection state
├── query.ts             // Search history, saved queries
├── extraction.ts        // Job tracking, progress polling
├── reasoning.ts         // Rules, reasoning results
├── visualization.ts     // Layout mode, filters, zoom level
├── notification.ts      // Toasts, alerts, system messages
└── settings.ts          // UI preferences, industry mode
```

### Component Organization

```
components/
├── common/              # Button, Modal, Table, Form...
├── graph/               # Graph-specific components
│   ├── GraphCanvas.vue       # ECharts wrapper
│   ├── NodeTooltip.vue       # Hover info
│   ├── FilterPanel.vue       # Entity/relation filters
│   ├── LayoutSwitcher.vue    # Force/hierarchy/circular
│   └── ExportDialog.vue      # PNG/JSON export
├── extraction/          # Data ingestion components
│   ├── FileUploader.vue
│   ├── DatabaseConnector.vue
│   ├── DataPreview.vue
│   └── JobProgress.vue
├── query/               # Query components
│   ├── SearchBar.vue
│   ├── NLQueryInput.vue
│   ├── PathFinder.vue
│   └── ResultList.vue
└── industry/            # Industry-specific
    ├── finance/
    └── healthcare/
```

### Pages (route views)

```
pages/
├── Login.vue
├── Dashboard.vue
├── projects/
├── ingestion/
├── extraction/
├── graph/
├── query/
├── reasoning/
├── finance/             # Finance module pages
├── healthcare/          # Healthcare module pages
└── system/              # Admin pages
```

## 7. Cross-Cutting Concerns

### Hybrid Sync/Async Processing Flow

```python
# Threshold configuration
SYNC_FILE_SIZE_LIMIT = 5 * 1024 * 1024  # 5MB
SYNC_ROW_LIMIT = 10000                   # 10K rows

# ingestion_service.py
async def process_data(file: UploadFile, project_id: str):
    size = file.size

    if size <= SYNC_FILE_SIZE_LIMIT:
        # Sync path - immediate response
        result = await extraction_pipeline.execute(file, project_id)
        return {"status": "completed", "result": result}
    else:
        # Async path - queue and return job ID
        job_id = await task_queue.enqueue(
            "extraction_task",
            file_path=saved_path,
            project_id=project_id
        )
        return {"status": "processing", "job_id": job_id}
```

### Job Polling (frontend)

```typescript
// composables/useJobPolling.ts
export function useJobPolling(jobId: string) {
  const status = ref<JobStatus>('pending')
  const progress = ref(0)

  const poll = async () => {
    const res = await api.jobs.getStatus(jobId)
    status.value = res.status
    progress.value = res.progress

    if (res.status === 'completed' || res.status === 'failed') {
      stop()
    }
  }

  const { pause: stop } = useIntervalFn(poll, 2000)
  return { status, progress, stop }
}
```

### Error Handling Strategy

```python
# domain/exceptions.py - Domain errors
class EntityNotFoundError(DomainError): ...
class DuplicateEntityError(DomainError): ...
class InvalidRuleError(DomainError): ...
class ExtractionFailedError(DomainError): ...

# api/middleware/error_handler.py - Maps to HTTP
DOMAIN_ERROR_MAP = {
    EntityNotFoundError: (404, "ENTITY_NOT_FOUND"),
    DuplicateEntityError: (409, "DUPLICATE_ENTITY"),
    InvalidRuleError: (400, "INVALID_RULE"),
}
```

### Testing Strategy

```
tests/
├── unit/
│   ├── domain/          # Pure logic, no mocks needed
│   └── application/     # Mock ports, test use cases
├── integration/
│   ├── persistence/     # Real Neo4j/MySQL (testcontainers)
│   └── nlp/             # Real NLP libs, sample texts
└── e2e/
    └── api/             # Full API tests with test DB
```

## 8. Deployment & Dev Setup

### Docker Compose Structure

```yaml
# docker/docker-compose.yml
services:
  frontend:
    build: ../frontend
    ports: ["3000:80"]

  backend:
    build: ../backend
    ports: ["8000:8000"]
    depends_on: [neo4j, mysql, redis]
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - MYSQL_URI=mysql://mysql:3306/kg
      - REDIS_URI=redis://redis:6379

  worker:
    build: ../backend
    command: celery -A infrastructure.queue.celery_config worker
    depends_on: [redis, neo4j]

  neo4j:
    image: neo4j:5-community
    ports: ["7474:7474", "7687:7687"]
    volumes: [neo4j_data:/data]

  mysql:
    image: mysql:8.0
    volumes: [mysql_data:/var/lib/mysql]

  redis:
    image: redis:7-alpine
```

### Development Scripts

```powershell
# scripts/
├── dev-setup.ps1        # Install deps, init DBs, seed data
├── dev-start.ps1        # Start all services locally
├── dev-reset.ps1        # Reset DBs to clean state
├── test-unit.ps1        # Run unit tests
├── test-integration.ps1 # Run integration tests (needs Docker)
└── build.ps1            # Production build
```

### Recommended Dev Workflow

```
1. Run Neo4j + MySQL + Redis via Docker
2. Run backend with uvicorn --reload
3. Run worker with celery -A ... worker
4. Run frontend with npm run dev
```

### Environment Configuration

```python
# backend/src/config.py
class Settings(BaseSettings):
    # Database
    neo4j_uri: str = "bolt://localhost:7687"
    mysql_uri: str = "mysql+asyncmy://root:pass@localhost:3306/kg"
    redis_uri: str = "redis://localhost:6379"

    # Processing thresholds
    sync_file_size_limit: int = 5 * 1024 * 1024
    sync_row_limit: int = 10000

    # NLP
    default_ner_provider: str = "hanlp"  # or "spacy"

    class Config:
        env_file = ".env"
```

## Key Architectural Benefits

1. **Domain logic isolated, easily testable** - No framework dependencies in domain layer
2. **NLP providers swappable** - HanLP ↔ spaCy via ports
3. **Graph database swappable** - Neo4j → other via repository ports
4. **Industry modules cleanly separated** - Finance/healthcare as distinct router groups
5. **Ready for microservice extraction** - Clear module boundaries for V2.0
