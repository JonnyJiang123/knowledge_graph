# Graph Builder & Jobs Frontend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ship dedicated Vue 3 flows for graph project/entity creation and neighbor job review, fully wired to the new backend `/api/graph` endpoints.

**Architecture:** Add a graph-specific API client plus a Pinia store that manages graph projects, entity/relation drafts, and neighbor query results. Build standalone wizard and jobs pages under `/graph/...`, each composed from focused components. Reuse Element Plus steppers/tables and existing notification infrastructure; keep all API calls centralized in the new store. Testing relies on Vitest with API mocks similar to the ingestion suite.

**Tech Stack:** Vue 3, TypeScript, Pinia, Element Plus, Axios, Vue Router, Vitest, @vue/test-utils.

---

### Task 1: Graph API Client

**Files:**
- Create: `frontend/src/api/graph.ts`
- Modify: `frontend/src/api/index.ts` (if re-exporting) *skip if not needed*

**Step 1: Scaffold API module**

Create `frontend/src/api/graph.ts` exporting typed functions:
```ts
import { apiClient } from './client'
import type { GraphProject, GraphEntityPayload, GraphRelationPayload, NeighborResponse } from '@/types/graph'

export async function fetchGraphProjects() { return (await apiClient.get('/graph/projects')).data }
export async function createGraphProject(payload: GraphProjectPayload) { ... }
// include createEntity, createRelation, fetchNeighbors
```
Use backend contract naming (see `backend/src/api/schemas/{project,graph}.py`).

**Step 2: Verify lint/type**

Run: `cd frontend && npm run build`
Expected: TS build passes (ensures new module compiles).

### Task 2: Pinia Graph Store

**Files:**
- Create: `frontend/src/stores/graph.ts`
- Modify: `frontend/src/stores/index.ts` (if there’s a barrel export)

**Step 1: Define state + actions**

Implement Pinia store:
```ts
export const useGraphStore = defineStore('graph', {
  state: () => ({
    projects: [] as GraphProject[],
    currentProjectId: '',
    entityDrafts: [] as GraphEntityDraft[],
    relationDrafts: [] as GraphRelationDraft[],
    neighborRuns: [] as NeighborRun[],
    loading: false,
  }),
  actions: {
    async loadProjects() { this.projects = await fetchGraphProjects() },
    async saveProject(payload) { ... },
    async addEntityDraft(draft) { ... },
    async persistEntity(draft) { await createGraphEntity(...) },
    async fetchNeighbors(opts) { this.neighborRuns.unshift(await fetchNeighbors(...)) },
  },
})
```
Handle errors via existing notification store (`useNotificationStore().error(...)`).

**Step 2: Type definitions**

Add reusable interfaces in `frontend/src/types/graph.ts`.

**Step 3: Run unit tests for store skeleton**

`cd frontend && npm run test:unit -- stores/__tests__/graph.spec.ts`
(Empty placeholder test for now; will add real specs in Task 6.)

### Task 3: Graph Builder Page & Components

**Files:**
- Create: `frontend/src/pages/graph/GraphBuilder.vue`
- Create: `frontend/src/components/graph/GraphProjectSelector.vue`
- Create: `frontend/src/components/graph/EntityComposer.vue`
- Create: `frontend/src/components/graph/RelationComposer.vue`
- Modify: `frontend/src/components/index.d.ts` (if auto-imports needed)

**Step 1: Components**

Implement project selector with Element Plus `<el-select>` listing `graphStore.projects` plus “Create new” dialog. Entity composer collects type, labels, properties; relation composer references selected entity drafts + relation type.

**Step 2: Page layout**

`GraphBuilder.vue`:
```vue
<template>
  <el-steps :active="activeStep">...</el-steps>
  <component :is="currentStep" />
  <el-button @click="onSubmitWizard" :loading="graphStore.loading">Submit Graph</el-button>
</template>
```
Steps: project selection → entities → relations → review. On submit, iterate drafts calling store actions; show toast on success and reset drafts.

**Step 3: Manual QA**

Run `npm run dev`, navigate to `/graph/builder`, ensure you can add drafts and see them persist in the summary panel.

### Task 4: Graph Jobs Page (Neighbor Runner)

**Files:**
- Create: `frontend/src/pages/graph/GraphJobs.vue`
- Create: `frontend/src/components/graph/NeighborResultDrawer.vue` (for expandable view)

**Step 1: Page**

Provide filters (project select, entity ID input, depth slider). On “Run neighbors,” call `graphStore.fetchNeighbors`. Render results in Element Plus table showing entity count, relation count, timestamp, and action button to open drawer.

**Step 2: Visualization hook**

Inside `NeighborResultDrawer`, reuse existing `components/graph/GraphCanvas.vue` (if available) or show JSON for MVP. Accept nodes/edges props and handle empty states.

**Step 3: Manual QA**

`npm run dev`, navigate to `/graph/jobs`, run sample neighbor query; verify store updates and drawer renders results.

### Task 5: Router & Layout Integration

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/layouts/DefaultLayout.vue` (sidebar links)

**Step 1: Add routes**

Insert under authenticated children:
```ts
{
  path: 'graph/builder',
  name: 'GraphBuilder',
  component: () => import('@/pages/graph/GraphBuilder.vue'),
},
{
  path: 'graph/jobs',
  name: 'GraphJobs',
  component: () => import('@/pages/graph/GraphJobs.vue'),
},
```

**Step 2: Navigation**

Add sidebar menu entries pointing to new routes. Ensure active-class styling matches existing pattern.

**Step 3: Smoke test**

`npm run dev`, click new sidebar links to confirm navigation + auth guards.

### Task 6: Unit Tests & Docs

**Files:**
- Create: `frontend/src/stores/__tests__/graph.spec.ts`
- Create: `frontend/src/pages/graph/__tests__/graphBuilder.spec.ts`
- Create: `frontend/src/pages/graph/__tests__/graphJobs.spec.ts`
- Modify: `README.md` (frontend section)

**Step 1: Store tests**

Use Vitest + `vi.mock('@/api/graph')` to verify `loadProjects`, `saveProject`, and `fetchNeighbors` update state/handle errors.

**Step 2: Component tests**

For builder:
```ts
it('submits entity drafts to store', async () => {
  const wrapper = mount(GraphBuilder, { global: { plugins: [pinia] } })
  await wrapper.find('[data-test="add-entity"]').trigger('click')
  expect(graphStore.persistEntity).toHaveBeenCalled()
})
```
For jobs: ensure running neighbors calls store and renders results table.

**Step 3: Run targeted tests**

`cd frontend && npm run test:unit -- stores/__tests__/graph.spec.ts pages/graph/__tests__/graphBuilder.spec.ts pages/graph/__tests__/graphJobs.spec.ts`

**Step 4: README update**

Add bullet noting `/graph/builder` & `/graph/jobs` flows and dev instructions (e.g., “Run `npm run dev` and open Graph Builder to create projects/entities”).

---

Plan complete and saved to `docs/plans/2026-02-14-graph-frontend.md`. Two execution options:

1. **Subagent-Driven (this session)** – I dispatch a fresh subagent per task with reviews between steps.
2. **Parallel Session** – Start a new session with executing-plans, batch the tasks, and report back after checkpoints.

Which approach would you like to use?
