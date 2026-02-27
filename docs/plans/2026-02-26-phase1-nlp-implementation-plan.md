# Phase 1 NLP Extraction (Chinese) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver the P0 Chinese-only knowledge extraction stack (domain ports/services, NLP adapters, application commands, and API endpoints) so ingestion jobs can run tokenize → NER → relation steps and persist results.

**Architecture:** Hexagonal domain ports (Tokenizer, NER, Relation) feed a `KnowledgeExtractor` service that outputs `MatchScore` + `PathResult` aggregates. Infrastructure adapters wrap Jieba and HanLP for Chinese, exposing async + sync calls. Application commands orchestrate Celery jobs and persist to Neo4j/MySQL before API routers expose job-trigger + merge endpoints.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, Celery, Redis, MySQL, Neo4j, jieba, HanLP, pytest, httpx.

---

### Task 1: Domain Value Objects (MatchScore, PathResult)

**Files:**
- Create: `backend/src/domain/value_objects/match_score.py`
- Create: `backend/src/domain/value_objects/path_result.py`
- Modify: `backend/src/domain/value_objects/__init__.py`
- Test: `tests/unit/domain/value_objects/test_match_score.py`, `tests/unit/domain/value_objects/test_path_result.py`

**Step 1: Write failing tests**
```python
# tests/unit/domain/value_objects/test_match_score.py
import pytest
from backend.src.domain.value_objects import MatchScore

def test_match_score_accepts_range():
    assert MatchScore(0.85).value == 0.85

def test_match_score_outside_range_raises():
    with pytest.raises(ValueError):
        MatchScore(-0.2)
```
```python
# tests/unit/domain/value_objects/test_path_result.py
from backend.src.domain.value_objects import PathResult

def test_path_result_returns_nodes_edges():
    result = PathResult(nodes=["A", "B"], relations=["REL"], score=0.9)
    assert result.length == 2 and result.score == 0.9
```
**Step 2: Run tests to see failures**
Run: `pytest tests/unit/domain/value_objects -q`
Expected: FAIL (objects not defined / validation missing).

**Step 3: Implement value objects**
```python
# backend/src/domain/value_objects/match_score.py
from dataclasses import dataclass

@dataclass(frozen=True)
class MatchScore:
    value: float

    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("MatchScore must be between 0 and 1")
```
```python
# backend/src/domain/value_objects/path_result.py
from dataclasses import dataclass, field
from typing import Sequence
from .match_score import MatchScore

@dataclass(frozen=True)
class PathResult:
    nodes: Sequence[str]
    relations: Sequence[str]
    score: float = field(default=1.0)

    @property
    def length(self) -> int:
        return max(len(self.nodes) - 1, 0)

    def normalized_score(self) -> MatchScore:
        return MatchScore(self.score)
```
**Step 4: Re-run tests**
Run: `pytest tests/unit/domain/value_objects -q`
Expected: PASS.

**Step 5: Commit**
Run: `git add backend/src/domain/value_objects tests/unit/domain/value_objects && git commit -m "feat: add match score and path result"`

---

### Task 2: Domain NLP Ports Package + KnowledgeExtractor Service

**Files:**
- Modify: `backend/src/domain/ports/__init__.py`
- Replace: `backend/src/domain/ports/nlp.py` with package `backend/src/domain/ports/nlp/`
  - Create: `backend/src/domain/ports/nlp/__init__.py`
  - Create: `backend/src/domain/ports/nlp/tokenizer.py`
  - Create: `backend/src/domain/ports/nlp/ner_extractor.py`
  - Create: `backend/src/domain/ports/nlp/relation_extractor.py`
  - Create: `backend/src/domain/ports/nlp/types.py`
  - Create: `backend/src/domain/ports/nlp/pipeline.py`
- Create: `backend/src/domain/services/extraction/knowledge_extractor.py`
- Test: `tests/unit/domain/ports/test_nlp_types.py`, `tests/unit/domain/services/test_knowledge_extractor.py`

**Step 1: Write failing tests**
```python
# tests/unit/domain/ports/test_nlp_types.py
from backend.src.domain.ports.nlp import Token, EntityMention, RelationMention

def test_token_positions_are_readonly():
    token = Token(text="上海", pos="ns", start=0, end=2)
    assert token.text == "上海" and token.end == 2
```
```python
# tests/unit/domain/services/test_knowledge_extractor.py
import asyncio
from backend.src.domain.services.extraction.knowledge_extractor import KnowledgeExtractor
from backend.src.domain.ports.nlp import Tokenizer, NERExtractor, RelationExtractor

class DummyTokenizer(Tokenizer):
    async def tokenize(self, text): return []
    def tokenize_sync(self, text): return []

class DummyNER(NERExtractor):
    async def extract_entities(self, text): return []
    def extract_entities_sync(self, text): return []
    @property
    def supported_labels(self): return {"ORG"}

class DummyRelation(RelationExtractor):
    async def extract_relations(self, text, entities): return []
    def extract_relations_sync(self, text, entities): return []

async def test_async_pipeline_runs_all_ports():
    extractor = KnowledgeExtractor(DummyTokenizer(), DummyNER(), DummyRelation())
    result = await extractor.process_text("测试")
    assert result.tokens == [] and result.entities == [] and result.relations == []
```
**Step 2: Run tests**
Run: `pytest tests/unit/domain/ports tests/unit/domain/services -q`
Expected: FAIL (modules missing and service undefined).

