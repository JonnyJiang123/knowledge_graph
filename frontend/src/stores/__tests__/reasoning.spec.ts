import { setActivePinia, createPinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useReasoningStore } from '../reasoning'

const mockReasoningApi = vi.hoisted(() => ({
  createRule: vi.fn(),
  listRules: vi.fn(),
  getRule: vi.fn(),
  updateRule: vi.fn(),
  deleteRule: vi.fn(),
  runReasoning: vi.fn(),
  getReasoningResults: vi.fn(),
}))

vi.mock('@/api/reasoning', () => mockReasoningApi)

describe('reasoning store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.values(mockReasoningApi).forEach((fn) => fn.mockReset())
  })

  it('initializes with default values', () => {
    const store = useReasoningStore()
    expect(store.rules).toEqual([])
    expect(store.currentResults).toBeNull()
    expect(store.currentJob).toBeNull()
    expect(store.loading.rules).toBe(false)
    expect(store.loading.save).toBe(false)
    expect(store.loading.run).toBe(false)
    expect(store.loading.results).toBe(false)
  })

  it('loads rules for a project', async () => {
    const store = useReasoningStore()
    const mockRules = [
      {
        id: 'rule-1',
        projectId: 'proj-1',
        name: 'Test Rule 1',
        description: 'Test description',
        ruleType: 'CUSTOM' as const,
        conditions: [],
        actions: [],
        priority: 50,
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
    ]

    mockReasoningApi.listRules.mockResolvedValue(mockRules)

    const result = await store.loadRules('proj-1')

    expect(mockReasoningApi.listRules).toHaveBeenCalledWith('proj-1')
    expect(store.rules).toEqual(mockRules)
    expect(result).toEqual(mockRules)
    expect(store.loading.rules).toBe(false)
  })

  it('creates a new rule and adds it to the list', async () => {
    const store = useReasoningStore()
    const newRule = {
      id: 'rule-2',
      projectId: 'proj-1',
      name: 'New Rule',
      description: 'New rule description',
      ruleType: 'FINANCE_FRAUD' as const,
      conditions: [{ field: 'amount', operator: 'greater_than' as const, value: 10000 }],
      actions: [{ type: 'create_alert' as const, params: { level: 'HIGH' } }],
      priority: 80,
      isActive: true,
      createdAt: '2024-01-02T00:00:00Z',
      updatedAt: '2024-01-02T00:00:00Z',
    }

    mockReasoningApi.createRule.mockResolvedValue(newRule)

    const createParams = {
      projectId: 'proj-1',
      name: 'New Rule',
      description: 'New rule description',
      ruleType: 'FINANCE_FRAUD' as const,
      conditions: [{ field: 'amount', operator: 'greater_than' as const, value: 10000 }],
      actions: [{ type: 'create_alert' as const, params: { level: 'HIGH' } }],
      priority: 80,
    }

    const result = await store.createRule(createParams)

    expect(mockReasoningApi.createRule).toHaveBeenCalledWith(createParams)
    expect(store.rules).toHaveLength(1)
    expect(store.rules[0]).toEqual(newRule)
    expect(result).toEqual(newRule)
  })

  it('updates an existing rule in the list', async () => {
    const store = useReasoningStore()
    const existingRule = {
      id: 'rule-1',
      projectId: 'proj-1',
      name: 'Old Name',
      description: 'Old description',
      ruleType: 'CUSTOM' as const,
      conditions: [],
      actions: [],
      priority: 50,
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    }

    store.rules = [existingRule]

    const updatedRule = {
      ...existingRule,
      name: 'Updated Name',
      priority: 90,
    }

    mockReasoningApi.updateRule.mockResolvedValue(updatedRule)

    const result = await store.updateRule('rule-1', { name: 'Updated Name', priority: 90 })

    expect(mockReasoningApi.updateRule).toHaveBeenCalledWith('rule-1', { name: 'Updated Name', priority: 90 })
    expect(store.rules[0].name).toBe('Updated Name')
    expect(store.rules[0].priority).toBe(90)
    expect(result).toEqual(updatedRule)
  })

  it('deletes a rule from the list', async () => {
    const store = useReasoningStore()
    store.rules = [
      {
        id: 'rule-1',
        projectId: 'proj-1',
        name: 'Rule 1',
        description: '',
        ruleType: 'CUSTOM' as const,
        conditions: [],
        actions: [],
        priority: 50,
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
      {
        id: 'rule-2',
        projectId: 'proj-1',
        name: 'Rule 2',
        description: '',
        ruleType: 'CUSTOM' as const,
        conditions: [],
        actions: [],
        priority: 50,
        isActive: true,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      },
    ]

    mockReasoningApi.deleteRule.mockResolvedValue(undefined)

    await store.deleteRule('rule-1')

    expect(mockReasoningApi.deleteRule).toHaveBeenCalledWith('rule-1')
    expect(store.rules).toHaveLength(1)
    expect(store.rules[0].id).toBe('rule-2')
  })

  it('runs reasoning and stores the job', async () => {
    const store = useReasoningStore()
    const mockJob = {
      jobId: 'job-1',
      status: 'pending' as const,
      ruleId: 'rule-1',
      startedAt: '2024-01-01T00:00:00Z',
    }

    mockReasoningApi.runReasoning.mockResolvedValue(mockJob)

    const result = await store.runReasoning('rule-1')

    expect(mockReasoningApi.runReasoning).toHaveBeenCalledWith('rule-1')
    expect(store.currentJob).toEqual(mockJob)
    expect(result).toEqual(mockJob)
  })

  it('loads reasoning results', async () => {
    const store = useReasoningStore()
    const mockResults = {
      jobId: 'job-1',
      status: 'completed' as const,
      alerts: [
        {
          id: 'alert-1',
          level: 'HIGH' as const,
          message: 'High risk detected',
          entities: ['entity-1'],
          ruleId: 'rule-1',
        },
      ],
      statistics: {
        entitiesAnalyzed: 100,
        relationsAnalyzed: 200,
        alertsGenerated: 5,
      },
    }

    mockReasoningApi.getReasoningResults.mockResolvedValue(mockResults)

    const result = await store.loadResults('job-1')

    expect(mockReasoningApi.getReasoningResults).toHaveBeenCalledWith('job-1')
    expect(store.currentResults).toEqual(mockResults)
    expect(result).toEqual(mockResults)
  })

  it('finds a rule by id', () => {
    const store = useReasoningStore()
    const rule = {
      id: 'rule-1',
      projectId: 'proj-1',
      name: 'Test Rule',
      description: '',
      ruleType: 'CUSTOM' as const,
      conditions: [],
      actions: [],
      priority: 50,
      isActive: true,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
    }

    store.rules = [rule]

    expect(store.getRuleById('rule-1')).toEqual(rule)
    expect(store.getRuleById('non-existent')).toBeUndefined()
  })

  it('clears results and job', () => {
    const store = useReasoningStore()
    store.currentResults = {
      jobId: 'job-1',
      status: 'completed' as const,
      alerts: [],
      statistics: { entitiesAnalyzed: 0, relationsAnalyzed: 0, alertsGenerated: 0 },
    }
    store.currentJob = {
      jobId: 'job-1',
      status: 'completed' as const,
      ruleId: 'rule-1',
    }

    store.clearResults()

    expect(store.currentResults).toBeNull()
    expect(store.currentJob).toBeNull()
  })

  it('handles API errors during loadRules', async () => {
    const store = useReasoningStore()
    mockReasoningApi.listRules.mockRejectedValue(new Error('Network error'))

    await expect(store.loadRules('proj-1')).rejects.toThrow('Network error')
    expect(store.lastError).toBe('Network error')
    expect(store.loading.rules).toBe(false)
  })

  it('handles API errors during createRule', async () => {
    const store = useReasoningStore()
    mockReasoningApi.createRule.mockRejectedValue(new Error('Validation failed'))

    const createParams = {
      projectId: 'proj-1',
      name: 'Invalid Rule',
      description: '',
      ruleType: 'CUSTOM' as const,
      conditions: [],
      actions: [],
      priority: 50,
    }

    await expect(store.createRule(createParams)).rejects.toThrow('Validation failed')
    expect(store.lastError).toBe('Validation failed')
    expect(store.loading.save).toBe(false)
  })
})
