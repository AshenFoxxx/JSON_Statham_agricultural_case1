const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!response.ok) {
    const error = await response.text().catch(() => '')
    throw new Error(`API error ${response.status}: ${error || response.statusText}`)
  }
  return response.json() as Promise<T>
}

// ── Farm ──────────────────────────────────────────────────────────

export interface Farm {
  id: string
  name: string
  longitude: number
  latitude: number
}

export const farmApi = {
  get: () => request<Farm>('/api/v1/farm'),
  create: (data: { name: string; longitude: number; latitude: number }) =>
    request<Farm>('/api/v1/farm', { method: 'POST', body: JSON.stringify(data) }),
  update: (data: { name: string; longitude: number; latitude: number }) =>
    request<Farm>('/api/v1/farm', { method: 'PUT', body: JSON.stringify(data) }),
}

// ── Products ──────────────────────────────────────────────────────

export interface Product {
  id: string
  name: string
  stock_kg: number
  max_delivery_hours: number
}

export const productsApi = {
  list: () => request<Product[]>('/api/v1/products'),
  create: (data: Product) =>
    request<Product>('/api/v1/products', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: { name: string; stock_kg: number; max_delivery_hours: number }) =>
    request<Product>(`/api/v1/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/api/v1/products/${id}`, { method: 'DELETE' }),
}

// ── Buyers ────────────────────────────────────────────────────────

export interface Buyer {
  id: string
  name: string
  longitude: number
  latitude: number
}

export const buyersApi = {
  list: () => request<Buyer[]>('/api/v1/buyers'),
  create: (data: Buyer) =>
    request<Buyer>('/api/v1/buyers', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: { name: string; longitude: number; latitude: number }) =>
    request<Buyer>(`/api/v1/buyers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/api/v1/buyers/${id}`, { method: 'DELETE' }),
}

// ── Orders ────────────────────────────────────────────────────────

export interface BuyerOrder {
  id: string
  product_id: string
  buyer_id: string
  demand_kg: number
  price_per_kg: number
}

export const ordersApi = {
  list: () => request<BuyerOrder[]>('/api/v1/orders'),
  create: (data: { product_id: string; buyer_id: string; demand_kg: number; price_per_kg: number }) =>
    request<BuyerOrder>('/api/v1/orders', { method: 'POST', body: JSON.stringify(data) }),
  update: (product_id: string, buyer_id: string, data: { demand_kg: number; price_per_kg: number }) =>
    request<BuyerOrder>(`/api/v1/orders/${product_id}/${buyer_id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (product_id: string, buyer_id: string) =>
    request<void>(`/api/v1/orders/${product_id}/${buyer_id}`, { method: 'DELETE' }),
}

// ── Vehicles ──────────────────────────────────────────────────────

export interface Vehicle {
  id: string
  name: string
  capacity_kg: number
  fuel_consumption_l_per_100km: number
  fuel_price_rub_per_liter: number
  max_trips: number
  max_stops: number
  available: boolean
}

export const vehiclesApi = {
  list: () => request<Vehicle[]>('/api/v1/vehicles'),
  create: (data: Vehicle) =>
    request<Vehicle>('/api/v1/vehicles', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: { name: string; capacity_kg: number; fuel_consumption_l_per_100km: number; fuel_price_rub_per_liter: number; max_trips: number; max_stops: number; available?: boolean }) =>
    request<Vehicle>(`/api/v1/vehicles/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) =>
    request<void>(`/api/v1/vehicles/${id}`, { method: 'DELETE' }),
}

// ── Solver ────────────────────────────────────────────────────────
// Solver API — отдельный URL (отдельный FastAPI сервер)
const SOLVER_BASE = import.meta.env.VITE_SOLVER_URL || 'http://127.0.0.1:8000'

async function solverRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${SOLVER_BASE}${path}`
  // Solver может считать до 120 секунд — ставим 130с
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 180_000)
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options?.headers },
      ...options,
      signal: controller.signal,
    })
    if (!response.ok) {
      const error = await response.text().catch(() => '')
      throw new Error(`Solver API error ${response.status}: ${error || response.statusText}`)
    }
    return response.json() as Promise<T>
  } finally {
    clearTimeout(timeout)
  }
}

export interface SolverFarm {
  name: string
  longitude: number
  latitude: number
}

export interface SolverProduct {
  id: string
  name: string
  stock_kg: number
  max_delivery_hours: number
}

export interface SolverOrder {
  product_id: string
  demand_kg: number
  price_per_kg: number
}

export interface SolverBuyer {
  id: string
  name: string
  longitude: number
  latitude: number
  orders: SolverOrder[]
}

export interface SolverVehicle {
  id: string
  name: string
  capacity_kg: number
  fuel_consumption_l_per_100km: number
  fuel_price_rub_per_liter: number
  max_trips: number
  max_stops: number
  available: boolean
}

export interface SolverPlanRequest {
  farm: SolverFarm
  products: SolverProduct[]
  buyers: SolverBuyer[]
  vehicles: SolverVehicle[]
}

export interface SolverShipment {
  product_id: string
  buyer_id: string
  vehicle_id: string
  quantity_kg: number
}

// Остановка в рейсе — buyer_id (не id), время прибытия, нагрузка
export interface SolverStop {
  buyer_id: string
  arrival_hours: number
  load_kg: number
}

// Точка маршрута — может быть ферма (с координатами) или покупатель
export interface SolverWaypoint {
  id: string
  longitude?: number
  latitude?: number
}

export interface SolverTrip {
  vehicle_id: string
  stops: SolverStop[]
  distance_km: number
  cost: number
  load_kg: number
  waypoints: SolverWaypoint[]
  geometry: { type: string; coordinates: number[][] } // GeoJSON LineString [lon, lat]
}

// Балансы — leftover_kg (не remaining_kg), loss_kg (не lost_kg)
export interface SolverBalance {
  product_id: string
  leftover_kg: number
  loss_kg: number
  stock_kg?: number
  shipped_kg?: number
}

export interface SolverPlanResponse {
  status: string
  message: string
  revenue: number
  transport_cost: number
  profit: number
  shipments: SolverShipment[]
  trips: SolverTrip[]
  balances: SolverBalance[]
}

export const solverApi = {
  plan: (data: SolverPlanRequest) =>
    solverRequest<SolverPlanResponse>('/api/v1/plan', { method: 'POST', body: JSON.stringify(data) }),
}
