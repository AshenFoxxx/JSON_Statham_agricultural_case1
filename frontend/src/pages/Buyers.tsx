import { useState, useEffect } from 'react'
import { buyersApi, ordersApi, productsApi, type Buyer, type BuyerOrder, type Product } from '../api/client'
import DataTable from '../components/DataTable'
import Modal from '../components/Modal'

export default function Buyers() {
  const [buyers, setBuyers] = useState<Buyer[]>([])
  const [orders, setOrders] = useState<BuyerOrder[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formData, setFormData] = useState<Partial<Buyer>>({})
  const [orderForm, setOrderForm] = useState<Partial<BuyerOrder>>({})

  const fetchData = async () => {
    try {
      setLoading(true)
      const [buyersData, ordersData, productsData] = await Promise.all([
        buyersApi.list(),
        ordersApi.list(),
        productsApi.list(),
      ])
      setBuyers(buyersData)
      setOrders(ordersData)
      setProducts(productsData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const getBuyerOrders = (buyerId: string): BuyerOrder[] => {
    return orders.filter((o) => o.buyer_id === buyerId)
  }

  const columns = [
    { key: 'name', label: 'Покупатель' },
    { key: 'longitude', label: 'Долгота', render: (v: number) => v.toFixed(4) },
    { key: 'latitude', label: 'Широта', render: (v: number) => v.toFixed(4) },
    {
      key: 'orders',
      label: 'Заказы',
      render: (_: unknown, row: Buyer) => {
        const buyerOrders = getBuyerOrders(row.id)
        if (buyerOrders.length === 0) return <span className="text-gray-400 text-xs">Нет заказов</span>
        return (
          <div className="space-y-1">
            {buyerOrders.map((o, i) => (
              <div key={i} className="text-xs">
                <span className="font-medium">{o.product_id}</span>: {o.demand_kg} кг × {o.price_per_kg} ₽
              </div>
            ))}
          </div>
        )
      },
    },
  ]

  const handleEdit = (buyer: Buyer) => {
    setEditingId(buyer.id)
    setFormData({ ...buyer })
    setIsModalOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (confirm('Удалить покупателя?')) {
      try {
        await buyersApi.delete(id)
        setBuyers(buyers.filter((b) => b.id !== id))
      } catch (err: any) {
        alert(err.message)
      }
    }
  }

  const handleSave = async () => {
    try {
      if (editingId) {
        const updated = await buyersApi.update(editingId, formData as Buyer)
        setBuyers(buyers.map((b) => (b.id === editingId ? updated : b)))
      } else {
        const newBuyer: Buyer = {
          ...(formData as Buyer),
          id: `buyer-${Date.now()}`,
        }
        const created = await buyersApi.create(newBuyer)
        setBuyers([...buyers, created])
      }
      closeModal()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleSaveOrder = async () => {
    try {
      const buyer = buyers.find((b) => b.id === editingId)
      if (!buyer) return

      const newOrder: BuyerOrder = {
        id: `order-${Date.now()}`,
        product_id: orderForm.product_id || '',
        buyer_id: buyer.id,
        demand_kg: orderForm.demand_kg || 0,
        price_per_kg: orderForm.price_per_kg || 0,
      }

      const created = await ordersApi.create(newOrder)
      setOrders([...orders, created])
      setIsOrderModalOpen(false)
      setOrderForm({})
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleDeleteOrder = async (product_id: string, buyer_id: string) => {
    if (confirm('Удалить заказ?')) {
      try {
        await ordersApi.delete(product_id, buyer_id)
        setOrders(orders.filter((o) => !(o.product_id === product_id && o.buyer_id === buyer_id)))
      } catch (err: any) {
        alert(err.message)
      }
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Покупатели</h2>
        <button className="btn-primary" onClick={() => { setEditingId(null); setFormData({}); setIsModalOpen(true); }}>
          + Добавить покупателя
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <DataTable
          columns={columns}
          data={buyers}
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

      {/* Buyer Modal */}
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

          <div className="grid grid-cols-2 gap-4">
            <input
              className="input-field"
              placeholder="Долгота (lon)"
              type="number"
              step="0.000001"
              value={formData.longitude ?? ''}
              onChange={(e) => setFormData({ ...formData, longitude: Number(e.target.value) })}
            />
            <input
              className="input-field"
              placeholder="Широта (lat)"
              type="number"
              step="0.000001"
              value={formData.latitude ?? ''}
              onChange={(e) => setFormData({ ...formData, latitude: Number(e.target.value) })}
            />
          </div>

          {/* Orders section */}
          {editingId && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">Заказы</h3>
                <button
                  className="text-xs text-primary-600 hover:text-primary-700"
                  onClick={() => {
                    setEditingId(editingId)
                    setIsOrderModalOpen(true)
                  }}
                >
                  + Добавить заказ
                </button>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {getBuyerOrders(editingId).map((o) => (
                  <div key={o.product_id} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    <div>
                      <span className="font-medium">{o.product_id}</span>: {o.demand_kg} кг × {o.price_per_kg} ₽
                    </div>
                    <button
                      className="text-red-500 hover:text-red-700 text-xs"
                      onClick={() => handleDeleteOrder(o.product_id, o.buyer_id)}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2 justify-end pt-4">
            <button className="btn-secondary" onClick={closeModal}>Отмена</button>
            <button className="btn-primary" onClick={handleSave}>
              {editingId ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
        </div>
      </Modal>

      {/* Order Modal */}
      <Modal
        isOpen={isOrderModalOpen}
        onClose={() => setIsOrderModalOpen(false)}
        title="Новый заказ"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Культура
            </label>
            <select
              className="input-field"
              value={orderForm.product_id || ''}
              onChange={(e) => setOrderForm({ ...orderForm, product_id: e.target.value })}
            >
              <option value="">Выберите культуру</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <input
            className="input-field"
            placeholder="Спрос (кг)"
            type="number"
            min="0"
            value={orderForm.demand_kg ?? ''}
            onChange={(e) => setOrderForm({ ...orderForm, demand_kg: Number(e.target.value) })}
          />
          <input
            className="input-field"
            placeholder="Цена (₽/кг)"
            type="number"
            min="0"
            value={orderForm.price_per_kg ?? ''}
            onChange={(e) => setOrderForm({ ...orderForm, price_per_kg: Number(e.target.value) })}
          />
          <div className="flex gap-2 justify-end pt-4">
            <button className="btn-secondary" onClick={() => setIsOrderModalOpen(false)}>Отмена</button>
            <button className="btn-primary" onClick={handleSaveOrder}>Добавить</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
