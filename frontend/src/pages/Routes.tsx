import { useState, useEffect } from 'react'
import { farmApi, productsApi, buyersApi, vehiclesApi, ordersApi, solverApi, type Farm, type Product, type Buyer, type Vehicle, type BuyerOrder, type SolverTrip, type SolverShipment, type SolverBalance } from '../api/client'

export default function Routes() {
  const [trips, setTrips] = useState<SolverTrip[]>([])
  const [shipments, setShipments] = useState<SolverShipment[]>([])
  const [balances, setBalances] = useState<SolverBalance[]>([])
  const [summary, setSummary] = useState<{ revenue: number; transport_cost: number; profit: number; status: string; message: string } | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [buyers, setBuyers] = useState<Buyer[]>([])
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [orders, setOrders] = useState<BuyerOrder[]>([])
  const [farm, setFarm] = useState<Farm | null>(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [calcError, setCalcError] = useState<string | null>(null)
  const [selectedTrip, setSelectedTrip] = useState<SolverTrip | null>(null)

  const fetchData = async () => {
    try {
      const [farmData, productsData, buyersData, vehiclesData, ordersData] = await Promise.all([
        farmApi.get().catch(() => null),
        productsApi.list(),
        buyersApi.list(),
        vehiclesApi.list(),
        ordersApi.list(),
      ])
      setFarm(farmData)
      setProducts(productsData)
      setBuyers(buyersData)
      setVehicles(vehiclesData)
      setOrders(ordersData)
    } catch (err: any) {
      console.error('Failed to fetch data:', err)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const getBuyerName = (buyerId: string) => buyers.find((b) => b.id === buyerId)?.name || buyerId
  const getProductName = (productId: string) => products.find((p) => p.id === productId)?.name || productId
  const getVehicleName = (vehicleId: string) => vehicles.find((v) => v.id === vehicleId)?.name || vehicleId

  const handleCalculate = async () => {
    if (!farm) {
      setCalcError('Сначала добавьте хозяйство на странице "Хозяйство"')
      return
    }

    setIsCalculating(true)
    setCalcError(null)

    try {
      const result = await solverApi.plan({
        farm: {
          name: farm.name,
          longitude: farm.longitude,
          latitude: farm.latitude,
        },
        products: products.map((p) => ({
          id: p.id,
          name: p.name,
          stock_kg: p.stock_kg,
          max_delivery_hours: p.max_delivery_hours,
        })),
        buyers: buyers.map((b) => ({
          id: b.id,
          name: b.name,
          longitude: b.longitude,
          latitude: b.latitude,
          orders: orders
            .filter((o) => o.buyer_id === b.id)
            .map((o) => ({
              product_id: o.product_id,
              demand_kg: o.demand_kg,
              price_per_kg: o.price_per_kg,
            })),
        })),
        vehicles: vehicles.map((v) => ({
          id: v.id,
          name: v.name,
          capacity_kg: v.capacity_kg,
          fuel_consumption_l_per_100km: v.fuel_consumption_l_per_100km,
          fuel_price_rub_per_liter: v.fuel_price_rub_per_liter,
          max_trips: v.max_trips,
          max_stops: v.max_stops,
          available: v.available,
        })),
      })

      setTrips(result.trips || [])
      setShipments(result.shipments || [])
      setBalances(result.balances || [])
      setSummary({
        revenue: result.revenue || 0,
        transport_cost: result.transport_cost || 0,
        profit: result.profit || 0,
        status: result.status || '',
        message: result.message || '',
      })
    } catch (err: any) {
      setCalcError(err.message || 'Ошибка при расчёте маршрутов')
    } finally {
      setIsCalculating(false)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Маршруты доставки</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Планирование маршрутов через API расчёта (POST /api/v1/plan)
          </p>
        </div>
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
      </div>

      {/* Error message */}
      {calcError && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-lg text-red-800 dark:text-red-200">
          ⚠️ {calcError}
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <span className="text-xl">💰</span>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Выручка</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.revenue.toLocaleString()} ₽</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-100 dark:bg-red-900 rounded-lg flex items-center justify-center">
                <span className="text-xl">🚛</span>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Транспортные расходы</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.transport_cost.toLocaleString()} ₽</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-xl">📈</span>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Прибыль</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{summary.profit.toLocaleString()} ₽</p>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                <span className="text-xl">🛣️</span>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Рейсов</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{trips.length}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Status message */}
      {summary?.message && (
        <div className="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg text-primary-800 dark:text-primary-200">
          {summary.message}
        </div>
      )}

      {/* Trips Section */}
      {trips.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Рейсы</h3>
          <div className="space-y-4">
            {trips.map((trip, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                <button
                  onClick={() => setSelectedTrip(selectedTrip === trip ? null : trip)}
                  className="w-full flex items-center justify-between p-5 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🚛</span>
                    <div className="text-left">
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {getVehicleName(trip.vehicle_id)} — Рейс {index + 1}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {trip.distance_km.toFixed(1)} км • {trip.load_kg} кг • {trip.cost.toLocaleString()} ₽
                      </p>
                    </div>
                  </div>
                  <svg
                    className={`w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform duration-200 ${
                      selectedTrip === trip ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {selectedTrip === trip && (
                  <div className="border-t border-gray-200 dark:border-gray-700 p-5 space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Маршрут</h4>
                      <div className="flex flex-wrap gap-2">
                        {trip.waypoints.map((wp, wpIndex) => (
                          <span
                            key={wpIndex}
                            className="px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-full text-sm"
                          >
                            {wpIndex === 0 ? '🌾 ' : '📍 '}{getBuyerName(wp.id)}
                          </span>
                        ))}
                      </div>
                    </div>

                    {trip.geometry && trip.geometry.coordinates && trip.geometry.coordinates.length > 0 && (
                      <div className="h-64 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                        <div className="text-center">
                          <span className="text-4xl">🗺️</span>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                            Карта маршрута ({trip.geometry.coordinates.length} точек)
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Shipments Section */}
      {shipments.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Отгрузки</h3>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-750">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Продукт</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Покупатель</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Машина</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Количество</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {shipments.map((s, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getProductName(s.product_id)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getBuyerName(s.buyer_id)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getVehicleName(s.vehicle_id)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{s.quantity_kg} кг</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Balances Section */}
      {balances.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Остатки и потери</h3>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-750">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Культура</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Остаток</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Потеря</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {balances.map((b, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getProductName(b.product_id)}</td>
                    <td className="px-6 py-4 text-sm text-green-600 dark:text-green-400 font-medium">{b.remaining_kg} кг</td>
                    <td className="px-6 py-4 text-sm text-red-600 dark:text-red-400 font-medium">{b.lost_kg} кг</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {trips.length === 0 && !calcError && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <span className="text-5xl">🗺️</span>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-4">Маршруты не рассчитаны</h3>
          <p className="text-gray-500 dark:text-gray-400 mt-2 max-w-md mx-auto">
            Нажмите "Рассчитать оптимальные маршруты" для планирования доставки на основе текущих данных.
          </p>
        </div>
      )}
    </div>
  )
}
