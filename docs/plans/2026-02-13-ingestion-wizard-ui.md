# 2026-02-13-ingestion-wizard-ui Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ship the ingestion wizard and job list UI slices wired to the ingestion Pinia store and backend API.

**Architecture:** Build composable Vue 3 components (Element Plus) that consume the existing useIngestionStore. The wizard coordinates step components for source selection, file upload, rule configuration, preview, and submission, while the job list page reads store jobs and polls for updates via the API. Routing updates expose /ingestion/wizard and /ingestion/jobs under the default layout.

**Tech Stack:** Vue 3 + TypeScript, Pinia, Element Plus, Vitest, Vue Test Utils.

---

### Task 1: Wizard Components & Store Integration

**Files:**
- Create: rontend/src/components/ingestion/SourceSelector.vue
- Create: rontend/src/components/ingestion/MySQLConnectorForm.vue
- Create: rontend/src/components/ingestion/FileUploadStep.vue
- Create: rontend/src/components/ingestion/CleaningRuleBuilder.vue
- Create: rontend/src/components/ingestion/PreviewTable.vue
- Create: rontend/src/components/ingestion/SubmissionPanel.vue
- Modify: rontend/src/stores/ingestion.ts
- Test: rontend/src/components/ingestion/__tests__/cleaningRuleBuilder.spec.ts

**Step 1: Write failing component tests**
`	s
// cleaningRuleBuilder emits updated rules
`
Run: cd frontend && npm run test:unit -- CleaningRuleBuilder ¡ú FAIL.

**Step 2: Implement components**
- Compose Element Plus controls, accept props for sources/rules, emit update events.
- Add helper store actions (e.g., setSelectedSource, setWizardStep).

**Step 3: Re-run tests**

pm run test:unit -- CleaningRuleBuilder
Expected: PASS.

**Step 4: Commit**
git add frontend/src/components/ingestion frontend/src/stores/ingestion.ts ¡ú git commit -m "feat(frontend): add ingestion wizard components".

### Task 2: Wizard Page & Routing

**Files:**
- Create: rontend/src/pages/ingestion/IngestionWizard.vue
- Modify: rontend/src/router/index.ts
- Modify: rontend/src/layouts/DefaultLayout.vue
- Test: rontend/src/pages/ingestion/__tests__/wizard.spec.ts

**Step 1: Write failing page test**
`	s
// mount IngestionWizard, step buttons move through flow
`
Run: 
pm run test:unit -- wizard ¡ú FAIL.

**Step 2: Implement IngestionWizard**
- Use <el-steps> to manage step indexes.
- Inject store, call etchTemplates, etchSources, uploadFile, submitMysqlImport on CTA.
- Wire SourceSelector/MySQL form/etc. components via props/events.

**Step 3: Update router/layout**
- Add /ingestion/wizard route + nav link.

**Step 4: Re-run tests**

pm run test:unit -- wizard
Expected: PASS.

**Step 5: Commit**
git add frontend/src/pages/ingestion frontend/src/router/index.ts frontend/src/layouts/DefaultLayout.vue ¡ú git commit -m "feat(frontend): add ingestion wizard page".

### Task 3: Job List Page & Polling

**Files:**
- Create: rontend/src/components/ingestion/JobProgress.vue
- Create: rontend/src/pages/ingestion/JobList.vue
- Modify: rontend/src/router/index.ts
- Test: rontend/src/pages/ingestion/__tests__/jobList.spec.ts

**Step 1: Write failing tests**
`	s
// job list renders jobs, triggers refresh/polling intervals
`
Run: 
pm run test:unit -- jobList ¡ú FAIL.

**Step 2: Implement JobProgress + JobList**
- JobProgress shows status badge, <el-progress> for percent.
- JobList fetches jobs on mount, uses setInterval/onUnmounted to poll efreshJob for running ones.

**Step 3: Update router nav**
- Ensure /ingestion/jobs route is accessible.

**Step 4: Run unit tests**

pm run test:unit -- jobList
Expected: PASS.

**Step 5: Commit**
git add frontend/src/components/ingestion/JobProgress.vue frontend/src/pages/ingestion/JobList.vue frontend/src/router/index.ts ¡ú git commit -m "feat(frontend): add ingestion job list".

### Task 4: End-to-End UI Smoke + Docs

**Files:**
- Modify: README.md
- Optional: docs/runbooks/ingestion.md

**Step 1: Run full frontend tests**

pm run test:unit
Expected: PASS.

**Step 2: Manual smoke (document)**
- Describe manual steps: open wizard, upload sample file, view jobs page.

**Step 3: Update docs**
- Mention new routes/components in README or runbook.

**Step 4: Commit**
git add README.md docs/runbooks/ingestion.md ¡ú git commit -m "docs: add ingestion ui usage".
