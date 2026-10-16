import { useState, useEffect } from 'react'
import { solverApi, productsApi, buyersApi, vehiclesApi, type Product, type Buyer, type Vehicle } from '../api/client'
import type { Route } from '../types'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Routes() {
  const [data, setData] = useState<Route[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [buyers, setBuyers] = useState<Buyer[]>([])
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<Partial<Route>>({})
  const [isCalculating, setIsCalculating] = useState(false)
  const [calcError, setCalcError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      const [productsData, buyersData, vehiclesData] = await Promise.all([
        productsApi.list(),
        buyersApi.list(),
        vehiclesApi.list(),
      ])
      setProducts(productsData)
      setBuyers(buyersData)
      setVehicles(vehiclesData)
    } catch (err: any) {
      console.error('Failed to fetch data:', err)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const columns = [
    {
      key: 'vehicle_name',
      label: 'Машина',
      render: (v: string) => (
        <div className="flex items-center gap-2">
          <span>🚛</span>
          <span className="font-medium">{v}</span>
        </div>
      ),
    },
    {
      key: 'buyer_name',
      label: 'Покупатель',
      render: (v: string) => (
        <div className="flex items-center gap-2">
          <span>🛒</span>
          <span className="font-medium">{v}</span>
        </div>
      ),
    },
    {
      key: 'product_name',
      label: 'Продукт',
      render: (v: string) => (
        <div className="flex items-center gap-2">
          <span>📦</span>
          <span className="font-medium">{v}</span>
        </div>
      ),
    },
    { key: 'quantity_kg', label: 'Количество (кг)', render: (v: number) => `${v.toLocaleString()} кг` },
    { key: 'distance_km', label: 'Расстояние (км)', render: (v: number) => `${v} км` },
    { key: 'travel_time_hours', label: 'Время в пути (ч)', render: (v: number) => `${v} ч` },
    { key: 'cost', label: 'Стоимость (₽)', render: (v: number) => `${v.toLocaleString()} ₽` },
  ]

  const handleEdit = (route: Route) => {
    setEditingId(route.id)
    setFormData({ ...route })
    setIsModalOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Удалить маршрут?')) {
      setData(data.filter((r) => r.id !== id))
    }
  }

  const handleSave = () => {
    if (editingId) {
      setData(data.map((r) => (r.id === editingId ? { ...r, ...formData } as Route : r)))
    } else {
      const newRoute: Route = {
        ...(formData as Route),
        id: `route-${Date.now()}`,
      }
      setData([...data, newRoute])
    }
    closeModal()
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingId(null)
    setFormData({})
  }

  const handleCalculate = async () => {
    setIsCalculating(true)
    setCalcError(null)

    try {
      const result = await solverApi.plan({ products, buyers, vehicles })

      const routes: Route[] = result.routes.map((r: any) => ({
        id: `route-${Date.now()}-${r.vehicle_id}-${r.buyer_id}-${r.product_id}`,
        vehicle_id: r.vehicle_id,
        vehicle_name: r.vehicle_name,
        buyer_id: r.buyer_id,
        buyer_name: r.buyer_name,
        product_id: r.product_id,
        product_name: r.product_name,
        quantity_kg: r.quantity_kg,
        distance_km: r.distance_km,
        travel_time_hours: r.travel_time_hours,
        cost: r.cost,
      }))

      setData(routes)
    } catch (err: any) {
      setCalcError(err.message || 'Ошибка при расчёте маршрутов')
    } finally {
      setIsCalculating(false)
    }
  }

  const totalCost = data.reduce((sum, r) => sum + r.cost, 0)
  const totalQuantity = data.reduce((sum, r) => sum + r.quantity_kg, 0)
  const totalDistance = data.reduce((sum, r) => sum + r.distance_km, 0)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Маршруты доставки</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Планирование и отслеживание логистических маршрутов
          </p>
        </div>
        <div className="flex gap-2">
          <button
            className="btn-secondary flex items-center gap-2"
            onClick={handleCalculate}
            disabled={isCalculating}
          >
            {isCalculating ? (
              <>
                <span className="animate-spin">⏳</span>
                Расчёт...
              </>
            ) : (
              <>
                <span>🧮</span>
                Рассчитать оптимальные маршруты
              </>
            )}
          </button>
          <button className="btn-primary" onClick={() => { setEditingId(null); setFormData({}); setIsModalOpen(true); }}>
            + Новый маршрут
          </button>
        </div>
      </div>

      {/* Error message */}
      {calcError && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-lg text-red-800 dark:text-red-200">
          ⚠️ {calcError}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
              <span className="text-xl">📦</span>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Всего груза</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalQuantity.toLocaleString()} кг</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
              <span className="text-xl">💰</span>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Общая стоимость</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalCost.toLocaleString()} ₽</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
              <span className="text-xl">🛣️</span>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Общая дистанция</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalDistance.toLocaleString()} км</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
              <span className="text-xl">🚛</span>
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Маршрутов</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{data.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Routes Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <DataTable
          columns={columns}
          data={data}
          actions={(row) => (
            <div className="flex gap-2">
              <button className="btn-secondary" onClick={() => handleEdit(row)}>
                ✏️
              </button>
              <button className="btn-danger" onClick={() => handleDelete(row.id)}>
                🗑️
              </button>
            </div>
          )}
        />
      </div>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingId ? 'Редактировать маршрут' : 'Новый маршрут'}
      >
        <div className="space-y-4">
          {/* Vehicle Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Машина
            </label>
            <select
              className="input-field"
              value={formData.vehicle_id || ''}
              onChange={(e) => {
                const vehicle = vehicles.find((v) => v.id === e.target.value)
                setFormData({
                  ...formData,
                  vehicle_id: e.target.value,
                  vehicle_name: vehicle?.name || '',
                })
              }}
            >
              <option value="">Выберите машину</option>
              {vehicles
                .filter((v) => v.available)
                .map((v) => (
                  <option key={v.id} value={v.id}>{v.name} (до {v.capacity_kg} кг)</option>
                ))}
            </select>
          </div>

          {/* Buyer Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Покупатель
            </label>
            <select
              className="input-field"
              value={formData.buyer_id || ''}
              onChange={(e) => {
                const buyer = buyers.find((b) => b.id === e.target.value)
                setFormData({
                  ...formData,
                  buyer_id: e.target.value,
                  buyer_name: buyer?.name || '',
                })
              }}
            >
              <option value="">Выберите покупателя</option>
              {buyers.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          {/* Product Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Продукт
            </label>
            <select
              className="input-field"
              value={formData.product_id || ''}
              onChange={(e) => {
                const product = products.find((p) => p.id === e.target.value)
                setFormData({
                  ...formData,
                  product_id: e.target.value,
                  product_name: product?.name || '',
                })
              }}
            >
              <option value="">Выберите продукт</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name} ({p.stock_kg} кг доступно)</option>
              ))}
            </select>
          </div>

          {/* Quantity */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Количество (кг)
            </label>
            <input
              className="input-field"
              type="number"
              min="0"
              placeholder="Введите количество"
              value={formData.quantity_kg ?? ''}
              onChange={(e) => setFormData({ ...formData, quantity_kg: Number(e.target.value) })}
            />
          </div>

          {/* Distance */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Расстояние (км)
            </label>
            <input
              className="input-field"
              type="number"
              min="0"
              placeholder="Введите расстояние"
              value={formData.distance_km ?? ''}
              onChange={(e) => setFormData({ ...formData, distance_km: Number(e.target.value) })}
            />
          </div>

          {/* Travel Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Время в пути (ч)
            </label>
            <input
              className="input-field"
              type="number"
              min="0"
              step="0.5"
              placeholder="Введите время в пути"
              value={formData.travel_time_hours ?? ''}
              onChange={(e) => setFormData({ ...formData, travel_time_hours: Number(e.target.value) })}
            />
          </div>

          {/* Cost */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Стоимость (₽)
            </label>
            <input
              className="input-field"
              type="number"
              min="0"
              placeholder="Введите стоимость"
              value={formData.cost ?? ''}
              onChange={(e) => setFormData({ ...formData, cost: Number(e.target.value) })}
            />
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <button className="btn-secondary" onClick={closeModal}>Отмена</button>
            <button className="btn-primary" onClick={handleSave}>
              {editingId ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