**Step 3: Implement ports + service**
- Move dataclasses/exceptions from old `nlp.py` into `types.py` and expose via `backend/src/domain/ports/nlp/__init__.py`.
- Define abstract base classes in dedicated files with async + sync APIs mirroring roadmap.
- Implement `KnowledgeExtractor` to orchestrate tokenizer → NER → relation steps with both async (`process_text`) and sync (`process_text_sync`) helpers, returning a frozen dataclass `ExtractionResult` for typed outputs.

**Step 4: Update imports**
- Search repo for `domain.ports.nlp` usages via `rg "domain\\.ports\\.nlp" -n` and adjust to new package path.

**Step 5: Re-run tests**
Run: `pytest tests/unit/domain/ports tests/unit/domain/services -q`
Expected: PASS.

**Step 6: Commit**
`git add backend/src/domain/ports backend/src/domain/services tests/unit/domain && git commit -m "feat: add NLP ports package and extractor"`

---

### Task 3: Infrastructure NLP Adapters (Chinese)

**Files:**
- Create: `backend/src/infrastructure/nlp/__init__.py`
- Create: `backend/src/infrastructure/nlp/jieba_tokenizer.py`
- Create: `backend/src/infrastructure/nlp/hanlp_ner.py`
- Create: `backend/src/infrastructure/nlp/pattern_relation_extractor.py`
- Modify: `pyproject.toml` (add `jieba`, `hanlp`, `pyhanlp` dependencies)
- Test: `tests/integration/nlp/test_tokenizer.py`, `tests/integration/nlp/test_ner.py`, `tests/integration/nlp/test_relations.py`

**Step 1: Write failing integration tests**
```python
# tests/integration/nlp/test_tokenizer.py
import pytest
from backend.src.infrastructure.nlp.jieba_tokenizer import JiebaTokenizer

@pytest.mark.asyncio
async def test_jieba_tokenizes_chinese_text():
    tokenizer = JiebaTokenizer()
    tokens = await tokenizer.tokenize("上海证券交易所")
    assert any(t.text == "上海" for t in tokens)
```
```python
# tests/integration/nlp/test_ner.py
import pytest
from backend.src.infrastructure.nlp.hanlp_ner import HanLPNERExtractor

@pytest.mark.asyncio
async def test_hanlp_returns_entities():
    ner = HanLPNERExtractor()
    entities = await ner.extract_entities("阿里巴巴总部位于杭州")
    assert any(e.label == "ORG" for e in entities)
```
**Step 2: Run tests to confirm failures**
`pytest tests/integration/nlp -q` (expected import errors).

**Step 3: Implement adapters**
- `JiebaTokenizer` uses `jieba.posseg` to populate `Token` objects; include lazy model load + thread lock.
- `HanLPNERExtractor` initializes `HanLP` once, maps HanLP labels to internal label set, exposes `supported_labels` and async/sync paths.
- `PatternRelationExtractor` applies regex + dependency templates to emit `RelationMention` for verbs like “任/位于/收购”.
- Wrap third-party errors in `NLPPipelineError` and provide graceful fallbacks (return empty list when model unavailable in tests).

**Step 4: Update pyproject.toml**
Add dependencies with pins (e.g., `jieba>=0.42.1`, `hanlp>=2.1.0`) and run `poetry lock` / `poetry install`.

**Step 5: Re-run integration tests**
`pytest tests/integration/nlp -q` (allow skips via env flag if models not downloaded).

**Step 6: Commit**
`git add backend/src/infrastructure/nlp pyproject.toml tests/integration/nlp && git commit -m "feat: add Chinese NLP adapters"`

---

### Task 4: Application Extraction Commands + Pipeline Service

**Files:**
- Create: `backend/src/application/services/extraction_pipeline.py`
- Create: `backend/src/application/commands/extract_knowledge.py`
- Create: `backend/src/application/commands/build_graph.py`
- Create: `backend/src/application/commands/merge_entities.py`
- Modify: `backend/src/application/__init__.py`
- Test: `tests/unit/application/test_extraction_pipeline.py`, `tests/unit/application/test_commands.py`

