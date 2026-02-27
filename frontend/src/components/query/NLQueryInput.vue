<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChatDotRound, Magic, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: string
  loading?: boolean
  cypher?: string | null
  answer?: string | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', query: string): void
}>()

const showExamples = ref(false)

const exampleQueries = [
  '查找所有与"阿里巴巴"有直接投资的机构',
  '查询"腾讯"和"字节跳动"之间的最短路径',
  '统计医疗健康行业的企业数量',
  '找出投资轮次最多的前10个投资人',
]

const hasInput = computed(() => props.modelValue.trim().length > 0)
const showResults = computed(() => Boolean(props.cypher || props.answer))

function handleSubmit() {
  if (!hasInput.value) return
  emit('submit', props.modelValue.trim())
}

function handleExampleClick(example: string) {
  emit('update:modelValue', example)
  showExamples.value = false
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div class="nl-query-input">
    <div class="input-header">
      <div class="input-title">
        <el-icon><ChatDotRound /></el-icon>
        <span>自然语言查询</span>
      </div>
      <el-button
        link
        type="primary"
        size="small"
        @click="showExamples = !showExamples"
      >
        <el-icon><Magic /></el-icon>
        示例查询
      </el-button>
    </div>

    <div class="input-wrapper">
      <el-input
        :model-value="modelValue"
        type="textarea"
        :rows="3"
        placeholder="用自然语言描述您想查询的内容，例如：查找所有与阿里巴巴有投资关系的公司..."
        resize="none"
        @update:model-value="emit('update:modelValue', $event)"
        @keydown="handleKeyDown"
      />
      <el-button
        class="submit-btn"
        type="primary"
        :loading="loading"
        :disabled="!hasInput"
        @click="handleSubmit"
      >
        <el-icon><ArrowRight /></el-icon>
        查询
      </el-button>
    </div>

    <!-- 示例查询 -->
    <transition name="slide">
      <div v-if="showExamples" class="examples-panel">
        <div class="examples-title">点击使用示例查询:</div>
        <div class="examples-list">
          <el-tag
            v-for="(example, index) in exampleQueries"
            :key="index"
            class="example-tag"
            type="info"
            effect="plain"
            @click="handleExampleClick(example)"
          >
            {{ example }}
          </el-tag>
        </div>
      </div>
    </transition>

    <!-- NL→Cypher 转换结果 -->
    <transition name="fade">
      <div v-if="showResults" class="nl-results">
        <div v-if="cypher" class="result-section">
          <div class="result-label">生成的 Cypher 查询:</div>
          <pre class="cypher-code">{{ cypher }}</pre>
        </div>
        <div v-if="answer" class="result-section">
          <div class="result-label">回答:</div>
          <div class="answer-text">{{ answer }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.nl-query-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.input-wrapper {
  position: relative;
}

.submit-btn {
  position: absolute;
  right: 8px;
  bottom: 8px;
}

.examples-panel {
  background: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 12px;
}

.examples-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.examples-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.example-tag:hover {
  color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.nl-results {
  background: var(--el-fill-color-light);
  border-radius: 4px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.cypher-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  overflow-x: auto;
  margin: 0;
}

.answer-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
