<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Search, Connection, ChatDotRound, Star, Delete } from '@element-plus/icons-vue'
import { useQueryStore } from '@/stores/query'
import { useProjectStore } from '@/stores/project'
import SearchBar from '@/components/query/SearchBar.vue'
import NLQueryInput from '@/components/query/NLQueryInput.vue'
import PathFinder from '@/components/query/PathFinder.vue'
import ResultList from '@/components/query/ResultList.vue'
import type { SearchParams, PathParams } from '@/types/query'

const queryStore = useQueryStore()
const projectStore = useProjectStore()

const activeTab = ref<'entity' | 'path' | 'nl'>('entity')
const searchKeyword = ref('')
const nlQuery = ref('')
const showSaveDialog = ref(false)
const saveQueryName = ref('')

// 当前项目ID
const currentProjectId = computed(() => projectStore.currentProject?.id || '')

// 模拟的实体选项（实际应该从后端获取）
const entityOptions = ref([
  { id: 'ent-1', name: '阿里巴巴', type: '公司' },
  { id: 'ent-2', name: '腾讯', type: '公司' },
  { id: 'ent-3', name: '马云', type: '人物' },
  { id: 'ent-4', name: '字节跳动', type: '公司' },
  { id: 'ent-5', name: '美团', type: '公司' },
])

const availableEntityTypes = ['公司', '人物', '产品', '地点', '事件']

onMounted(() => {
  projectStore.fetchProjects()
  queryStore.loadSavedQueries()
})

async function handleEntitySearch(params: SearchParams) {
  if (!currentProjectId.value) {
    // 如果没有项目ID，直接使用原来的方法（向后兼容）
    await queryStore.searchEntities(params)
    return
  }
  // 使用新的 API 方法，传入 projectId
  await queryStore.searchEntities(currentProjectId.value, params)
}

async function handlePathSearch(params: PathParams) {
  await queryStore.findPaths(params)
}

async function handleNLSubmit(query: string) {
  await queryStore.naturalLanguageQuery(query)
}

function handleEntityClick(entity: any) {
  console.log('Entity clicked:', entity)
  // 可以打开实体详情抽屉或导航到实体页面
}

function handlePathClick(path: any) {
  console.log('Path clicked:', path)
  // 可以在图谱中显示路径
}

function openSaveDialog() {
  if (!queryStore.currentResults) return
  saveQueryName.value = ''
  showSaveDialog.value = true
}

async function confirmSaveQuery() {
  if (!saveQueryName.value || !queryStore.currentResults) return

  let params: SearchParams | PathParams | { query: string }
  
  if (activeTab.value === 'entity') {
    params = {
      keyword: searchKeyword.value,
      entityTypes: [],
    }
  } else if (activeTab.value === 'path') {
    params = {
      startId: '',
      endId: '',
    }
  } else {
    params = { query: nlQuery.value }
  }

  await queryStore.saveQuery(saveQueryName.value, params, activeTab.value)
  showSaveDialog.value = false
}

async function loadSavedQuery(saved: any) {
  // 根据保存的查询类型加载
  console.log('Loading saved query:', saved)
}

function handleSortChange(field: any, order: any) {
  console.log('Sort:', field, order)
  // 实现排序逻辑
}

function handlePageChange(page: number) {
  console.log('Page:', page)
  // 实现分页逻辑
}
</script>

