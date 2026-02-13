/// <reference types="vitest" />
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import IngestionWizard from '../IngestionWizard.vue'
import ElementPlus from 'element-plus'

// Mock API
vi.mock('@/api/ingestion', () => ({
  fetchCleaningRuleTemplates: vi.fn().mockResolvedValue([
    { key: 'NOT_NULL', label: '非空检查', description: '确保字段值不为空' },
  ]),
  listDataSources: vi.fn().mockResolvedValue([]),
  uploadFileArtifact: vi.fn(),
  submitMysqlImport: vi.fn(),
}))

// Mock project store
vi.mock('@/stores/project', () => ({
  useProjectStore: vi.fn(() => ({
    currentProject: { id: 'test-project' },
  })),
}))

describe('IngestionWizard', () => {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', component: { template: '<div>Home</div>' } },
      { path: '/ingestion/wizard', component: IngestionWizard },
      { path: '/ingestion/jobs', component: { template: '<div>Jobs</div>' } },
    ],
  })

  beforeEach(async () => {
    setActivePinia(createPinia())
    router.push('/ingestion/wizard?projectId=test-project')
    await router.isReady()
  })

  const mountComponent = () => {
    return mount(IngestionWizard, {
      global: {
        plugins: [ElementPlus, router, createPinia()],
        stubs: {
          'el-page-header': true,
        },
      },
    })
  }

  it('renders wizard with steps', async () => {
    const wrapper = mountComponent()
    await flushPromises()

    // 应该有步骤条
    const steps = wrapper.findAll('.el-step')
    expect(steps.length).toBe(4)
  })

  it('renders wizard container', async () => {
    const wrapper = mountComponent()
    await flushPromises()

    // 应该有向导容器
    expect(wrapper.find('.ingestion-wizard').exists()).toBe(true)
  })

  it('shows SourceSelector component initially', async () => {
    const wrapper = mountComponent()
    await flushPromises()

    // 应该能看到数据源选择器
    expect(wrapper.find('.source-selector').exists()).toBe(true)
  })

  it('has step navigation buttons', async () => {
    const wrapper = mountComponent()
    await flushPromises()

    // 应该有导航按钮区域
    expect(wrapper.find('.step-actions').exists()).toBe(true)
  })
})
