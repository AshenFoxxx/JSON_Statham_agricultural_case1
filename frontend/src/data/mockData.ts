import type { Product, Buyer, Vehicle, Route } from '../types'

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

export const mockRoutes: Route[] = [
  {
    id: 'route-1',
    vehicle_id: 'vehicle-a',
    vehicle_name: 'Газель А',
    buyer_id: 'buyer-obninsk',
    buyer_name: 'Рынок Обнинск',
    product_id: 'strawberry',
    product_name: 'Клубника',
    quantity_kg: 200,
    distance_km: 45,
    travel_time_hours: 1,
    cost: 6000,
  },
  {
    id: 'route-2',
    vehicle_id: 'vehicle-b',
    vehicle_name: 'Газель Б',
    buyer_id: 'buyer-kaluga',
    buyer_name: 'Сеть Калуга',
    product_id: 'tomato',
    product_name: 'Томаты',
    quantity_kg: 200,
    distance_km: 80,
    travel_time_hours: 4,
    cost: 6500,
  },
  {
    id: 'route-3',
    vehicle_id: 'vehicle-c',
    vehicle_name: 'Рефрижератор',
    buyer_id: 'buyer-moscow',
    buyer_name: 'Рестораны Москва',
    product_id: 'strawberry',
    product_name: 'Клубника',
    quantity_kg: 300,
    distance_km: 250,
    travel_time_hours: 7,
    cost: 8000,
  },
  {
    id: 'route-4',
    vehicle_id: 'vehicle-a',
    vehicle_name: 'Газель А',
    buyer_id: 'buyer-tula',
    buyer_name: 'Опт Тула',
    product_id: 'cucumber',
    product_name: 'Огурцы',
    quantity_kg: 220,
    distance_km: 150,
    travel_time_hours: 5.5,
    cost: 6000,
  },
]
