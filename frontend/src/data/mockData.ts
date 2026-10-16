import type { Product, Buyer, Vehicle } from '../types'

export const mockProducts: Product[] = [
  {
    id: 'strawberry',
    name: 'Клубника',
    stock_kg: 600,
    max_delivery_hours: 6,
  },
  {
    id: 'tomato',
    name: 'Томаты',
    stock_kg: 900,
    max_delivery_hours: 24,
  },
  {
    id: 'cucumber',
    name: 'Огурцы',
    stock_kg: 700,
    max_delivery_hours: 18,
  },
]

export const mockBuyers: Buyer[] = [
  {
    id: 'buyer-obninsk',
    name: 'Рынок Обнинск',
    coordinates: { lat: 54.5126, lng: 36.5927 },
    travel_time_hours: 1,
    orders: [
      { product_id: 'strawberry', demand_kg: 200, price_per_kg: 160 },
      { product_id: 'tomato', demand_kg: 250, price_per_kg: 70 },
      { product_id: 'cucumber', demand_kg: 200, price_per_kg: 50 },
    ],
  },
  {
    id: 'buyer-kaluga',
    name: 'Сеть Калуга',
    coordinates: { lat: 54.5293, lng: 36.2754 },
    travel_time_hours: 4,
    orders: [
      { product_id: 'strawberry', demand_kg: 250, price_per_kg: 210 },
      { product_id: 'tomato', demand_kg: 200, price_per_kg: 85 },
      { product_id: 'cucumber', demand_kg: 180, price_per_kg: 60 },
    ],
  },
  {
    id: 'buyer-tula',
    name: 'Опт Тула',
    coordinates: { lat: 54.1931, lng: 37.6182 },
    travel_time_hours: 5.5,
    orders: [
      { product_id: 'strawberry', demand_kg: 180, price_per_kg: 190 },
      { product_id: 'tomato', demand_kg: 300, price_per_kg: 75 },
      { product_id: 'cucumber', demand_kg: 220, price_per_kg: 55 },
    ],
  },
  {
    id: 'buyer-moscow',
    name: 'Рестораны Москва',
    coordinates: { lat: 55.7558, lng: 37.6173 },
    travel_time_hours: 7,
    orders: [
      { product_id: 'strawberry', demand_kg: 300, price_per_kg: 280 },
      { product_id: 'tomato', demand_kg: 400, price_per_kg: 120 },
      { product_id: 'cucumber', demand_kg: 250, price_per_kg: 90 },
    ],
  },
]

export const mockVehicles: Vehicle[] = [
  {
    id: 'vehicle-a',
    name: 'Газель А',
    capacity_kg: 800,
    cost_per_trip: 6000,
    max_trips: 2,
    fuel_consumption_l_per_100km: 10,
    available: true,
  },
  {
    id: 'vehicle-b',
    name: 'Газель Б',
    capacity_kg: 800,
    cost_per_trip: 6500,
    max_trips: 2,
    fuel_consumption_l_per_100km: 11,
    available: true,
  },
  {
    id: 'vehicle-c',
    name: 'Рефрижератор',
    capacity_kg: 700,
    cost_per_trip: 8000,
    max_trips: 1,
    fuel_consumption_l_per_100km: 15,
    available: true,
  },
]
