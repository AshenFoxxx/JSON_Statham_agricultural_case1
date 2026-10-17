import { useState, useEffect } from 'react'
import { vehiclesApi, type Vehicle } from '../api/client'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Vehicles() {
  const [data, setData] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<Partial<Vehicle>>({})

  const fetchData = async () => {
    try {
      setLoading(true)
      const vehicles = await vehiclesApi.list()
      setData(vehicles)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const columns = [
    { key: 'name', label: 'Машина' },
    { key: 'capacity_kg', label: 'Грузоподъёмность (кг)', render: (v: number) => `${v.toLocaleString()} кг` },
    { key: 'fuel_consumption_l_per_100km', label: 'Расход топлива (л/100км)', render: (v: number) => `${v} л` },
    { key: 'max_stops', label: 'Макс. остановок', render: (v: number) => `${v}` },
    { key: 'max_trips', label: 'Макс. рейсов', render: (v: number) => `${v}` },
    {
      key: 'available',
      label: 'Статус',
      render: (v: boolean) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          v
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {v ? 'Доступна' : 'Недоступна'}
        </span>
      ),
    },
  ]

  const handleEdit = (vehicle: Vehicle) => {
    setEditingId(vehicle.id)
    setFormData({ ...vehicle })
    setIsModalOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('Удалить машину?')) {
      try {
        await vehiclesApi.delete(id)
        setData(data.filter((v) => v.id !== id))
      } catch (err: any) {
        alert(err.message)
      }
    }
  }

  const handleSave = async () => {
    try {
      if (editingId) {
        const updated = await vehiclesApi.update(editingId, formData as Vehicle)
        setData(data.map((v) => (v.id === editingId ? updated : v)))
      } else {
        const newVehicle: Vehicle = {
          ...(formData as Vehicle),
          id: `vehicle-${Date.now()}`,
          max_trips: formData.max_trips || 2,
          available: formData.available ?? true,
        }
        const created = await vehiclesApi.create(newVehicle)
        setData([...data, created])
      }
      closeModal()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingId(null)
    setFormData({})
  }

  if (loading) return <div className="text-center py-8">Загрузка...</div>
  if (error) return <div className="text-center py-8 text-red-500">Ошибка: {error}</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Машины</h2>
        <button className="btn-primary" onClick={() => { setEditingId(null); setFormData({}); setIsModalOpen(true); }}>
          + Добавить машину
        </button>
      </div>

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

      <Modal
        isOpen={isModalOpen}
        onClose={closeModal}
        title={editingId ? 'Редактировать машину' : 'Новая машина'}
      >
        <div className="space-y-4">
          <input
            className="input-field"
            placeholder="Название (например: Газель А)"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Грузоподъёмность (кг)"
            type="number"
            min="0"
            value={formData.capacity_kg ?? ''}
            onChange={(e) => setFormData({ ...formData, capacity_kg: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Расход топлива (л/100км)"
            type="number"
            min="0"
            step="0.1"
            value={formData.fuel_consumption_l_per_100km ?? ''}
            onChange={(e) => setFormData({ ...formData, fuel_consumption_l_per_100km: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Цена топлива (₽/л)"
            type="number"
            min="0"
            step="0.1"
            value={formData.fuel_price_rub_per_liter ?? ''}
            onChange={(e) => setFormData({ ...formData, fuel_price_rub_per_liter: Number(e.target.value) })}
          />
          <div className="grid grid-cols-2 gap-4">
            <input
              className="input-field"
              placeholder="Макс. остановок"
              type="number"
              min="1"
              max="5"
              value={formData.max_stops ?? ''}
              onChange={(e) => setFormData({ ...formData, max_stops: Number(e.target.value) })}
            />
            <input
              className="input-field"
              placeholder="Макс. рейсов"
              type="number"
              min="1"
              max="3"
              value={formData.max_trips ?? ''}
              onChange={(e) => setFormData({ ...formData, max_trips: Number(e.target.value) })}
            />
          </div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.available ?? true}
              onChange={(e) => setFormData({ ...formData, available: e.target.checked })}
              className="w-4 h-4 text-primary-600 bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-600 rounded focus:ring-primary-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">Доступна</span>
          </label>
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
