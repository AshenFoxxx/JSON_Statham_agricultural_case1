from collections import defaultdict

from app.schemas import PlanRequest
from app import seed

ASSUMPTIONS = [
    "Срок культуры считается с начала смены до конца разгрузки у покупателя.",
    "Выгруженный товар обратная дорога не портит. Остаток на дворе стареет, пока эта машина в рейсе.",
    "Следующий выезд той же машины стартует после возврата на хозяйство.",
    "Другая машина, если ещё не выезжала, везёт с полным сроком.",
    "Время и километры считаются по дорогам между координатами хозяйства и покупателей.",
    "Один выезд может объехать нескольких покупателей. Прибытие — перегоны плюс разгрузка: секунды на килограмм на этой остановке.",
    "Погрузка на хозяйстве в срок не входит.",
    "Водитель занят не больше 12 часов за смену: от первого выезда до возврата с последнего рейса.",
    "Стоимость выезда — топливо по километрам туда и обратно: (км / 100) × расход × цена литра.",
    "Число выездов машины не больше max_trips (1–3). Вместимость — в килограммах.",
    "Поиск CP-SAT ограничен time_limit_seconds (по умолчанию 25). По истечении отдаётся лучший найденный план, если оптимум не доказан.",
    "Прибыль = выручка − стоимость топлива. Штрафа за порчу в рублях нет.",
    "Остаток = запас − отгрузка. Потеря равна остатку: что не уехало в этом плане, для отчёта сгнило.",
]


def _from_seed() -> dict:
    """То же содержимое, что seed при первом запуске базы."""
    orders_by_buyer: dict[str, list] = defaultdict(list)
    for product_id, buyer_id, demand_kg, price_per_kg in seed.ORDERS:
        orders_by_buyer[buyer_id].append(
            {
                "product_id": product_id,
                "demand_kg": demand_kg,
                "price_per_kg": price_per_kg,
            }
        )
    farm_name, farm_lon, farm_lat = seed.FARM
    return {
        "farm": {
            "name": farm_name,
            "longitude": farm_lon,
            "latitude": farm_lat,
        },
        "products": [
            {
                "id": product_id,
                "name": name,
                "stock_kg": stock_kg,
                "max_delivery_hours": max_hours,
            }
            for product_id, name, stock_kg, max_hours in seed.PRODUCTS
        ],
        "buyers": [
            {
                "id": buyer_id,
                "name": name,
                "longitude": longitude,
                "latitude": latitude,
                "orders": orders_by_buyer[buyer_id],
            }
            for buyer_id, name, longitude, latitude in seed.BUYERS
        ],
        "unload_seconds_per_kg": 2,
        "vehicles": [
            {
                "id": vehicle_id,
                "name": name,
                "capacity_kg": capacity_kg,
                "fuel_consumption_l_per_100km": fuel,
                "fuel_price_rub_per_liter": price,
                "max_trips": max_trips,
                "max_stops": max_stops,
                "available": available,
            }
            for (
                vehicle_id,
                name,
                capacity_kg,
                fuel,
                price,
                max_trips,
                max_stops,
                available,
            ) in seed.VEHICLES
        ],
    }


def demo_request() -> PlanRequest:
    return PlanRequest.model_validate(_from_seed())


def demo_fleet_request() -> PlanRequest:
    """Тот же каталог, что seed: 4 культуры, 8 покупателей, 3 машины."""
    return demo_request()
