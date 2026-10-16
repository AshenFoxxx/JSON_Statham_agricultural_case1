from app.schemas import PlanRequest

ASSUMPTIONS = [
    "Срок культуры ограничивает только время в пути до покупателя.",
    "Отсчёт срока начинается в момент отправки. Время на складе не учитывается.",
    "Время и километры считаются по дорогам между координатами хозяйства и покупателей.",
    "Один выезд может объехать нескольких покупателей. Время прибытия складывается из перегонов.",
    "Стоимость выезда — топливо по километрам маршрута: (км / 100) × расход × цена литра.",
    "Каждый выезд проверяется отдельно. Очередь выездов одной машины не моделируется.",
    "Вместимость измеряется в килограммах.",
    "Прибыль = выручка − стоимость топлива.",
    "Невывезенный объём остаётся остатком. Потеря — только объём, который нельзя доставить ни одному покупателю в срок.",
]


def _base() -> dict:
    """Пример тела запроса. Расчёт его не использует: план строится из POST /api/v1/plan."""
    return {
        "farm": {
            "name": "Хозяйство Обнинск",
            "longitude": 36.6103,
            "latitude": 55.0969,
        },
        "products": [
            {
                "id": "strawberry",
                "name": "Клубника",
                "stock_kg": 600,
                "max_delivery_hours": 6,
            },
            {
                "id": "tomato",
                "name": "Томаты",
                "stock_kg": 900,
                "max_delivery_hours": 24,
            },
            {
                "id": "cucumber",
                "name": "Огурцы",
                "stock_kg": 700,
                "max_delivery_hours": 18,
            },
        ],
        "buyers": [
            {
                "id": "buyer-obninsk",
                "name": "Рынок Обнинск",
                "longitude": 36.5855,
                "latitude": 55.112,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 200, "price_per_kg": 160},
                    {"product_id": "tomato", "demand_kg": 250, "price_per_kg": 70},
                    {"product_id": "cucumber", "demand_kg": 200, "price_per_kg": 50},
                ],
            },
            {
                "id": "buyer-kaluga",
                "name": "Сеть Калуга",
                "longitude": 36.2613,
                "latitude": 54.5138,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 250, "price_per_kg": 210},
                    {"product_id": "tomato", "demand_kg": 200, "price_per_kg": 85},
                    {"product_id": "cucumber", "demand_kg": 180, "price_per_kg": 60},
                ],
            },
            {
                "id": "buyer-tula",
                "name": "Опт Тула",
                "longitude": 37.6186,
                "latitude": 54.193,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 180, "price_per_kg": 190},
                    {"product_id": "tomato", "demand_kg": 300, "price_per_kg": 75},
                    {"product_id": "cucumber", "demand_kg": 220, "price_per_kg": 55},
                ],
            },
            {
                "id": "buyer-moscow",
                "name": "Рестораны Москва",
                "longitude": 37.6173,
                "latitude": 55.7558,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 300, "price_per_kg": 280},
                    {"product_id": "tomato", "demand_kg": 400, "price_per_kg": 120},
                    {"product_id": "cucumber", "demand_kg": 250, "price_per_kg": 90},
                ],
            },
            {
                "id": "buyer-far",
                "name": "Дальний опт",
                "longitude": 39.2003,
                "latitude": 51.672,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 200, "price_per_kg": 300},
                    {"product_id": "tomato", "demand_kg": 350, "price_per_kg": 140},
                    {"product_id": "cucumber", "demand_kg": 200, "price_per_kg": 100},
                ],
            },
        ],
        "vehicles": [
            {
                "id": "vehicle-a",
                "name": "Газель А",
                "capacity_kg": 800,
                "fuel_consumption_l_per_100km": 15,
                "fuel_price_rub_per_liter": 60,
                "max_trips": 1,
                "max_stops": 3,
                "available": True,
            },
            {
                "id": "vehicle-b",
                "name": "Газель Б",
                "capacity_kg": 800,
                "fuel_consumption_l_per_100km": 18,
                "fuel_price_rub_per_liter": 60,
                "max_trips": 1,
                "max_stops": 3,
                "available": True,
            },
            {
                "id": "vehicle-c",
                "name": "Рефрижератор",
                "capacity_kg": 700,
                "fuel_consumption_l_per_100km": 25,
                "fuel_price_rub_per_liter": 70,
                "max_trips": 1,
                "max_stops": 3,
                "available": True,
            },
        ],
    }


def demo_request() -> PlanRequest:
    return PlanRequest.model_validate(_base())
