export type RuleType = 'FINANCE_FRAUD' | 'FINANCE_RISK' | 'HEALTHCARE_DRUG' | 'HEALTHCARE_DIAGNOSIS' | 'CUSTOM'

export type Operator = 'equals' | 'not_equals' | 'in' | 'not_in' | 'greater_than' | 'less_than' | 'exists'

export type ActionType = 'flag_risk' | 'create_alert' | 'add_relation' | 'update_property'

export type ReasoningStatus = 'pending' | 'running' | 'completed' | 'failed'

export type AlertLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface Condition {
  field: string
  operator: Operator
  value: any
}

export interface Action {
  type: ActionType
  params: Record<string, any>
}

export interface Rule {
  id: string
  projectId: string
  name: string
  description: string
  ruleType: RuleType
  conditions: Condition[]
  actions: Action[]
  priority: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface CreateRuleParams {
  projectId: string
  name: string
  description: string
  ruleType: RuleType
  conditions: Condition[]
  actions: Action[]
  priority: number
  isActive?: boolean
}

export interface UpdateRuleParams {
  name?: string
  description?: string
  ruleType?: RuleType
  conditions?: Condition[]
  actions?: Action[]
  priority?: number
  isActive?: boolean
}

export interface Alert {
  id: string
  level: AlertLevel
  message: string
  entities: string[]
  ruleId: string
}

export interface ReasoningStatistics {
  entitiesAnalyzed: number
  relationsAnalyzed: number
  alertsGenerated: number
}

export interface ReasoningResult {
  jobId: string
  status: ReasoningStatus
  alerts: Alert[]
  statistics: ReasoningStatistics
}

export interface ReasoningJob {
  jobId: string
  status: ReasoningStatus
  ruleId: string
  startedAt?: string
  completedAt?: string
}

export interface RuleListResponse {
  items: Rule[]
  total: number
}
