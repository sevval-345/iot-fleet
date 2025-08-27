export type RiskBadge = 'green' | 'orange' | 'red'
export type Action = 'freeze_24h' | 'throttle' | 'notify'

export interface FleetItem {
  sim_id: string
  device_type: string
  apn: string
  plan: string
  status: string
  city?: string
  last_seen_at?: string
  risk_score: number
  risk_badge: RiskBadge
  anomalies_count: number
  has_roaming: boolean
}

export interface UsagePoint {
  ts: string
  mb_used: number
  roaming_mb: number
  sms_count?: number
}

export interface Anomaly { type: string; ts: string; reason: string }

export interface ImpactItem {
  sim_id: string
  baseline_mb_24h: number
  expected_mb_24h: number
  delta_pct: number
}

export interface ImpactResponse {
  action: Action
  total_baseline_mb_24h: number
  total_expected_mb_24h: number
  delta_pct: number
  items: ImpactItem[]
}

export interface WhatIfOption {
  label: string
  plan_id: string
  addons: string[]
  total: number
  saving: number
}
export interface WhatIfTop3 {
  current_total: number
  options: WhatIfOption[]
}
