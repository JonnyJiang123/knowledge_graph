<script setup lang="ts">
import { computed } from 'vue'
import { Aim, Rank, CircleCheck } from '@element-plus/icons-vue'
import type { LayoutMode } from '@/types/visualization'

const props = defineProps<{
  modelValue: LayoutMode
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', mode: LayoutMode): void
  (e: 'change', mode: LayoutMode): void
}>()

const layouts = [
  {
    value: 'force' as LayoutMode,
    label: '力导向',
    icon: Aim,
    description: '基于物理模拟的自动布局',
  },
  {
    value: 'hierarchical' as LayoutMode,
    label: '层次布局',
    icon: Rank,
    description: '按层级结构排列',
  },
  {
    value: 'circular' as LayoutMode,
    label: '环形布局',
    icon: CircleCheck,
    description: '节点呈环形分布',
  },
]

const currentLayout = computed({
  get: () => props.modelValue,
  set: (val) => {
    emit('update:modelValue', val)
    emit('change', val)
  },
})

function handleChange(mode: LayoutMode) {
  if (props.disabled) return
  currentLayout.value = mode
}
</script>

<template>
  <div class="layout-switcher">
    <div class="switcher-label">布局模式:</div>
    <div class="layout-options">
      <el-tooltip
        v-for="layout in layouts"
        :key="layout.value"
        :content="layout.description"
        placement="bottom"
      >
        <el-button
          :type="currentLayout === layout.value ? 'primary' : 'default'"
          :plain="currentLayout !== layout.value"
          size="small"
          :disabled="disabled"
          @click="handleChange(layout.value)"
        >
          <el-icon class="layout-icon">
            <component :is="layout.icon" />
          </el-icon>
          {{ layout.label }}
        </el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<style scoped>
.layout-switcher {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.switcher-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
}

.layout-options {
  display: flex;
  gap: 8px;
}

.layout-icon {
  margin-right: 4px;
}
</style>
