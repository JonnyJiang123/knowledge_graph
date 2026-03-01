import client from './client'
import type {
  Rule,
  RuleListResponse,
  CreateRuleParams,
  UpdateRuleParams,
  ReasoningJob,
  ReasoningResult,
} from '@/types/reasoning'

export async function createRule(projectId: string, params: CreateRuleParams): Promise<Rule> {
  const { data } = await client.post<Rule>(`/reasoning/projects/${projectId}/rules`, params)
  return data
}

export async function listRules(projectId: string): Promise<Rule[]> {
  const { data } = await client.get<RuleListResponse>(`/reasoning/projects/${projectId}/rules`)
  return data.items
}

export async function getRule(ruleId: string): Promise<Rule> {
  const { data } = await client.get<Rule>(`/reasoning/rules/${ruleId}`)
  return data
}

export async function updateRule(ruleId: string, params: UpdateRuleParams): Promise<Rule> {
  const { data } = await client.put<Rule>(`/reasoning/rules/${ruleId}`, params)
  return data
}

export async function deleteRule(ruleId: string): Promise<void> {
  await client.delete(`/reasoning/rules/${ruleId}`)
}

export async function runReasoning(projectId: string, ruleId: string): Promise<ReasoningJob> {
  const { data } = await client.post<ReasoningJob>(`/reasoning/projects/${projectId}/rules/${ruleId}/run`)
  return data
}

export async function getReasoningResults(jobId: string): Promise<ReasoningResult> {
  const { data } = await client.get<ReasoningResult>(`/reasoning/jobs/${jobId}/results`)
  return data
}
