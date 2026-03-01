<script setup lang="ts">
import type { Alert, AlertLevel } from '@/types/reasoning'

const props = defineProps<{
  alert: Alert
}>()

const emit = defineEmits<{
  (e: 'ignore', alert: Alert): void
  (e: 'process', alert: Alert): void
  (e: 'click:entity', entityId: string): void
}>()

function getLevelTag(level: AlertLevel) {
  const tags: Record<AlertLevel, { type: "info" | "warning" | "danger" | "primary" | "success"; text: string }> = {
    LOW: { type: 'info', text: '低' },
    MEDIUM: { type: 'warning', text: '中' },
    HIGH: { type: 'danger', text: '高' },
    CRITICAL: { type: 'danger', text: '严重' },
  }
  return tags[level]
}

function getLevelColor(level: AlertLevel): string {
  const colors: Record<AlertLevel, string> = {
    LOW: '#909399',
    MEDIUM: '#E6A23C',
    HIGH: '#F56C6C',
    CRITICAL: '#FF4D4F',
  }
  return colors[level]
}
</script>

<template>
  <el-card
    class="alert-card"
    :class="`alert-level-${props.alert.level.toLowerCase()}`"
    shadow="hover"
  >
    <div class="alert-header">
      <div class="alert-level">
        <el-tag
          :type="getLevelTag(props.alert.level).type"
          size="small"
          effect="dark"
        >
          {{ getLevelTag(props.alert.level).text }}风险
        </el-tag>
        <span class="alert-id">ID: {{ props.alert.id.slice(0, 8) }}</span>
      </div>
      <div class="alert-actions">
        <el-button
          link
          type="primary"
          size="small"
          @click="emit('process', props.alert)"
        >
          处理
        </el-button>
        <el-button
          link
          type="info"
          size="small"
          @click="emit('ignore', props.alert)"
        >
          忽略
        </el-button>
      </div>
    </div>

    <div class="alert-message">
      <el-icon class="alert-icon" :style="{ color: getLevelColor(props.alert.level) }">
        <Warning />
      </el-icon>
      <p class="message-text">{{ props.alert.message }}</p>
    </div>

    <div v-if="props.alert.entities.length" class="alert-entities">
      <span class="entities-label">关联实体:</span>
      <div class="entities-list">
        <el-tag
          v-for="entityId in props.alert.entities"
          :key="entityId"
          size="small"
          class="entity-tag"
          @click="emit('click:entity', entityId)"
        >
          {{ entityId.slice(0, 12) }}...
        </el-tag>
      </div>
    </div>

    <div class="alert-footer">
      <span class="rule-info">
        触发规则: {{ props.alert.ruleId.slice(0, 8) }}...
      </span>
    </div>
  </el-card>
</template>

<style scoped>
.alert-card {
  margin-bottom: 12px;
  border-left: 4px solid v-bind('getLevelColor(props.alert.level)');
}

.alert-card.alert-level-low {
  --alert-accent-color: #909399;
}

.alert-card.alert-level-medium {
  --alert-accent-color: #E6A23C;
}

.alert-card.alert-level-high {
  --alert-accent-color: #F56C6C;
}

.alert-card.alert-level-critical {
  --alert-accent-color: #FF4D4F;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.alert-level {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-id {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.alert-actions {
  display: flex;
  gap: 8px;
}

.alert-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 12px;
}

.alert-icon {
  font-size: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.message-text {
  margin: 0;
  line-height: 1.5;
  color: var(--el-text-color-primary);
}

.alert-entities {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 12px;
  padding: 8px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.entities-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
  margin-top: 4px;
}

.entities-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.entity-tag {
  cursor: pointer;
}

.entity-tag:hover {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.alert-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-light);
}

.rule-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
