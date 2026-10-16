from app.schemas import PlanRequest

ASSUMPTIONS = [
    "Срок культуры ограничивает только время в пути до покупателя.",
    "Отсчёт срока начинается в момент отправки. Время на складе не учитывается.",
    "Один рейс обслуживает одного покупателя.",
    "Каждый рейс проверяется отдельно. Очередь рейсов одной машины не моделируется.",
    "Вместимость измеряется в килограммах.",
    "Прибыль = выручка − стоимость рейсов.",
    "Невывезенный объём остаётся остатком. Потеря — только объём, который нельзя доставить ни одному покупателю в срок.",
]


def _base() -> dict:
    """Пример тела запроса. Расчёт его не использует: план строится из POST /api/v1/plan."""
    return {
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
                "travel_time_hours": 1,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 200, "price_per_kg": 160},
                    {"product_id": "tomato", "demand_kg": 250, "price_per_kg": 70},
                    {"product_id": "cucumber", "demand_kg": 200, "price_per_kg": 50},
                ],
            },
            {
                "id": "buyer-kaluga",
                "name": "Сеть Калуга",
                "travel_time_hours": 4,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 250, "price_per_kg": 210},
                    {"product_id": "tomato", "demand_kg": 200, "price_per_kg": 85},
                    {"product_id": "cucumber", "demand_kg": 180, "price_per_kg": 60},
                ],
            },
            {
                "id": "buyer-tula",
                "name": "Опт Тула",
                "travel_time_hours": 5.5,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 180, "price_per_kg": 190},
                    {"product_id": "tomato", "demand_kg": 300, "price_per_kg": 75},
                    {"product_id": "cucumber", "demand_kg": 220, "price_per_kg": 55},
                ],
            },
            {
                "id": "buyer-moscow",
                "name": "Рестораны Москва",
                "travel_time_hours": 7,
                "orders": [
                    {"product_id": "strawberry", "demand_kg": 300, "price_per_kg": 280},
                    {"product_id": "tomato", "demand_kg": 400, "price_per_kg": 120},
                    {"product_id": "cucumber", "demand_kg": 250, "price_per_kg": 90},
                ],
            },
            {
                "id": "buyer-far",
                "name": "Дальний опт",
                "travel_time_hours": 20,
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
                "cost_per_trip": 6000,
                "max_trips": 1,
                "available": True,
            },
            {
                "id": "vehicle-b",
                "name": "Газель Б",
                "capacity_kg": 800,
                "cost_per_trip": 6500,
                "max_trips": 1,
                "available": True,
            },
            {
                "id": "vehicle-c",
                "name": "Рефрижератор",
                "capacity_kg": 700,
                "cost_per_trip": 8000,
                "max_trips": 1,
                "available": True,
            },
        ],
    }


def demo_request() -> PlanRequest:
    return PlanRequest.model_validate(_base())
