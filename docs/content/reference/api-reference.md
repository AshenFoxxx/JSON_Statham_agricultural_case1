# Справочник: API и данные

## Базовый URL {#bazovyi-url}

```
http://localhost:8000/api/v1
```

Интерактивная документация: `http://localhost:8000/docs`

## Сущности {#sushchnosti}

### Хозяйство (Farm)

Модель: единственная запись — основная ферма.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Идентификатор (фиксированный: "farm") |
| `name` | string | Название хозяйства |
| `longitude` | float | Долгота |
| `latitude` | float | Широта |

#### GET /farm

Получить информацию о хозяйстве.

```bash
curl http://localhost:8000/api/v1/farm
```

Ответ:

```json
{
  "id": "farm",
  "name": "Хозяйство Обнинск",
  "longitude": 36.6103,
  "latitude": 55.0969
}
```

#### POST /farm

Создать хозяйство.

```bash
curl -X POST http://localhost:8000/api/v1/farm \
  -H "Content-Type: application/json" \
  -d '{"name": "Хозяйство Обнинск", "longitude": 36.6103, "latitude": 55.0969}'
```

#### PUT /farm

Обновить хозяйство.

```bash
curl -X PUT http://localhost:8000/api/v1/farm \
  -H "Content-Type: application/json" \
  -d '{"name": "Хозяйство Обнинск", "longitude": 36.6103, "latitude": 55.0969}'
```

### Продукция (Products)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название культуры |
| `stock_kg` | float | Запас на складе (кг) |
| `max_delivery_hours` | float | Максимальное время доставки (часы) |

#### GET /products

Получить список всей продукции.

```bash
curl http://localhost:8000/api/v1/products
```

Ответ:

```json
[
  {"id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6},
  {"id": "tomato", "name": "Томаты", "stock_kg": 900, "max_delivery_hours": 24}
]
```

#### POST /products

Добавить продукт.

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6}'
```

#### PUT /products/{product_id}

Обновить продукт.

```bash
curl -X PUT http://localhost:8000/api/v1/products/strawberry \
  -H "Content-Type: application/json" \
  -d '{"name": "Клубника", "stock_kg": 700, "max_delivery_hours": 6}'
```

#### DELETE /products/{product_id}

Удалить продукт.

```bash
curl -X DELETE http://localhost:8000/api/v1/products/strawberry
```

### Покупатели (Buyers)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название покупателя |
| `longitude` | float | Долгота |
| `latitude` | float | Широта |

#### GET /buyers

Получить список покупателей.

```bash
curl http://localhost:8000/api/v1/buyers
```

Ответ:

```json
[
  {"id": "buyer-obninsk", "name": "Рынок Обнинск", "longitude": 36.5855, "latitude": 55.112},
  {"id": "buyer-kaluga", "name": "Сеть Калуга", "longitude": 36.2613, "latitude": 54.5138}
]
```

#### POST /buyers

Добавить покупателя.

```bash
curl -X POST http://localhost:8000/api/v1/buyers \
  -H "Content-Type: application/json" \
  -d '{"id": "buyer-obninsk", "name": "Рынок Обнинск", "longitude": 36.5855, "latitude": 55.112}'
```

#### PUT /buyers/{buyer_id}

Обновить покупателя.

```bash
curl -X PUT http://localhost:8000/api/v1/buyers/buyer-obninsk \
  -H "Content-Type: application/json" \
  -d '{"name": "Рынок Обнинск", "longitude": 36.5855, "latitude": 55.112}'
```

#### DELETE /buyers/{buyer_id}

Удалить покупателя.

```bash
curl -X DELETE http://localhost:8000/api/v1/buyers/buyer-obninsk
```

### Заказы (Orders)

Связывает продукт и покупателя.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Идентификатор (авто: `order-{product_id}-{buyer_id}`) |
| `product_id` | string | ID продукта |
| `buyer_id` | string | ID покупателя |
| `demand_kg` | float | Спрос (кг) |
| `price_per_kg` | float | Цена за кг (₽) |

#### GET /orders

Получить список всех заказов.

```bash
curl http://localhost:8000/api/v1/orders
```

Ответ:

```json
[
  {"id": "order-strawberry-buyer-obninsk", "product_id": "strawberry", "buyer_id": "buyer-obninsk", "demand_kg": 200, "price_per_kg": 160}
]
```

#### POST /orders

Создать заказ.

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": "strawberry", "buyer_id": "buyer-obninsk", "demand_kg": 200, "price_per_kg": 160}'
```

#### PUT /orders/{product_id}/{buyer_id}

Обновить заказ.

```bash
curl -X PUT http://localhost:8000/api/v1/orders/strawberry/buyer-obninsk \
  -H "Content-Type: application/json" \
  -d '{"demand_kg": 250, "price_per_kg": 170}'
```

#### DELETE /orders/{product_id}/{buyer_id}

Удалить заказ.

```bash
curl -X DELETE http://localhost:8000/api/v1/orders/strawberry/buyer-obninsk
```

### Транспорт (Vehicles)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название транспорта |
| `capacity_kg` | float | Грузоподъемность (кг) |
| `fuel_consumption_l_per_100km` | float | Расход топлива (л/100км) |
| `fuel_price_rub_per_liter` | float | Цена топлива (₽/л) |
| `max_trips` | int | Максимум рейсов (1–3) |
| `max_stops` | int | Максимум остановок (1-5) |
| `available` | boolean | Доступен ли транспорт |

#### GET /vehicles

Получить список транспорта.

```bash
curl http://localhost:8000/api/v1/vehicles
```

Ответ:

