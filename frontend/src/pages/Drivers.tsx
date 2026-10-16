import { useState } from 'react'
import type { Driver } from '../types'
import { mockDrivers } from '../data/mockData'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Drivers() {
  const [data, setData] = useState<Driver[]>(mockDrivers)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<Partial<Driver>>({})

  const columns = [
    { key: 'name', label: 'ФИО' },
    { key: 'license', label: 'Водительское удостоверение' },
    { key: 'phone', label: 'Телефон' },
    { key: 'email', label: 'Email' },
    { key: 'vehicleType', label: 'Тип ТС' },
    { key: 'experience', label: 'Опыт (лет)', render: (v: number) => `${v} лет` },
    { key: 'rating', label: 'Рейтинг', render: (v: number) => `⭐ ${v}` },
    { key: 'status', label: 'Статус', render: (v: string) => {
      const styles: Record<string, string> = {
        active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        inactive: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        'on-leave': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      }
      const labels: Record<string, string> = {
        active: 'Активен',
        inactive: 'Неактивен',
        'on-leave': 'В отпуске',
      }
      return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[v] || ''}`}>
          {labels[v] || v}
        </span>
      )
    }},
  ]

  const handleEdit = (driver: Driver) => {
    setEditingId(driver.id)
    setFormData({ ...driver })
    setIsModalOpen(true)
  }

  const handleDelete = (id: number) => {
    if (confirm('Удалить водителя?')) {
      setData(data.filter((d) => d.id !== id))
    }
  }

  const handleSave = () => {
    if (editingId) {
      setData(data.map((d) => (d.id === editingId ? { ...d, ...formData } as Driver : d)))
    } else {
      const newDriver: Driver = {
        ...formData as Driver,
        id: Math.max(...data.map((d) => d.id), 0) + 1,
        status: 'active',
      }
      setData([...data, newDriver])
    }
    closeModal()
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingId(null)
    setFormData({})
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Водители</h2>
        <button className="btn-primary" onClick={() => { setEditingId(null); setFormData({}); setIsModalOpen(true); }}>
          + Добавить
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
        title={editingId ? 'Редактировать водителя' : 'Новый водитель'}
      >
        <div className="space-y-4">
          <input
            className="input-field"
            placeholder="ФИО"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Водительское удостоверение"
            value={formData.license || ''}
            onChange={(e) => setFormData({ ...formData, license: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Телефон"
            value={formData.phone || ''}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Email"
            type="email"
            value={formData.email || ''}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Тип ТС"
            value={formData.vehicleType || ''}
            onChange={(e) => setFormData({ ...formData, vehicleType: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Опыт (лет)"
            type="number"
            value={formData.experience || ''}
            onChange={(e) => setFormData({ ...formData, experience: Number(e.target.value) })}
          />
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