**Step 1: Write failing service tests**
```python
# tests/unit/application/test_extraction_pipeline.py
import pytest
from unittest.mock import AsyncMock
from backend.src.application.services.extraction_pipeline import ExtractionPipeline

@pytest.mark.asyncio
async def test_pipeline_invokes_ports_in_order():
    tokenizer = AsyncMock()
    ner = AsyncMock()
    relation = AsyncMock()
    repo = AsyncMock()
    pipeline = ExtractionPipeline(tokenizer, ner, relation, repo)
    await pipeline.run("原始文本", project_id=1, user_id=7)
    tokenizer.tokenize.assert_awaited_once()
    ner.extract_entities.assert_awaited_once()
```
**Step 2: Write failing command tests**
```python
# tests/unit/application/test_commands.py
from unittest.mock import AsyncMock
from backend.src.application.commands.extract_knowledge import ExtractKnowledgeCommand

async def test_extract_command_enqueues_job():
    pipeline = AsyncMock()
    job_repo = AsyncMock()
    cmd = ExtractKnowledgeCommand(pipeline, job_repo)
    job = await cmd.execute(project_id=1, text="百度是一家科技公司")
    job_repo.create.assert_awaited_once()
    pipeline.run.assert_awaited_once()
```
Add tests for `BuildGraphCommand` and `MergeEntitiesCommand` verifying GraphRepository interactions.

**Step 3: Run tests**
`pytest tests/unit/application -q` → FAIL.

**Step 4: Implement services + commands**
- `ExtractionPipeline.run` composes NLP outputs, persists via repositories, emits ingestion job updates using `MatchScore` + `PathResult`.
- `ExtractKnowledgeCommand` handles request validation, triggers Celery background job (inject Celery task object, but in unit tests mock interface).
- `BuildGraphCommand` persists aggregated entities/relations to Neo4j through repositories.
- `MergeEntitiesCommand` merges duplicates based on `MatchScore` threshold parameter.

**Step 5: Re-run tests**
`pytest tests/unit/application -q` → PASS.

**Step 6: Commit**
`git add backend/src/application tests/unit/application && git commit -m "feat: add extraction pipeline commands"`

---

### Task 5: Extraction API Routers + Schemas

**Files:**
- Create: `backend/src/api/schemas/extraction.py`
- Create: `backend/src/api/routers/extraction.py`
- Modify: `backend/src/api/routers/__init__.py`
- Modify: `backend/src/api/dependencies.py`
- Test: `tests/integration/api/test_extraction_routes.py`

**Step 1: Write failing API tests**
```python
# tests/integration/api/test_extraction_routes.py
import pytest

@pytest.mark.asyncio
async def test_create_extraction_job(async_client):
    response = await async_client.post(
        "/api/extraction/jobs",
        json={"project_id": 1, "text": "腾讯控股总部在深圳"},
    )
    assert response.status_code == 202
    assert "job_id" in response.json()
```
Add tests for `GET /api/extraction/jobs/{job_id}` and `POST /api/extraction/entities/merge`.

**Step 2: Run tests**
`pytest tests/integration/api/test_extraction_routes.py -q` → FAIL.

**Step 3: Implement schemas + router**
- Define request/response Pydantic models with validation (max text length, allowed dedupe thresholds).
- Router handlers call application commands and map domain exceptions (`NLPPipelineError`, `ProcessingError`) to HTTP 422/500 responses.

**Step 4: Wire dependencies**
- Update DI container to construct `ExtractionPipeline`, `ExtractKnowledgeCommand`, etc., injecting infrastructure adapters created in Task 3.
- Register router with prefix `/api/extraction` and tag `Extraction`.

**Step 5: Re-run tests**
`pytest tests/integration/api/test_extraction_routes.py -q` → PASS.

**Step 6: Commit**
`git add backend/src/api tests/integration/api/test_extraction_routes.py && git commit -m "feat: add extraction endpoints"`

---

### Task 6: End-to-End Smoke + Celery Wiring

**Files:**
- Create: `tests/integration/extraction/test_end_to_end.py`
- Modify: `docker-compose.yml` (ensure Redis/Neo4j/HanLP resources available)
- Update: `docs/plans/2026-02-26-phase1-phase2-completion-report.md`

**Step 1: Write failing e2e test**
```python
# tests/integration/extraction/test_end_to_end.py
import pytest

@pytest.mark.asyncio
async def test_celery_job_processes_text(async_client, celery_worker):
    resp = await async_client.post(
        "/api/extraction/jobs",
        json={"project_id": 1, "text": "字节跳动总部在北京"},
    )
    job_id = resp.json()["job_id"]
    result = await wait_for_job(async_client, job_id)
    assert result["status"] == "completed"
    assert result["entities"]
```
**Step 2: Run test**
`pytest tests/integration/extraction/test_end_to_end.py -q` → FAIL.

**Step 3: Implement helpers**
- Add `wait_for_job` utility polling `/api/extraction/jobs/{job_id}` with timeout.
- Ensure Celery worker fixture uses in-memory backend (`CELERY_BROKER_URL=redis://localhost/15`).
- Configure pipeline to persist to test Neo4j database (use env var or fixture to clean between runs).

**Step 4: Re-run tests**
`pytest tests/integration/extraction/test_end_to_end.py -q` → PASS.

**Step 5: Commit**
`git add tests/integration/extraction docker-compose.yml docs/plans/2026-02-26-phase1-phase2-completion-report.md && git commit -m "test: add extraction e2e coverage"`

---
