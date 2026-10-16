import { useState } from 'react'
import type { Supplier } from '../types'
import { mockSuppliers } from '../data/mockData'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Suppliers() {
  const [data, setData] = useState<Supplier[]>(mockSuppliers)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<Partial<Supplier>>({})

  const columns = [
    { key: 'name', label: 'Название' },
    { key: 'contact', label: 'Контактное лицо' },
    { key: 'phone', label: 'Телефон' },
    { key: 'email', label: 'Email' },
    { key: 'address', label: 'Адрес' },
    { key: 'capacity', label: 'Мощность (т)', render: (v: number) => `${v.toLocaleString()} т` },
    { key: 'rating', label: 'Рейтинг', render: (v: number) => `⭐ ${v}` },
  ]

  const handleEdit = (supplier: Supplier) => {
    setEditingId(supplier.id)
    setFormData({ ...supplier })
    setIsModalOpen(true)
  }

  const handleDelete = (id: number) => {
    if (confirm('Удалить поставщика?')) {
      setData(data.filter((s) => s.id !== id))
    }
  }

  const handleSave = () => {
    if (editingId) {
      setData(data.map((s) => (s.id === editingId ? { ...s, ...formData } as Supplier : s)))
    } else {
      const newSupplier: Supplier = {
        ...formData as Supplier,
        id: Math.max(...data.map((s) => s.id), 0) + 1,
        coordinates: { lat: 0, lng: 0 },
        preferences: [],
      }
      setData([...data, newSupplier])
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Поставщики</h2>
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
        title={editingId ? 'Редактировать поставщика' : 'Новый поставщик'}
      >
        <div className="space-y-4">
          <input
            className="input-field"
            placeholder="Название"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Контактное лицо"
            value={formData.contact || ''}
            onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
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
            placeholder="Адрес"
            value={formData.address || ''}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Мощность (тонн)"
            type="number"
            value={formData.capacity || ''}
            onChange={(e) => setFormData({ ...formData, capacity: Number(e.target.value) })}
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
