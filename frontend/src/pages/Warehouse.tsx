import { useState } from 'react'
import type { Warehouse } from '../types'
import { mockWarehouses } from '../data/mockData'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Warehouse() {
  const [data, setData] = useState<Warehouse[]>(mockWarehouses)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<Partial<Warehouse>>({})

  const columns = [
    { key: 'name', label: 'Название' },
    { key: 'address', label: 'Адрес' },
    { key: 'manager', label: 'Менеджер' },
    { key: 'capacity', label: 'Мощность (т)', render: (v: number) => `${v.toLocaleString()} т` },
    { key: 'currentStock', label: 'Загрузка', render: (v: number, row: Warehouse) => {
      const pct = Math.round((v / row.capacity) * 100)
      return (
        <div className="flex items-center gap-2">
          <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-500 rounded-full"
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="text-xs">{pct}%</span>
        </div>
      )
    }},
    { key: 'products', label: 'Продукция', render: (v: string[]) => v.join(', ') },
    { key: 'temperature', label: 'Температура' },
  ]

  const handleEdit = (warehouse: Warehouse) => {
    setEditingId(warehouse.id)
    setFormData({ ...warehouse })
    setIsModalOpen(true)
  }

  const handleDelete = (id: number) => {
    if (confirm('Удалить склад?')) {
      setData(data.filter((w) => w.id !== id))
    }
  }

  const handleSave = () => {
    if (editingId) {
      setData(data.map((w) => (w.id === editingId ? { ...w, ...formData } as Warehouse : w)))
    } else {
      const newWarehouse: Warehouse = {
        ...formData as Warehouse,
        id: Math.max(...data.map((w) => w.id), 0) + 1,
        coordinates: { lat: 0, lng: 0 },
        products: [],
      }
      setData([...data, newWarehouse])
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Складская логистика</h2>
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
        title={editingId ? 'Редактировать склад' : 'Новый склад'}
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
            placeholder="Адрес"
            value={formData.address || ''}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Менеджер"
            value={formData.manager || ''}
            onChange={(e) => setFormData({ ...formData, manager: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Мощность (тонн)"
            type="number"
            value={formData.capacity || ''}
            onChange={(e) => setFormData({ ...formData, capacity: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Текущий запас (тонн)"
            type="number"
            value={formData.currentStock || ''}
            onChange={(e) => setFormData({ ...formData, currentStock: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Продукция (через запятую)"
            value={formData.products?.join(', ') || ''}
            onChange={(e) => setFormData({ ...formData, products: e.target.value.split(',').map(s => s.trim()) })}
          />
          <input
            className="input-field"
            placeholder="Температура"
            value={formData.temperature || ''}
            onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
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
