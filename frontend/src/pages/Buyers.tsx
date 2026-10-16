import { useState } from 'react'
import type { Buyer, BuyerOrder } from '../types'
import { mockBuyers } from '../data/mockData'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Buyers() {
  const [data, setData] = useState<Buyer[]>(mockBuyers)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<Partial<Buyer>>({})

  const columns = [
    { key: 'name', label: 'Покупатель' },
    { key: 'travel_time_hours', label: 'Время в пути (ч)', render: (v: number) => `${v} ч` },
    {
      key: 'orders',
      label: 'Заказы',
      render: (orders: BuyerOrder[]) => (
        <div className="space-y-1">
          {orders.map((o, i) => (
            <div key={i} className="text-xs">
              <span className="font-medium">{o.product_id}</span>: {o.demand_kg} кг × {o.price_per_kg} ₽
            </div>
          ))}
        </div>
      ),
    },
  ]

  const handleEdit = (buyer: Buyer) => {
    setEditingId(buyer.id)
    setFormData({ ...buyer, orders: JSON.parse(JSON.stringify(buyer.orders)) })
    setIsModalOpen(true)
  }

  const handleDelete = (id: string) => {
    if (confirm('Удалить покупателя?')) {
      setData(data.filter((b) => b.id !== id))
    }
  }

  const handleSave = () => {
    if (editingId) {
      setData(data.map((b) => (b.id === editingId ? { ...b, ...formData } as Buyer : b)))
    } else {
      const newBuyer: Buyer = {
        ...formData as Buyer,
        id: `buyer-${Date.now()}`,
        coordinates: { lat: 0, lng: 0 },
        orders: [],
      }
      setData([...data, newBuyer])
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Покупатели</h2>
        <button className="btn-primary" onClick={() => { setEditingId(null); setFormData({}); setIsModalOpen(true); }}>
          + Добавить покупателя
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
        title={editingId ? 'Редактировать покупателя' : 'Новый покупатель'}
      >
        <div className="space-y-4">
          <input
            className="input-field"
            placeholder="Название (например: Рынок Обнинск)"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <input
            className="input-field"
            placeholder="Время в пути от склада (часов)"
            type="number"
            min="0"
            step="0.5"
            value={formData.travel_time_hours ?? ''}
            onChange={(e) => setFormData({ ...formData, travel_time_hours: Number(e.target.value) })}
          />

          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Заказы</h3>
            <div className="space-y-2">
              <input
                className="input-field text-sm"
                placeholder="Культура (product_id)"
                value={(formData.orders?.[0]?.product_id || '')}
                onChange={(e) => {
                  const orders = formData.orders ? [...formData.orders] : []
                  if (orders.length === 0) orders.push({ product_id: '', demand_kg: 0, price_per_kg: 0 })
                  orders[0] = { ...orders[0], product_id: e.target.value }
                  setFormData({ ...formData, orders })
                }}
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  className="input-field text-sm"
                  placeholder="Спрос (кг)"
                  type="number"
                  min="0"
                  value={formData.orders?.[0]?.demand_kg ?? ''}
                  onChange={(e) => {
                    const orders = formData.orders ? [...formData.orders] : []
                    if (orders.length === 0) orders.push({ product_id: '', demand_kg: 0, price_per_kg: 0 })
                    orders[0] = { ...orders[0], demand_kg: Number(e.target.value) }
                    setFormData({ ...formData, orders })
                  }}
                />
                <input
                  className="input-field text-sm"
                  placeholder="Цена (₽/кг)"
                  type="number"
                  min="0"
                  value={formData.orders?.[0]?.price_per_kg ?? ''}
                  onChange={(e) => {
                    const orders = formData.orders ? [...formData.orders] : []
                    if (orders.length === 0) orders.push({ product_id: '', demand_kg: 0, price_per_kg: 0 })
                    orders[0] = { ...orders[0], price_per_kg: Number(e.target.value) }
                    setFormData({ ...formData, orders })
                  }}
                />
              </div>
            </div>
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
