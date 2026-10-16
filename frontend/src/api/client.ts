const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

export const solverApi = {
  plan: (data: { products: any[]; buyers: any[]; vehicles: any[] }) =>
    request<{ routes: any[] }>('/api/v1/plan', { method: 'POST', body: JSON.stringify(data) }),
}
