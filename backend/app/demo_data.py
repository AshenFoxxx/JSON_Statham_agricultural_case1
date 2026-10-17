from app.schemas import PlanRequest

ASSUMPTIONS = [
    "Срок культуры ограничивает только время в пути до покупателя.",
    "Отсчёт срока начинается в момент отправки. Время на складе не учитывается.",
    "Время и километры считаются по дорогам между координатами хозяйства и покупателей.",
    "Один выезд может объехать нескольких покупателей. Время прибытия — перегоны плюс разгрузка: секунды на килограмм уже выгруженного, включая эту остановку.",
    "Погрузка на хозяйстве в срок культуры не входит: отсчёт с выезда со двора.",
    "Стоимость выезда — топливо по километрам маршрута туда и обратно на хозяйство: (км / 100) × расход × цена литра.",
    "Машина выезжает со склада один раз за план и возвращается на хозяйство.",
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
        "unload_seconds_per_kg": 2,
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


def demo_fleet_request() -> PlanRequest:
    """Три машины и десять покупателей вокруг хозяйства."""
    buyers = [
        ("buyer-obninsk", "Рынок Обнинск", 36.5855, 55.112),
        ("buyer-balabanovo", "Балабаново", 36.656, 55.177),
        ("buyer-maloyaroslavets", "Малоярославец", 36.471, 55.014),
        ("buyer-zhukov", "Жуков", 36.744, 55.031),
        ("buyer-borovsk", "Боровск", 36.486, 55.206),
        ("buyer-naro-fominsk", "Наро-Фоминск", 36.734, 55.387),
        ("buyer-kaluga", "Сеть Калуга", 36.2613, 54.5138),
        ("buyer-serpukhov", "Серпухов", 37.415, 54.913),
        ("buyer-moscow", "Рестораны Москва", 37.6173, 55.7558),
        ("buyer-tula", "Опт Тула", 37.6186, 54.193),
    ]
    return PlanRequest.model_validate(
        {
            "farm": {
                "name": "Хозяйство Обнинск",
                "longitude": 36.6103,
                "latitude": 55.0969,
            },
            "products": [
                {
                    "id": "berry",
                    "name": "Ягода",
                    "stock_kg": 600,
                    "max_delivery_hours": 24,
                }
            ],
            "buyers": [
                {
                    "id": buyer_id,
                    "name": name,
                    "longitude": longitude,
                    "latitude": latitude,
                    "orders": [
                        {"product_id": "berry", "demand_kg": 100, "price_per_kg": 10}
                    ],
                }
                for buyer_id, name, longitude, latitude in buyers
            ],
            "vehicles": [
                {
                    "id": f"vehicle-{letter}",
                    "name": f"Машина {letter.upper()}",
                    "capacity_kg": 200,
                    "fuel_consumption_l_per_100km": 10,
                    "fuel_price_rub_per_liter": 50,
                    "max_trips": 1,
                    "max_stops": 3,
                    "available": True,
                }
                for letter in ("a", "b", "c")
            ],
        }
    )
