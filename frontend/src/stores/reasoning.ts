import { reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import * as reasoningApi from '@/api/reasoning'
import type {
  Rule,
  CreateRuleParams,
  UpdateRuleParams,
  ReasoningResult,
  ReasoningJob,
} from '@/types/reasoning'

const normalizeError = (error: unknown) => {
  if (error instanceof Error) return error.message
  return typeof error === 'string' ? error : 'Unexpected error'
}

export const useReasoningStore = defineStore('reasoning', () => {
  const rules = ref<Rule[]>([])
  const currentResults = ref<ReasoningResult | null>(null)
  const currentJob = ref<ReasoningJob | null>(null)
  const loading = reactive({
    rules: false,
    save: false,
    run: false,
    results: false,
  })
  const lastError = ref<string | null>(null)

  async function loadRules(projectId: string) {
    loading.rules = true
    lastError.value = null
    try {
      const items = await reasoningApi.listRules(projectId)
      rules.value = items
      return items
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.rules = false
    }
  }

  async function createRule(params: CreateRuleParams) {
    loading.save = true
    lastError.value = null
    try {
      const rule = await reasoningApi.createRule(params)
      rules.value = [rule, ...rules.value]
      return rule
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.save = false
    }
  }

  async function updateRule(id: string, params: UpdateRuleParams) {
    loading.save = true
    lastError.value = null
    try {
      const rule = await reasoningApi.updateRule(id, params)
      const index = rules.value.findIndex((r) => r.id === id)
      if (index !== -1) {
        rules.value[index] = rule
      }
      return rule
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.save = false
    }
  }

  async function deleteRule(id: string) {
    loading.save = true
    lastError.value = null
    try {
      await reasoningApi.deleteRule(id)
      rules.value = rules.value.filter((r) => r.id !== id)
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.save = false
    }
  }

  async function runReasoning(ruleId: string) {
    loading.run = true
    lastError.value = null
    try {
      const job = await reasoningApi.runReasoning(ruleId)
      currentJob.value = job
      return job
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.run = false
    }
  }

  async function loadResults(jobId: string) {
    loading.results = true
    lastError.value = null
    try {
      const results = await reasoningApi.getReasoningResults(jobId)
      currentResults.value = results
      return results
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.results = false
    }
  }

  function getRuleById(id: string): Rule | undefined {
    return rules.value.find((r) => r.id === id)
  }

  function clearResults() {
    currentResults.value = null
    currentJob.value = null
  }

  return {
    rules,
    currentResults,
    currentJob,
    loading,
    lastError,
    loadRules,
    createRule,
    updateRule,
    deleteRule,
    runReasoning,
    loadResults,
    getRuleById,
    clearResults,
  }
})