<template>
  <div class="query-builder">
    <el-row :gutter="24">
      <!-- 左侧查询区域 -->
      <el-col :xs="24" :lg="10" :xl="8">
        <el-card class="query-card">
          <template #header>
            <div class="card-header">
              <h2>查询构建器</h2>
              <p class="hint">选择查询类型并输入条件</p>
            </div>
          </template>

          <el-tabs v-model="activeTab" type="border-card">
            <!-- 实体搜索 -->
            <el-tab-pane name="entity">
              <template #label>
                <el-icon><Search /></el-icon>
                实体搜索
              </template>
              <SearchBar
                v-model="searchKeyword"
                :entity-types="[]"
                :available-types="availableEntityTypes"
                :history="queryStore.searchHistory"
                :loading="queryStore.loading"
                @search="handleEntitySearch"
                @clear-history="queryStore.clearHistory"
              />
            </el-tab-pane>

            <!-- 路径查找 -->
            <el-tab-pane name="path">
              <template #label>
                <el-icon><Connection /></el-icon>
                路径查找
              </template>
              <PathFinder
                :loading="queryStore.loading"
                :entity-options="entityOptions"
                @search="handlePathSearch"
              />
            </el-tab-pane>

            <!-- 自然语言查询 -->
            <el-tab-pane name="nl">
              <template #label>
                <el-icon><ChatDotRound /></el-icon>
                自然语言
              </template>
              <NLQueryInput
                v-model="nlQuery"
                :loading="queryStore.loading"
                :cypher="queryStore.currentResults?.cypher"
                :answer="queryStore.currentResults?.answer"
                @submit="handleNLSubmit"
              />
            </el-tab-pane>
          </el-tabs>

          <!-- 已保存查询 -->
          <div v-if="queryStore.savedQueries.length > 0" class="saved-queries">
            <div class="saved-header">
              <el-icon><Star /></el-icon>
              <span>已保存的查询</span>
            </div>
            <el-scrollbar max-height="150px">
              <div
                v-for="query in queryStore.savedQueries"
                :key="query.id"
                class="saved-item"
              >
                <span class="saved-name" @click="loadSavedQuery(query)">{{ query.name }}</span>
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="queryStore.deleteSavedQuery(query.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </el-scrollbar>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧结果区域 -->
      <el-col :xs="24" :lg="14" :xl="16">
        <el-card class="result-card">
          <template #header>
            <div class="result-header">
              <div>
                <h3>查询结果</h3>
                <p v-if="queryStore.currentResults" class="result-meta">
                  共 {{ queryStore.currentResults.total }} 条结果
                </p>
              </div>
              <el-button
                v-if="queryStore.currentResults"
                type="primary"
                size="small"
                plain
                @click="openSaveDialog"
              >
                <el-icon><Star /></el-icon>
                保存查询
              </el-button>
            </div>
          </template>

          <div v-if="!queryStore.currentResults && !queryStore.loading" class="empty-state">
            <el-empty description="请输入查询条件并点击搜索">
              <template #image>
                <el-icon :size="80" color="#909399"><Search /></el-icon>
              </template>
            </el-empty>
          </div>

          <ResultList
            v-else-if="queryStore.currentResults"
            :entities="queryStore.currentResults.entities"
            :paths="queryStore.currentResults.paths"
            :total="queryStore.currentResults.total"
            :loading="queryStore.loading"
            @entity-click="handleEntityClick"
            @path-click="handlePathClick"
            @sort-change="handleSortChange"
            @page-change="handlePageChange"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 保存查询对话框 -->
    <el-dialog
      v-model="showSaveDialog"
      title="保存查询"
      width="400px"
    >
      <el-form>
        <el-form-item label="查询名称">
          <el-input
            v-model="saveQueryName"
            placeholder="输入查询名称..."
            @keyup.enter="confirmSaveQuery"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!saveQueryName"
          @click="confirmSaveQuery"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.query-builder {
  padding: 24px;
}

.query-card {
  height: 100%;
}

.card-header h2 {
  margin: 0 0 4px;
  font-size: 18px;
}

.hint {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.result-card {
  min-height: 600px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-header h3 {
  margin: 0 0 4px;
  font-size: 18px;
}

.result-meta {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.saved-queries {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
}

.saved-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.saved-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.saved-name {
  flex: 1;
  cursor: pointer;
  color: var(--el-text-color-primary);
}

.saved-name:hover {
  color: var(--el-color-primary);
}
</style>
