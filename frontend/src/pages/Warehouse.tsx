import { useState } from 'react'
import type { Product } from '../types'
import { mockProducts } from '../data/mockData'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Warehouse() {
  const [data, setData] = useState<Product[]>(mockProducts)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<Partial<Product>>({})

  const columns = [
    { key: 'name', label: 'Культура' },
    { key: 'stock_kg', label: 'Запас (кг)', render: (v: number) => `${v.toLocaleString()} кг` },
    { key: 'max_delivery_hours', label: 'Срок доставки (ч)', render: (v: number) => `${v} ч` },
  ]

  const handleEdit = (product: Product) => {
    setEditingId(product.id)
    setFormData({ ...product })
    setIsModalOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Удалить культуру?')) {
      setData(data.filter((p) => p.id !== id))
    }
  }

  const handleSave = () => {
    if (editingId) {
      setData(data.map((p) => (p.id === editingId ? { ...p, ...formData } as Product : p)))
    } else {
      const newProduct: Product = {
        ...formData as Product,
        id: `product-${Date.now()}`,
      }
      setData([...data, newProduct])
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
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Склад — Продукция</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Обнинск, ул. Горького 2А
          </p>
        </div>
        <button className="btn-primary" onClick={() => { setEditingId(null); setFormData({}); setIsModalOpen(true); }}>
          + Добавить культуру
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
        title={editingId ? 'Редактировать культуру' : 'Новая культура'}
      >
        <div className="space-y-4">
          <input
            className="input-field"
            placeholder="Название (например: Клубника)"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Запас (кг)"
            type="number"
            min="0"
            value={formData.stock_kg ?? ''}
            onChange={(e) => setFormData({ ...formData, stock_kg: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Макс. время доставки (часов)"
            type="number"
            min="0"
            value={formData.max_delivery_hours ?? ''}
            onChange={(e) => setFormData({ ...formData, max_delivery_hours: Number(e.target.value) })}
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
