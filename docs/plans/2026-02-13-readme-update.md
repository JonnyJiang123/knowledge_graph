# README Refresh Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update the root README so newcomers understand the full knowledge_graph platform, ingestion slice, and how to run services.

**Architecture:** Reuse existing documentation (docs/plans/2026-02-09-architecture-design.md, docs/plans/2026-02-11-phase2-ingestion.md, 知识图谱prd.md) to summarize backend (FastAPI, Celery, Redis, MySQL, Neo4j) and frontend (Vue 3, Pinia) subsystems plus workflows. README must link to these docs and flag async worker requirements.

**Tech Stack:** Markdown, PowerShell tooling, git.

---

### Task 1: Collect Source Material

**Files:**
- Read: 知识图谱prd.md
- Read: docs/plans/2026-02-09-architecture-design.md
- Read: docs/plans/2026-02-11-phase2-ingestion.md
- Read: docker/docker-compose.yml

**Step 1: Review product brief**

Run: Get-Content -Raw '.worktrees/phase2-ingestion/知识图谱prd.md' | more
Expected: Note product goals, personas, terminology for README overview.

**Step 2: Review architecture doc**

Run: Get-Content -Raw 'docs/plans/2026-02-09-architecture-design.md' | more
Expected: Capture service layout (backend, frontend, databases, infra) to summarize architecture.

**Step 3: Review ingestion plan**

Run: Get-Content -Raw 'docs/plans/2026-02-11-phase2-ingestion.md' | more
Expected: Identify ingestion pipeline features (file + MySQL, cleaning rules, Celery worker) for README sections.

**Step 4: Inspect docker compose**

Run: Get-Content -Raw 'docker/docker-compose.yml' | more
Expected: Gather service names/commands to document dev environment.

### Task 2: Rewrite README.md

**Files:**
- Modify: README.md

**Step 1: Draft outline**

Add sections: Introduction, System Architecture, Backend Services, Frontend Experience, Async Processing & Workers, Local Development (docker + scripts), Documentation Map.

**Step 2: Populate overview**

Describe product scope referencing insights from 知识图谱prd.md; include bullet list of key capabilities and data sources in README.

**Step 3: Detail architecture and services**

Summarize backend stack (FastAPI, SQLAlchemy/MySQL, Neo4j, Redis, Celery), storage directories, ingestion flows referencing docs/plans/2026-02-11-phase2-ingestion.md. Mention MySQL + Neo4j connection env vars and Celery worker command.

**Step 4: Document frontend & workflow**

Explain Vue 3 wizard, Pinia stores, Element Plus UI, linking to ingestion plan for wizard steps.

**Step 5: Add dev workflow**

List commands: scripts/dev-start.ps1, docker compose up, cd backend && uvicorn ..., celery -A src.infrastructure.queue.celery_app.celery_app worker -Q ingestion -l info, cd frontend && npm run dev, tests pytest, 
pm run test:unit.

**Step 6: Insert documentation map**

Add table/list linking to 知识图谱prd.md, docs/plans/2026-02-09-architecture-design.md, docs/plans/2026-02-11-phase2-ingestion.md, docs/plans/2026-02-09-phase1-implementation.md.

### Task 3: Verify, Commit, and Push

**Files:**
- README.md
- docs/plans/2026-02-13-readme-update.md

**Step 1: Proofread Markdown**

Run: Get-Content README.md
Expected: Ensure sections are present, links relative, environment variables accurate.

**Step 2: Git status & stage**

Run: git status -sb
Expected: Only README + plan modified.
Run: git add README.md docs/plans/2026-02-13-readme-update.md

**Step 3: Commit**

Run: git commit -m "docs: refresh top-level readme"
Expected: Commit succeeds.

**Step 4: Push**

Run: git push origin 0.0.1
Expected: Remote update success (report error if push blocked).