```json
[
  {
    "id": "vehicle-a",
    "name": "Газель А",
    "capacity_kg": 800,
    "fuel_consumption_l_per_100km": 10,
    "fuel_price_rub_per_liter": 62,
    "max_trips": 2,
    "max_stops": 3,
    "available": true
  }
]
```

#### POST /vehicles

Добавить транспорт.

```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{"id": "vehicle-a", "name": "Газель А", "capacity_kg": 800, "fuel_consumption_l_per_100km": 10, "fuel_price_rub_per_liter": 62, "max_trips": 2, "max_stops": 3, "available": true}'
```

#### PUT /vehicles/{vehicle_id}

Обновить транспорт.

```bash
curl -X PUT http://localhost:8000/api/v1/vehicles/vehicle-a \
  -H "Content-Type: application/json" \
  -d '{"name": "Газель А", "capacity_kg": 900, "fuel_consumption_l_per_100km": 10, "fuel_price_rub_per_liter": 62, "max_trips": 2, "max_stops": 3, "available": true}'
```

#### DELETE /vehicles/{vehicle_id}

Удалить транспорт.

```bash
curl -X DELETE http://localhost:8000/api/v1/vehicles/vehicle-a
```

## Планирование и маршрутизация {#planirovanie}

### POST /plan

Рассчитать оптимальный план поставок с использованием CP-SAT solver.

```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "farm": {"name": "Хозяйство Обнинск", "longitude": 36.6103, "latitude": 55.0969},
    "products": [
      {"id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6}
    ],
    "buyers": [
      {
        "id": "buyer-obninsk",
        "name": "Рынок Обнинск",
        "longitude": 36.5855,
        "latitude": 55.112,
        "orders": [
          {"product_id": "strawberry", "demand_kg": 200, "price_per_kg": 160}
        ]
      }
    ],
    "vehicles": [
      {
        "id": "vehicle-a",
        "name": "Газель А",
        "capacity_kg": 800,
        "fuel_consumption_l_per_100km": 15,
        "fuel_price_rub_per_liter": 60,
        "max_trips": 2,
        "max_stops": 3,
        "available": true
      }
    ]
  }'
```

Тело запроса:

- `farm` — объект хозяйства с координатами;
- `products` — массив культур с запасами и временем доставки;
- `buyers` — массив покупателей с заказами;
- `vehicles` — массив транспортных средств;
- `unload_seconds_per_kg` — время разгрузки на кг (опционально).

Ответ:

```json
{
  "status": "optimal",
  "objective": "maximize_profit",
  "message": "План рассчитан по данным запроса.",
  "assumptions": ["Срок культуры ограничивает только время в пути до покупателя."],
  "shipments": [
    {
      "product_id": "strawberry",
      "buyer_id": "buyer-obninsk",
      "vehicle_id": "vehicle-a",
      "quantity_kg": 200
    }
  ],
  "trips": [
    {
      "vehicle_id": "vehicle-a",
      "stops": [
        {
          "buyer_id": "buyer-obninsk",
          "arrival_hours": 0.5,
          "load_kg": 200
        }
      ],
      "distance_km": 45.0,
      "cost": 67.5,
      "load_kg": 200,
      "waypoints": [...],
      "geometry": {"type": "LineString", "coordinates": [...]}
    }
  ],
  "revenue": 32000,
  "transport_cost": 67.5,
  "profit": 31932.5,
  "balances": [
    {
      "product_id": "strawberry",
      "stock_kg": 600,
      "shipped_kg": 200,
      "leftover_kg": 400,
      "loss_kg": 0
    }
  ]
}
```

Статусы ответа:

| Статус | Описание |
|--------|----------|
| `optimal` | Доказан оптимум |
| `feasible` | Найден план, оптимум не доказан |
| `infeasible` | Нет допустимого плана |
| `not_solved` | Решение не выполнено |

### POST /route

Рассчитать маршрут между точками через OSRM.

```bash
curl -X POST http://localhost:8000/api/v1/route \
  -H "Content-Type: application/json" \
  -d '{
    "points": [
      {"id": "farm", "longitude": 36.6103, "latitude": 55.0969},
      {"id": "buyer-obninsk", "longitude": 36.5855, "latitude": 55.112}
    ],
    "fuel_consumption_l_per_100km": 15,
    "fuel_price_rub_per_liter": 60
  }'
```

Ответ:

```json
{
  "distance_km": 45.0,
  "duration_hours": 0.5,
  "fuel_liters": 6.75,
  "fuel_cost_rub": 405,
  "legs": [
    {
      "from_id": "farm",
      "to_id": "buyer-obninsk",
      "distance_km": 45.0,
      "hours": 0.5
    }
  ],
  "waypoints": [...],
  "geometry": {"type": "LineString", "coordinates": [...]}
}
```

### GET /demo

Получить демо-данные для одного покупателя.

```bash
curl http://localhost:8000/api/v1/demo
```

### GET /demo/fleet

Получить демо-данные для нескольких покупателей.

```bash
curl http://localhost:8000/api/v1/demo/fleet
```

---

## Health Check {#health-check}

### GET /health

Проверка работоспособности бэкенда.

```bash
curl http://localhost:8000/health
```

Ответ:

```json
{"status": "ok"}
```

---

## Коды ответов {#kody}

| Код | Описание |
|-----|----------|
| `200` | Успех |
| `201` | Создано |
| `404` | Не найдено |
| `422` | Ошибка валидации |
| `500` | Внутренняя ошибка сервера |

---

<< [Архитектура системы](/doc/reference/architecture) | [Docker-конфигурация](/doc/reference/docker-reference) >>
