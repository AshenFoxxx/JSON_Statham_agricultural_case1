import type { SolverBalance, SolverShipment, SolverTrip } from './api/client'

export type PlanSummary = {
  revenue: number
  transport_cost: number
  profit: number
  status: string
  message: string
  assumptions: string[]
  search_seconds?: number
}

export type PlanSnapshot = {
  version: 1
  trips: SolverTrip[]
  shipments: SolverShipment[]
  balances: SolverBalance[]
  summary: PlanSummary | null
  shipmentsOpen: boolean
  assumptionsOpen: boolean
  selectedTripIndex: number | null
  unloadSecondsPerKg: number
  timeLimitSeconds?: number
}

const KEY = 'agro-plan-result-v1'

export function loadPlanSnapshot(): PlanSnapshot | null {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) {
      return null
    }
    const parsed = JSON.parse(raw) as PlanSnapshot
    if (parsed?.version !== 1 || !Array.isArray(parsed.trips)) {
      return null
    }
    return parsed
  } catch {
    return null
  }
}

export function savePlanSnapshot(snapshot: PlanSnapshot): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(snapshot))
  } catch {
    // Quota or private mode — keep the in-memory result.
  }
}
