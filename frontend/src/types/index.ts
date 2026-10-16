export interface Supplier {
  id: number
  name: string
  contact: string
  phone: string
  email: string
  address: string
  coordinates: { lat: number; lng: number }
  preferences: string[]
  capacity: number
  rating: number
}

export interface Driver {
  id: number
  name: string
  license: string
  phone: string
  email: string
  vehicleType: string
  experience: number
  rating: number
  status: 'active' | 'inactive' | 'on-leave'
}

export interface Warehouse {
  id: number
  name: string
  address: string
  coordinates: { lat: number; lng: number }
  capacity: number
  currentStock: number
  products: string[]
  temperature: string
  manager: string
}
