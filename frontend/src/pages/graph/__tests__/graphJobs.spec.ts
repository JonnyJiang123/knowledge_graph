/// <reference types="vitest" />
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import GraphJobs from '../GraphJobs.vue'

const fetchNeighbors = vi.fn().mockResolvedValue({
  entities: [],
  relations: [],
})
const loadProjects = vi.fn().mockResolvedValue([
  { id: 'proj-1', name: 'Test Graph', industry: 'FINANCE', status: 'ACTIVE', owner_id: 'u1' },
])
const saveProject = vi.fn()

// Mock neighbor runs for replay testing - will be populated in tests
let mockNeighborRuns: any[] = []

vi.mock('@/stores/graph', () => ({
  useGraphStore: () => ({
    projects: [{ id: 'proj-1', name: 'Test Graph', industry: 'FINANCE', status: 'ACTIVE', owner_id: 'u1' }],
    currentProjectId: 'proj-1',
    neighborRuns: mockNeighborRuns,
    loading: { projects: false, neighbors: false },
    fetchNeighbors,
    loadProjects,
    saveProject,
    setCurrentProject: vi.fn(),
    clearNeighborRuns: vi.fn(),
  }),
}))

describe('GraphJobs', () => {
  beforeEach(() => {
    fetchNeighbors.mockClear()
    loadProjects.mockClear()
    saveProject.mockClear()
  })

  const mountComponent = () =>
    mount(GraphJobs, {
      global: {
        plugins: [ElementPlus],
        stubs: {
          GraphProjectSelector: {
            template: '<div class="graph-project-selector-stub"></div>',
          },
          NeighborResultDrawer: {
            template: '<div class="neighbor-result-drawer-stub"></div>',
          },
        },
      },
    })

  it('renders jobs table', async () => {
    const wrapper = mountComponent()
    await flushPromises()
    expect(wrapper.find('.graph-jobs').exists()).toBe(true)
  })

  it('runs neighbor query when form valid', async () => {
    const wrapper = mountComponent()
    await flushPromises()

    const vm = wrapper.vm as any
    vm.form.projectId = 'proj-1'
    vm.form.entityId = 'entity-123'
    await wrapper.vm.$nextTick()

    const runButton = wrapper.find('[data-test="run-neighbors"]')
    await runButton.trigger('click')
    await flushPromises()

    expect(fetchNeighbors).toHaveBeenCalledWith('proj-1', {
      entityId: 'entity-123',
      depth: 1,
      limit: undefined,
    })
  })

  it('renders saved neighbor runs and can replay one', async () => {
    // Set up mock neighbor runs
    mockNeighborRuns = [
      {
        id: 'run-1',
        projectId: 'proj-1',
        entityId: 'entity-99',
        depth: 2,
        limit: 5,
        result: { entities: [], relations: [] },
        createdAt: new Date().toISOString(),
      },
    ]
    
    const wrapper = mountComponent()
    await flushPromises()

    // Verify table exists
    expect(wrapper.find('.el-table').exists()).toBe(true)

    // Simulate replay by calling the method directly
    const vm = wrapper.vm as any
    vm.form.projectId = 'proj-1'
    vm.form.entityId = 'entity-99'
    vm.form.depth = 2
    vm.form.limit = 5
    await vm.replayRun(mockNeighborRuns[0])
    await flushPromises()

    // fetchNeighbors should be called with the replay parameters
    expect(fetchNeighbors).toHaveBeenCalledWith('proj-1', {
      entityId: 'entity-99',
      depth: 2,
      limit: 5,
    })
  })
})
