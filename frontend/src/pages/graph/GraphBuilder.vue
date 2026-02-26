<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import GraphProjectSelector from '@/components/graph/GraphProjectSelector.vue'
import EntityComposer from '@/components/graph/EntityComposer.vue'
import RelationComposer from '@/components/graph/RelationComposer.vue'
import { useGraphStore } from '@/stores/graph'
import type {
  GraphProjectCreatePayload,
  GraphEntityDraft,
  GraphRelationDraft,
} from '@/types/graph'

const graphStore = useGraphStore()
const activeStep = ref(0)
const submitting = ref(false)

onMounted(async () => {
  try {
    await graphStore.loadProjects()
  } catch (error) {
    console.error(error)
  }
  if (!graphStore.entityDrafts.length) {
    graphStore.addEntityDraft()
  }
})

watch(
  () => graphStore.entityDrafts.length,
  (count) => {
    if (count === 0) {
      graphStore.addEntityDraft()
    }
  },
)

const canProceed = computed(() => {
  if (activeStep.value === 0) {
    return Boolean(graphStore.currentProjectId)
  }
  if (activeStep.value === 1) {
    return graphStore.entityDrafts.every((draft) => draft.external_id && draft.type)
  }
  if (activeStep.value === 2) {
    return graphStore.relationDrafts.every(
      (draft) => draft.source_id && draft.target_id && draft.type,
    )
  }
  return true
})

const isLastStep = computed(() => activeStep.value === 3)

function nextStep() {
  if (!canProceed.value) return
  if (activeStep.value < 3) {
    activeStep.value += 1
  } else {
    submitGraph()
  }
}

function prevStep() {
  if (activeStep.value === 0) return
  activeStep.value -= 1
}

async function handleCreateProject(payload: GraphProjectCreatePayload) {
  try {
    await graphStore.saveProject(payload)
    ElMessage.success('Graph project created')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : 'Failed to create project')
  }
}

function handleEntityChange(event: { id: string; patch: Partial<GraphEntityDraft> }) {
  graphStore.updateEntityDraft(event.id, event.patch)
}

function handleRelationChange(event: { id: string; patch: Partial<GraphRelationDraft> }) {
  graphStore.updateRelationDraft(event.id, event.patch)
}

async function submitGraph() {
  if (submitting.value) return
  submitting.value = true
  try {
    const summary = await graphStore.persistGraphDrafts()
    ElMessage.success(`Graph persisted: ${summary.entities} entities, ${summary.relations} relations`)
    graphStore.resetDrafts()
    graphStore.addEntityDraft()
    activeStep.value = 0
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : 'Failed to persist graph')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="graph-builder">
    <el-card>
      <template #header>
        <div class="builder-header">
          <div>
            <h2>Graph Builder</h2>
            <p class="hint">Create graph projects, entities, and relations in a guided flow.</p>
          </div>
        </div>
      </template>

      <el-steps :active="activeStep" finish-status="success" align-center>
        <el-step title="Project" description="Select or create target graph project" />
        <el-step title="Entities" description="Draft nodes to persist" />
        <el-step title="Relations" description="Connect saved nodes" />
        <el-step title="Review" description="Submit to backend" />
      </el-steps>

      <section class="step-content">
        <div v-if="activeStep === 0">
          <GraphProjectSelector
            :model-value="graphStore.currentProjectId"
            :projects="graphStore.projects"
            :loading="graphStore.loading.projects"
            @update:modelValue="graphStore.setCurrentProject"
            @create="handleCreateProject"
          />
        </div>

        <div v-else-if="activeStep === 1">
          <EntityComposer
            :drafts="graphStore.entityDrafts"
            @add="graphStore.addEntityDraft"
            @change="handleEntityChange"
            @remove="graphStore.removeEntityDraft"
            @persist="graphStore.persistEntityDraft"
          />
        </div>

        <div v-else-if="activeStep === 2">
          <RelationComposer
            :drafts="graphStore.relationDrafts"
            @add="graphStore.addRelationDraft"
            @change="handleRelationChange"
            @remove="graphStore.removeRelationDraft"
            @persist="graphStore.persistRelationDraft"
          />
        </div>

        <div v-else>
          <h3>Review summary</h3>
          <p>
            {{ graphStore.entityDrafts.length }} entities ·
            {{ graphStore.relationDrafts.length }} relations
          </p>
          <el-table :data="graphStore.entityDrafts" style="width: 100%">
            <el-table-column prop="external_id" label="External ID" width="180" />
            <el-table-column prop="type" label="Type" width="140" />
            <el-table-column label="Status">
              <template #default="{ row }">
                <el-tag :type="row.status === 'saved' ? 'success' : 'warning'">
                  {{ row.status || 'draft' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <div class="actions">
        <el-button @click="prevStep" :disabled="activeStep === 0">Back</el-button>
        <el-button
          type="primary"
          :disabled="!canProceed"
          :loading="submitting || graphStore.loading.persist"
          data-test="submit-graph"
          @click="nextStep"
        >
          {{ isLastStep ? 'Submit graph' : 'Next' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.graph-builder {
  padding: 24px;
}
.builder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint {
  color: var(--el-text-color-secondary);
}
.step-content {
  margin-top: 24px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  gap: 12px;
}
</style>
