import { useState, useEffect } from 'react'
import { farmApi, productsApi, buyersApi, vehiclesApi, ordersApi, solverApi, type Farm, type Product, type Buyer, type Vehicle, type BuyerOrder, type SolverTrip, type SolverShipment, type SolverBalance } from '../api/client'
import RouteLineMap from '../components/RouteLineMap'
import AllRoutesMap, { tripColor } from '../components/AllRoutesMap'

export default function Routes() {
  const [trips, setTrips] = useState<SolverTrip[]>([])
  const [shipments, setShipments] = useState<SolverShipment[]>([])
  const [balances, setBalances] = useState<SolverBalance[]>([])
  const [summary, setSummary] = useState<{
    revenue: number
    transport_cost: number
    profit: number
    status: string
    message: string
    assumptions: string[]
  } | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [buyers, setBuyers] = useState<Buyer[]>([])
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [orders, setOrders] = useState<BuyerOrder[]>([])
  const [farm, setFarm] = useState<Farm | null>(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [calcError, setCalcError] = useState<string | null>(null)
  const [selectedTrip, setSelectedTrip] = useState<SolverTrip | null>(null)
  const [selectedOrderId, setSelectedOrderId] = useState('')
  const [selectedVehicleId, setSelectedVehicleId] = useState('')
  const [shipmentsOpen, setShipmentsOpen] = useState(false)
  const [unloadSecondsPerKg, setUnloadSecondsPerKg] = useState(2)
  const [assumptionsOpen, setAssumptionsOpen] = useState(false)

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

  useEffect(() => {
    if (orders.length === 0) {
      setSelectedOrderId('')
      return
    }
    if (!orders.some((order) => order.id === selectedOrderId)) {
      setSelectedOrderId(orders[0].id)
    }
  }, [orders, selectedOrderId])

  useEffect(() => {
    if (vehicles.length === 0) {
      setSelectedVehicleId('')
      return
    }
    if (!vehicles.some((vehicle) => vehicle.id === selectedVehicleId)) {
      setSelectedVehicleId(vehicles[0].id)
    }
  }, [vehicles, selectedVehicleId])

  const getBuyerName = (buyerId: string) => buyers.find((b) => b.id === buyerId)?.name || buyerId
  const getProductName = (productId: string) => products.find((p) => p.id === productId)?.name || productId
  const getVehicleName = (vehicleId: string) => vehicles.find((v) => v.id === vehicleId)?.name || vehicleId

  const persistVehicle = async (next: Vehicle) => {
    setVehicles((list) => list.map((v) => (v.id === next.id ? next : v)))
    try {
      const saved = await vehiclesApi.update(next.id, next)
      setVehicles((list) => list.map((v) => (v.id === saved.id ? saved : v)))
    } catch (err: any) {
      setCalcError(err.message || 'Не удалось сохранить машину')
    }
  }

  const persistOrderPrice = async (order: BuyerOrder, price_per_kg: number) => {
    const next = { ...order, price_per_kg }
    setOrders((list) => list.map((item) => (item.id === order.id ? next : item)))
    try {
      const saved = await ordersApi.update(order.product_id, order.buyer_id, {
        demand_kg: order.demand_kg,
        price_per_kg,
      })
      setOrders((list) => list.map((item) => (item.id === saved.id ? saved : item)))
    } catch (err: any) {
      setCalcError(err.message || 'Не удалось сохранить цену заказа')
    }
  }

  const handleCalculate = async () => {
    if (!farm) {
      setCalcError('Сначала добавьте хозяйство на странице "Хозяйство"')
      return
    }

    setIsCalculating(true)
    setCalcError(null)

    try {
    const buyersWithOrders = buyers.filter((b) => {
      const buyerOrders = orders.filter((o) => o.buyer_id === b.id)
      return buyerOrders.length > 0
    })

    if (buyersWithOrders.length === 0) {
      setCalcError('Добавьте хотя бы одного покупателя с заказом')
      return
    }

    if (vehicles.length === 0) {
      setCalcError('Добавьте хотя бы одно транспортное средство')
      return
    }

    if (!vehicles.some((v) => v.available)) {
      setCalcError('Все машины сломаны. Верните хотя бы одну в работу и пересчитайте.')
      return
    }

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
      buyers: buyersWithOrders.map((b) => ({
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
        max_trips: 1,
        max_stops: v.max_stops,
        available: v.available,
      })),
      unload_seconds_per_kg: unloadSecondsPerKg,
    })

      setTrips(result.trips || [])
      setShipments(result.shipments || [])
      setShipmentsOpen(false)
      setBalances(result.balances || [])
      setSelectedTrip(null)
      setAssumptionsOpen(false)
      setSummary({
        revenue: result.revenue || 0,
        transport_cost: result.transport_cost || 0,
        profit: result.profit || 0,
        status: result.status || '',
        message: result.message || '',
        assumptions: result.assumptions || [],
      })
    } catch (err: any) {
      setCalcError(err.message || 'Ошибка при расчёте маршрутов')
    } finally {
      setIsCalculating(false)
    }
  }

  const overviewRoutes = trips
    .map((trip, index) => ({
      coordinates: trip.geometry?.coordinates || [],
      color: tripColor(index),
    }))
    .filter((route) => route.coordinates.length > 1)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Маршруты доставки</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Сломайте машину или поменяйте цену товара у покупателя, затем пересчитайте план
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

      {(vehicles.length > 0 || orders.length > 0) && (
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">Сценарий</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Поломка убирает машину из плана. Цена товара у покупателя меняет выручку и то, куда выгоднее везти.
            Разгрузка входит в срок культуры: секунды на каждый килограмм на остановке.
          </p>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 mb-4">
            <span className="whitespace-nowrap">Разгрузка, сек/кг</span>
            <input
              className="input-field w-24 py-1"
              type="number"
              min="0"
              step="1"
              value={unloadSecondsPerKg}
              onChange={(e) => setUnloadSecondsPerKg(Number(e.target.value))}
            />
          </label>
          {vehicles.length > 0 && (
            <div className="rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-3 mb-5">
              <p className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-3">Поломка машины</p>
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <select
                  className="input-field flex-1"
                  value={selectedVehicleId}
                  onChange={(e) => setSelectedVehicleId(e.target.value)}
                >
                  {vehicles.map((vehicle) => (
                    <option key={vehicle.id} value={vehicle.id}>
                      {vehicle.name}
                      {vehicle.available ? '' : ' — сломана'}
                    </option>
                  ))}
                </select>
                {vehicles.find((vehicle) => vehicle.id === selectedVehicleId) && (
                  <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 shrink-0">
                    <input
                      type="checkbox"
                      checked={!vehicles.find((vehicle) => vehicle.id === selectedVehicleId)?.available}
                      onChange={(e) => {
                        const vehicle = vehicles.find((item) => item.id === selectedVehicleId)
                        if (vehicle) persistVehicle({ ...vehicle, available: !e.target.checked })
                      }}
                      className="w-4 h-4 rounded border-gray-300 dark:border-gray-600"
                    />
                    Сломана
                  </label>
                )}
              </div>
            </div>
          )}
          {orders.length > 0 && (
            <div className="rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-3">
              <p className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-3">Цена товара, ₽/кг</p>
              <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                <select
                  className="input-field flex-1"
                  value={selectedOrderId}
                  onChange={(e) => setSelectedOrderId(e.target.value)}
                >
                  {orders.map((order) => (
                    <option key={order.id} value={order.id}>
                      {getBuyerName(order.buyer_id)} — {getProductName(order.product_id)}
                    </option>
                  ))}
                </select>
                {orders.find((order) => order.id === selectedOrderId) && (
                  <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 shrink-0">
                    <span className="whitespace-nowrap">₽/кг</span>
                    <input
                      className="input-field w-28 py-1"
                      type="number"
                      min="0"
                      step="1"
                      value={orders.find((order) => order.id === selectedOrderId)?.price_per_kg ?? 0}
                      onChange={(e) =>
                        setOrders((list) =>
                          list.map((item) =>
                            item.id === selectedOrderId
                              ? { ...item, price_per_kg: Number(e.target.value) }
                              : item
                          )
                        )
                      }
                      onBlur={(e) => {
                        const order = orders.find((item) => item.id === selectedOrderId)
                        if (order) persistOrderPrice(order, Number(e.target.value))
                      }}
                    />
                  </label>
                )}
              </div>
              {orders.find((order) => order.id === selectedOrderId) && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Спрос {orders.find((order) => order.id === selectedOrderId)?.demand_kg} кг
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {calcError && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 border border-red-300 dark:border-red-700 rounded-lg text-red-800 dark:text-red-200">
          ⚠️ {calcError}
        </div>
      )}

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

      {summary?.message && (
        <div className="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg text-primary-800 dark:text-primary-200">
          {summary.message}
        </div>
      )}

      {summary && summary.assumptions.length > 0 && (
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          <button
            type="button"
            onClick={() => setAssumptionsOpen((open) => !open)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <span className="font-medium text-gray-900 dark:text-white">Допущения модели</span>
            <svg
              className={`w-5 h-5 text-gray-500 transition-transform ${assumptionsOpen ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {assumptionsOpen && (
            <ul className="px-5 pb-4 list-disc list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300 border-t border-gray-200 dark:border-gray-700 pt-3">
              {summary.assumptions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {overviewRoutes.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Все маршруты</h3>
          <AllRoutesMap routes={overviewRoutes} farm={farm} buyers={buyers} />
          <div className="mt-3 flex flex-wrap gap-3">
            {trips.map((trip, index) => (
              <span key={`${trip.vehicle_id}-${index}`} className="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: tripColor(index) }} />
                {getVehicleName(trip.vehicle_id)}
              </span>
            ))}
            {farm && (
              <span className="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <span className="inline-block w-3 h-3 rounded-full bg-green-600" />
                {farm.name}
              </span>
            )}
            {buyers.length > 0 && (
              <span className="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                <span className="inline-block w-3 h-3 rounded-full bg-amber-500" />
                Покупатели
              </span>
            )}
          </div>
        </div>
      )}

      {trips.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Рейсы</h3>
          <div className="space-y-4">
            {trips.map((trip, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                <button
                  onClick={() => setSelectedTrip(selectedTrip === trip ? null : trip)}
                  className="w-full flex items-center justify-between p-5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  style={{ borderLeft: `4px solid ${tripColor(index)}` }}
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
                        {trip.waypoints
                          .filter((wp) => wp.id !== "farm")
                          .map((wp, wpIndex) => (
                            <span
                              key={wpIndex}
                              className="px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-full text-sm"
                            >
                              📍 {getBuyerName(wp.id)}
                            </span>
                          ))}
                      </div>
                    </div>

                    {trip.geometry && trip.geometry.coordinates && trip.geometry.coordinates.length > 0 && (
                      <RouteLineMap
                        coordinates={trip.geometry.coordinates}
                        title={`Маршрут ${trip.vehicle_id}`}
                        color={tripColor(index)}
                        buyers={trip.waypoints
                          .filter((wp) => wp.id !== 'farm')
                          .map((wp) => {
                            const buyer = buyers.find((item) => item.id === wp.id)
                            return {
                              name: buyer?.name || getBuyerName(wp.id),
                              longitude: wp.longitude ?? buyer?.longitude,
                              latitude: wp.latitude ?? buyer?.latitude,
                            }
                          })
                          .filter(
                            (item): item is { name: string; longitude: number; latitude: number } =>
                              Number.isFinite(item.longitude) && Number.isFinite(item.latitude)
                          )}
                      />
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {shipments.length > 0 && (
        <div className="mb-8 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
          <button
            type="button"
            onClick={() => setShipmentsOpen((open) => !open)}
            className="w-full flex items-center justify-between p-5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Отгрузки ({shipments.length})
            </h3>
            <svg
              className={`w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform duration-200 ${
                shipmentsOpen ? 'rotate-180' : ''
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {shipmentsOpen && (
            <div className="border-t border-gray-200 dark:border-gray-700">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800/50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Продукт</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Покупатель</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Машина</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Количество</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {shipments.map((s, i) => (
                      <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getProductName(s.product_id)}</td>
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getBuyerName(s.buyer_id)}</td>
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getVehicleName(s.vehicle_id)}</td>
                        <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{s.quantity_kg} кг</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
          )}
        </div>
      )}

      {balances.length > 0 && (
        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Остатки и потери</h3>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Культура</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Остаток</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Потеря</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {balances.map((b, i) => (
                    <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{getProductName(b.product_id)}</td>
                      <td className="px-6 py-4 text-sm text-green-600 dark:text-green-400 font-medium">{b.leftover_kg} кг</td>
                      <td className="px-6 py-4 text-sm text-red-600 dark:text-red-400 font-medium">{b.loss_kg} кг</td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
            </div>
        </div>
      )}

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
