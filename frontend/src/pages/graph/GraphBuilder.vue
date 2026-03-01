<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import GraphProjectSelector from '@/components/graph/GraphProjectSelector.vue'
import EntityComposer from '@/components/graph/EntityComposer.vue'
import RelationComposer from '@/components/graph/RelationComposer.vue'
import GraphCanvas from '@/components/graph/GraphCanvas.vue'
import { useGraphStore } from '@/stores/graph'
import type {
  GraphProjectCreatePayload,
  GraphEntityDraft,
  GraphRelationDraft,
} from '@/types/graph'
import type { GraphData } from '@/types/visualization'

const router = useRouter()
const graphStore = useGraphStore()
const activeStep = ref(0)
const submitting = ref(false)

// 可视化预览相关
const previewLayoutMode = ref<'force' | 'hierarchical' | 'circular'>('force')
const previewSelectedNodes = ref<string[]>([])
const previewZoomLevel = ref(1)

// 将草稿转换为GraphCanvas所需的数据格式
const previewGraphData = computed<GraphData>(() => {
  // 从实体草稿生成节点
  const nodes = graphStore.entityDrafts
    .filter((draft) => draft.external_id && draft.status === 'saved')
    .map((draft, index) => ({
      id: draft.external_id,
      name: draft.external_id,
      category: getCategoryIndex(draft.type),
      symbolSize: 50,
      value: 1,
    }))

  // 从关系草稿生成边
  const edges = graphStore.relationDrafts
    .filter((draft) => draft.source_id && draft.target_id && draft.status === 'saved')
    .map((draft) => ({
      source: draft.source_id,
      target: draft.target_id,
      relation: draft.type || '关联',
      value: 1,
    }))

  // 获取所有唯一的实体类型作为类别
  const types = [...new Set(graphStore.entityDrafts.map((d) => d.type).filter(Boolean))]

  return {
    nodes,
    edges,
    categories: types.length > 0 ? types : ['实体'],
  }
})

// 获取类型对应的类别索引
const categoryMap = ref<Map<string, number>>(new Map())
function getCategoryIndex(type: string | undefined): number {
  if (!type) return 0
  if (!categoryMap.value.has(type)) {
    categoryMap.value.set(type, categoryMap.value.size)
  }
  return categoryMap.value.get(type)!
}

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

const isLastStep = computed(() => activeStep.value === 4)
const isReviewStep = computed(() => activeStep.value === 3)
const isPreviewStep = computed(() => activeStep.value === 4)

function nextStep() {
  if (!canProceed.value) return
  if (activeStep.value < 4) {
    activeStep.value += 1
  } else {
    submitGraph()
  }
}

function goToVisualization() {
  router.push('/graph/visualization')
}

function prevStep() {
  if (activeStep.value === 0) return
  activeStep.value -= 1
}

async function handleCreateProject(payload: GraphProjectCreatePayload) {
  try {
    await graphStore.saveProject(payload)
    ElMessage.success('图谱项目创建成功')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建项目失败')
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
    ElMessage.success(`图谱已保存: ${summary.entities} 个实体, ${summary.relations} 个关系`)
    // 保存成功后询问是否查看
    ElMessage.success('保存成功！正在跳转到可视化页面...')
    setTimeout(() => {
      router.push('/graph/visualization')
    }, 1000)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存图谱失败')
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
            <h2>图谱构建</h2>
            <p class="hint">在引导流程中创建图谱项目、实体和关系</p>
          </div>
        </div>
      </template>

      <el-steps :active="activeStep" finish-status="success" align-center>
        <el-step title="选择项目" description="选择或创建图谱项目" />
        <el-step title="实体定义" description="定义要保存的节点" />
        <el-step title="关系建立" description="连接已保存的节点" />
        <el-step title="提交审核" description="提交到后端保存" />
        <el-step title="可视化预览" description="预览生成的图谱" />
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

        <div v-else-if="activeStep === 3">
          <h3>提交审核</h3>
          <p class="summary-text">
            <el-statistic title="实体数量" :value="graphStore.entityDrafts.filter(d => d.status === 'saved').length" />
            <el-statistic title="关系数量" :value="graphStore.relationDrafts.filter(d => d.status === 'saved').length" />
          </p>
          <el-table :data="graphStore.entityDrafts" style="width: 100%" max-height="300">
            <el-table-column prop="external_id" label="外部ID" width="180" />
            <el-table-column prop="type" label="类型" width="140" />
            <el-table-column label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'saved' ? 'success' : 'warning'">
                  {{ row.status === 'saved' ? '已保存' : '草稿' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-else-if="activeStep === 4" class="preview-step">
          <div class="preview-header">
            <h3>可视化预览</h3>
            <el-button type="primary" :icon="View" @click="goToVisualization">
              查看完整图谱
            </el-button>
          </div>
          <p class="preview-desc">
            已保存 {{ previewGraphData.nodes.length }} 个实体，
            {{ previewGraphData.edges.length }} 个关系
          </p>
          <div class="preview-canvas-container">
            <GraphCanvas
              v-if="previewGraphData.nodes.length > 0"
              :data="previewGraphData"
              :layout-mode="previewLayoutMode"
              :selected-nodes="previewSelectedNodes"
              :zoom-level="previewZoomLevel"
              @update:zoom-level="previewZoomLevel = $event"
              @node-click="(id) => previewSelectedNodes = previewSelectedNodes.includes(id) ? previewSelectedNodes.filter(n => n !== id) : [...previewSelectedNodes, id]"
              @canvas-click="previewSelectedNodes = []"
            />
            <el-empty v-else description="暂无已保存的实体和关系，请先在前面的步骤中添加" />
          </div>
        </div>
      </section>

      <div class="actions">
        <el-button @click="prevStep" :disabled="activeStep === 0">上一步</el-button>
        <el-button
          v-if="isReviewStep"
          type="success"
          :disabled="!canProceed"
          :loading="submitting || graphStore.loading.persist"
          data-test="submit-graph"
          @click="submitGraph"
        >
          保存图谱
        </el-button>
        <el-button
          v-else-if="isPreviewStep"
          type="primary"
          :icon="View"
          @click="goToVisualization"
        >
          查看完整图谱
        </el-button>
        <el-button
          v-else
          type="primary"
          :disabled="!canProceed"
          @click="nextStep"
        >
          下一步
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
.summary-text {
  display: flex;
  gap: 48px;
  margin: 16px 0;
}
.preview-step {
  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .preview-desc {
    color: var(--el-text-color-secondary);
    margin-bottom: 16px;
  }
  .preview-canvas-container {
    height: 400px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    overflow: hidden;
    background: var(--el-fill-color-light);
  }
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
