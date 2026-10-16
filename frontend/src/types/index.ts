export interface Product {
  id: string
  name: string
  stock_kg: number
  max_delivery_hours: number
}

export interface BuyerOrder {
  product_id: string
  demand_kg: number
  price_per_kg: number
}

export interface Buyer {
  id: string
  name: string
  coordinates: { lat: number; lng: number }
  travel_time_hours: number
  orders: BuyerOrder[]
}

export interface Vehicle {
  id: string
  name: string
  capacity_kg: number
  cost_per_trip: number
  max_trips: number
  fuel_consumption_l_per_100km: number
  available: boolean
}
