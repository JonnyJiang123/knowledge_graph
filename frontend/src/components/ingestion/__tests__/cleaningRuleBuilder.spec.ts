/// <reference types="vitest" />
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CleaningRuleBuilder from '../CleaningRuleBuilder.vue'
import type { CleaningRule, CleaningRuleTemplate } from '@/types/ingestion'
import ElementPlus from 'element-plus'

describe('CleaningRuleBuilder', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const templates: CleaningRuleTemplate[] = [
    { key: 'NOT_NULL', label: '非空检查', description: '确保字段值不为空' },
    { key: 'RANGE', label: '范围限制', description: '限制数值在指定范围内' },
    { key: 'REGEX', label: '正则匹配', description: '使用正则表达式验证格式' },
    { key: 'DEDUPE', label: '去重', description: '去除重复记录' },
  ]

  const mountComponent = (props: {
    modelValue?: CleaningRule[]
    templates?: CleaningRuleTemplate[]
    fields?: string[]
  } = {}) => {
    return mount(CleaningRuleBuilder, {
      props: {
        modelValue: props.modelValue ?? [],
        templates: props.templates ?? templates,
        fields: props.fields,
      },
      global: {
        plugins: [ElementPlus],
      },
    })
  }

  it('renders empty rules list initially', () => {
    const wrapper = mountComponent()
    // 应该没有规则列表
    expect(wrapper.find('.rules-list').exists()).toBe(false)
  })

  it('renders existing rules in the table', () => {
    const rules: CleaningRule[] = [
      { type: 'NOT_NULL', field: 'name', severity: 'ERROR' },
      { type: 'RANGE', field: 'age', severity: 'WARN', params: { min: 0, max: 120 } },
    ]
    const wrapper = mountComponent({ modelValue: rules })

    expect(wrapper.find('.rules-list').exists()).toBe(true)
    // 检查表格行数
    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)
  })

  it('emits update:modelValue when adding a rule', async () => {
    const wrapper = mountComponent()

    // 填写新规则表单
    const fieldInput = wrapper.find('.add-rule-form input[placeholder="输入字段名"]')
    await fieldInput.setValue('email')

    // 点击添加按钮
    const addButton = wrapper.find('.add-rule-form button')
    await addButton.trigger('click')

    // 检查 emit 事件
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toEqual([
      expect.objectContaining({
        type: 'NOT_NULL',
        field: 'email',
        severity: 'WARN',
      }),
    ])
  })

  it('shows rules list when rules exist', () => {
    const rules: CleaningRule[] = [
      { type: 'NOT_NULL', field: 'name', severity: 'ERROR' },
    ]
    const wrapper = mountComponent({ modelValue: rules })

    // 应该显示规则列表
    expect(wrapper.find('.rules-list').exists()).toBe(true)
    // 应该有表格
    expect(wrapper.find('.el-table').exists()).toBe(true)
  })

  it('shows field dropdown when fields prop is provided', () => {
    const wrapper = mountComponent({
      fields: ['id', 'name', 'email'],
    })

    // 应该渲染 el-select 而不是 el-input
    expect(wrapper.find('.add-rule-form .el-select').exists()).toBe(true)
  })

  it('renders add rule form', () => {
    const wrapper = mountComponent()

    // 应该有添加规则表单
    expect(wrapper.find('.add-rule-form').exists()).toBe(true)
    // 应该有添加按钮
    expect(wrapper.find('.add-rule-form button').exists()).toBe(true)
  })
})
