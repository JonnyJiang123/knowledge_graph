<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import NeighborResultDrawer from '@/components/graph/NeighborResultDrawer.vue'
import GraphProjectSelector from '@/components/graph/GraphProjectSelector.vue'
import { useGraphStore } from '@/stores/graph'
import type { GraphProjectCreatePayload, NeighborRun } from '@/types/graph'

const graphStore = useGraphStore()
const drawerVisible = ref(false)
const selectedRun = ref<NeighborRun | null>(null)
const form = reactive({
  projectId: '',
  entityId: '',
  depth: 1,
  limit: undefined as number | undefined,
})

onMounted(async () => {
  try {
    await graphStore.loadProjects()
    form.projectId = graphStore.currentProjectId
  } catch (error) {
    console.error(error)
  }
})

function handleProjectSelection(id: string) {
  graphStore.setCurrentProject(id)
  form.projectId = id
}

async function handleCreateProject(payload: GraphProjectCreatePayload) {
  try {
    await graphStore.saveProject(payload)
    form.projectId = graphStore.currentProjectId
    ElMessage.success('图谱项目创建成功')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建项目失败')
  }
}

async function runNeighbors() {
  if (!form.projectId || !form.entityId) {
    ElMessage.warning('请选择项目并输入实体ID')
    return
  }
  try {
    await graphStore.fetchNeighbors(form.projectId, {
      entityId: form.entityId,
      depth: form.depth,
      limit: form.limit,
    })
    ElMessage.success('邻居查询已提交')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '获取邻居失败')
  }
}

function openResult(run: NeighborRun) {
  selectedRun.value = run
  drawerVisible.value = true
}

async function replayRun(run: NeighborRun) {
  // Populate form with run parameters
  form.projectId = run.projectId
  form.entityId = run.entityId
  form.depth = run.depth
  form.limit = run.limit
  // Execute the neighbor query
  await runNeighbors()
}
</script>

<template>
  <div class="graph-jobs">
    <el-card>
      <template #header>
        <div class="jobs-header">
          <div>
            <h2>图谱任务</h2>
            <p class="hint">运行邻居查询并查看最近的结果。</p>
          </div>
        </div>
      </template>

      <div class="filters">
        <GraphProjectSelector
          :model-value="form.projectId"
          :projects="graphStore.projects"
          :loading="graphStore.loading.projects"
          @update:modelValue="handleProjectSelection"
          @create="handleCreateProject"
        />
        <el-form label-width="140px" class="neighbor-form">
          <el-form-item label="实体ID">
            <el-input v-model="form.entityId" placeholder="实体UUID" data-test="entity-id-input" />
          </el-form-item>
          <el-form-item label="深度">
            <el-slider
              v-model="form.depth"
              :min="1"
              :max="3"
              show-input
              input-size="small"
            />
          </el-form-item>
          <el-form-item label="限制（可选）">
            <el-input-number v-model="form.limit" :min="1" :max="100" />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="graphStore.loading.neighbors"
              data-test="run-neighbors"
              @click="runNeighbors"
            >
              运行邻居查询
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="graphStore.neighborRuns" stripe>
        <el-table-column prop="entityId" label="实体" width="200" />
        <el-table-column prop="depth" label="深度" width="100" />
        <el-table-column
          label="节点"
          width="100"
          :formatter="(_, __, row) => row?.result?.entities?.length ?? 0"
        />
        <el-table-column
          label="关系"
          width="120"
          :formatter="(_, __, row) => row?.result?.relations?.length ?? 0"
 />
        <el-table-column
          prop="createdAt"
          label="创建时间"
          :formatter="(_, __, row) => new Date(row.createdAt).toLocaleString()"
        />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" data-test="neighbor-row-details" @click="openResult(row)">详情</el-button>
            <el-button link type="primary" data-test="neighbor-row-replay" @click="replayRun(row)">重新运行</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <NeighborResultDrawer
      v-model="drawerVisible"
      :run="selectedRun"
    />
  </div>
</template>

<style scoped>
.graph-jobs {
  padding: 24px;
}
.jobs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filters {
  margin-bottom: 24px;
}
.neighbor-form {
  margin-top: 16px;
  max-width: 720px;
}
.hint {
  color: var(--el-text-color-secondary);
}
</style>
