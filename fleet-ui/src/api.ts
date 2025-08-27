// src/api.ts
import axios from 'axios'
import type { FleetItem, Action, ImpactResponse, UsagePoint, Anomaly, WhatIfTop3 } from './types'

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
export const api = axios.create({ baseURL })

export async function fetchFleet(params: { risk?: string; roaming?: boolean; limit?: number; offset?: number }) {
  const { data } = await api.get('/api/fleet', { params })
  return data as FleetItem[]
}

export async function fetchUsage(simId: string, days=30, granularity:'day'|'hour'='day') {
  const { data } = await api.get(`/api/usage/${simId}`, { params: { days, granularity } })
  return data as UsagePoint[]
}

export async function fetchAnomalies(simId: string) {
  const { data } = await api.get(`/api/anomalies/${simId}`)
  return data as Anomaly[]
}

export async function fetchWhatIfTop3(simId: string) {
  const { data } = await api.post(`/api/whatif/${simId}/top3`)
  return data as WhatIfTop3
}

// sabit senaryo için tekil what-if
export async function fetchWhatIf(simId: string, body: { plan_id?: string; addons?: string[] }) {
  const { data } = await api.post(`/api/whatif/${simId}`, body)
  return data as {
    current_total: number
    candidate_total: number
    saving: number
    current_breakdown: any
    candidate_breakdown: any
  }
}

export async function postAction(sim_ids: string[], action: Action, reason = '') {
  const { data } = await api.post('/api/actions', { sim_ids, action, reason })
  return data as { status: string; applied_to: number }
}

export async function postImpact(sim_ids: string[], action: Action, throttle_reduction_pct = 65) {
  const { data } = await api.post('/api/actions/impact', { sim_ids, action, throttle_reduction_pct })
  return data as ImpactResponse
}
