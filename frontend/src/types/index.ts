import type { BuyerOrder } from '../api/client'

// Re-export API types
export type { Product, Buyer, Vehicle, Farm } from '../api/client'

// ── Frontend-only types (not in backend) ─────────────────────────

export interface BuyerWithOrders {
  id: string
  name: string
  longitude: number
  latitude: number
  orders: BuyerOrder[]
  travel_time_hours?: number
}

export interface Route {
  id: string
  vehicle_id: string
  vehicle_name: string
  buyer_id: string
  buyer_name: string
  product_id: string
  product_name: string
  quantity_kg: number
  distance_km: number
  travel_time_hours: number
  cost: number
}
