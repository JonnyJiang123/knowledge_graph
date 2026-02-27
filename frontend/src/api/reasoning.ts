import client from './client'
import type {
  Rule,
  RuleListResponse,
  CreateRuleParams,
  UpdateRuleParams,
  ReasoningJob,
  ReasoningResult,
} from '@/types/reasoning'

const BASE_URL = '/reasoning/rules'

export async function createRule(params: CreateRuleParams): Promise<Rule> {
  const { data } = await client.post<Rule>(BASE_URL, params)
  return data
}

export async function listRules(projectId: string): Promise<Rule[]> {
  const { data } = await client.get<RuleListResponse>(BASE_URL, {
    params: { projectId },
  })
  return data.items
}

export async function getRule(id: string): Promise<Rule> {
  const { data } = await client.get<Rule>(`${BASE_URL}/${id}`)
  return data
}

export async function updateRule(id: string, params: UpdateRuleParams): Promise<Rule> {
  const { data } = await client.put<Rule>(`${BASE_URL}/${id}`, params)
  return data
}

export async function deleteRule(id: string): Promise<void> {
  await client.delete(`${BASE_URL}/${id}`)
}

export async function runReasoning(ruleId: string): Promise<ReasoningJob> {
  const { data } = await client.post<ReasoningJob>(`${BASE_URL}/${ruleId}/run`)
  return data
}

export async function getReasoningResults(jobId: string): Promise<ReasoningResult> {
  const { data } = await client.get<ReasoningResult>(`/reasoning/jobs/${jobId}/results`)
  return data
}
