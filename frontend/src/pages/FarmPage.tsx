import { useState, useEffect } from 'react'
import { farmApi, type Farm } from '../api/client'
import LocationMap from '../components/LocationMap'
import Modal from '../components/Modal'

export default function FarmPage() {
  const [farm, setFarm] = useState<Farm | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState<Partial<Farm>>({})

  const fetchFarm = async () => {
    try {
      setLoading(true)
      const data = await farmApi.get()
      setFarm(data)
    } catch (err: any) {
      if (err.message.includes('404')) {
        setFarm(null)
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFarm()
  }, [])

  const handleEdit = () => {
    if (farm) {
      setFormData({ ...farm })
    } else {
      setFormData({ longitude: 36.6103, latitude: 55.0969 })
    }
    setIsModalOpen(true)
  }

  const handleSave = async () => {
    try {
      if (farm) {
        const updated = await farmApi.update(formData as Farm)
        setFarm(updated)
      } else {
        const created = await farmApi.create(formData as Farm)
        setFarm(created)
      }
      setIsModalOpen(false)
    } catch (err: any) {
      alert(err.message)
    }
  }

  if (loading) return <div className="text-center py-8">Загрузка...</div>
  if (error) return <div className="text-center py-8 text-red-500">Ошибка: {error}</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Хозяйство</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Основная ферма — место производства продукции
          </p>
        </div>
        <button className="btn-primary" onClick={handleEdit}>
          {farm ? 'Редактировать' : 'Добавить хозяйство'}
        </button>
      </div>

      {farm ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Название</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{farm.name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Долгота</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{farm.longitude}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Широта</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{farm.latitude}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">ID</h3>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">{farm.id}</p>
            </div>
          </div>

          <LocationMap
            longitude={farm.longitude}
            latitude={farm.latitude}
            title={farm.name}
          />
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <span className="text-5xl">🌾</span>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-4">Хозяйство не добавлено</h3>
          <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
            Добавьте информацию о вашем хозяйстве — месте производства продукции.
            Это понадобится для расчёта маршрутов доставки.
          </p>
        </div>
      )}

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={farm ? 'Редактировать хозяйство' : 'Новое хозяйство'}
      >
        <div className="space-y-4">
          <input
            className="input-field"
            placeholder="Название хозяйства"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Долгота"
            type="number"
            step="0.000001"
            value={formData.longitude ?? ''}
            onChange={(e) => setFormData({ ...formData, longitude: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Широта"
            type="number"
            step="0.000001"
            value={formData.latitude ?? ''}
            onChange={(e) => setFormData({ ...formData, latitude: Number(e.target.value) })}
          />
          <div className="flex gap-2 justify-end pt-4">
            <button className="btn-secondary" onClick={() => setIsModalOpen(false)}>Отмена</button>
            <button className="btn-primary" onClick={handleSave}>
              {farm ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
