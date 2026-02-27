<template>
  <div class="symptom-selector">
    <div class="symptom-categories">
      <el-tabs v-model="activeCategory">
        <el-tab-pane
          v-for="category in categories"
          :key="category.id"
          :label="category.name"
          :name="category.id"
        >
          <div class="symptom-tags">
            <el-check-tag
              v-for="symptom in category.symptoms"
              :key="symptom.id"
              :checked="isSelected(symptom.id)"
              @change="toggleSymptom(symptom.id)"
              class="symptom-tag"
            >
              {{ symptom.name }}
            </el-check-tag>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-divider />

    <div class="selected-symptoms">
      <h4>已选症状 ({{ modelValue.length }})</h4>
      <el-tag
        v-for="symptomId in modelValue"
        :key="symptomId"
        closable
        @close="removeSymptom(symptomId)"
        class="selected-tag"
      >
        {{ getSymptomName(symptomId) }}
      </el-tag>
      <el-empty v-if="modelValue.length === 0" description="请从上方选择症状" />
    </div>

    <el-button
      v-if="modelValue.length > 0"
      type="danger"
      link
      @click="clearAll"
      class="clear-btn"
    >
      清空全部
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  modelValue: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  confirm: []
}>()

const activeCategory = ref('general')

const categories = ref([
  {
    id: 'general',
    name: '全身',
    symptoms: [
      { id: 'fever', name: '发热' },
      { id: 'fatigue', name: '乏力' },
      { id: 'weight-loss', name: '消瘦' },
      { id: 'chills', name: '畏寒' }
    ]
  },
  {
    id: 'respiratory',
    name: '呼吸',
    symptoms: [
      { id: 'cough', name: '咳嗽' },
      { id: 'sputum', name: '咳痰' },
      { id: 'dyspnea', name: '呼吸困难' },
      { id: 'chest-pain', name: '胸痛' }
    ]
  },
  {
    id: 'digestive',
    name: '消化',
    symptoms: [
      { id: 'nausea', name: '恶心' },
      { id: 'vomiting', name: '呕吐' },
      { id: 'abdominal-pain', name: '腹痛' },
      { id: 'diarrhea', name: '腹泻' }
    ]
  },
  {
    id: 'neurological',
    name: '神经',
    symptoms: [
      { id: 'headache', name: '头痛' },
      { id: 'dizziness', name: '头晕' },
      { id: 'insomnia', name: '失眠' },
      { id: 'numbness', name: '麻木' }
    ]
  }
])

const symptomMap = computed(() => {
  const map: Record<string, string> = {}
  categories.value.forEach(cat => {
    cat.symptoms.forEach(s => {
      map[s.id] = s.name
    })
  })
  return map
})

const isSelected = (symptomId: string) => {
  return props.modelValue.includes(symptomId)
}

const toggleSymptom = (symptomId: string) => {
  const newValue = [...props.modelValue]
  const index = newValue.indexOf(symptomId)
  if (index > -1) {
    newValue.splice(index, 1)
  } else {
    newValue.push(symptomId)
  }
  emit('update:modelValue', newValue)
}

const removeSymptom = (symptomId: string) => {
  const newValue = props.modelValue.filter(id => id !== symptomId)
  emit('update:modelValue', newValue)
}

const getSymptomName = (id: string) => {
  return symptomMap.value[id] || id
}

const clearAll = () => {
  emit('update:modelValue', [])
}
</script>

<style scoped>
.symptom-selector {
  padding: 8px;
}
.symptom-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}
.symptom-tag {
  margin: 4px;
}
.selected-symptoms {
  min-height: 100px;
}
.selected-tag {
  margin: 4px;
}
.clear-btn {
  margin-top: 8px;
}
</style>
