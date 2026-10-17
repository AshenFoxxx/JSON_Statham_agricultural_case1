# Справочник: API и данные

---

## Базовый URL

```
http://localhost:8000/api/v1
```

Интерактивная документация: `http://localhost:8000/docs`

---

## Сущности

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
  "name": "ООО АгроТех",
  "longitude": 54.9815,
  "latitude": 36.2523
}
```

#### POST /farm

Создать хозяйство.

```bash
curl -X POST http://localhost:8000/api/v1/farm \
  -H "Content-Type: application/json" \
  -d '{"name": "ООО АгроТех", "longitude": 54.9815, "latitude": 36.2523}'
```

#### PUT /farm

Обновить хозяйство.

```bash
curl -X PUT http://localhost:8000/api/v1/farm \
  -H "Content-Type: application/json" \
  -d '{"name": "ООО АгроТех", "longitude": 54.9815, "latitude": 36.2523}'
```

---

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

---

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
  {"id": "buyer-obninsk", "name": "Рынок Обнинск", "longitude": 54.5126, "latitude": 36.5927},
  {"id": "buyer-kaluga", "name": "Сеть Калуга", "longitude": 54.5293, "latitude": 36.2754}
]
```

#### POST /buyers

Добавить покупателя.

```bash
curl -X POST http://localhost:8000/api/v1/buyers \
  -H "Content-Type: application/json" \
  -d '{"id": "buyer-obninsk", "name": "Рынок Обнинск", "longitude": 54.5126, "latitude": 36.5927}'
```

#### PUT /buyers/{buyer_id}

Обновить покупателя.

```bash
curl -X PUT http://localhost:8000/api/v1/buyers/buyer-obninsk \
  -H "Content-Type: application/json" \
  -d '{"name": "Рынок Обнинск", "longitude": 54.5126, "latitude": 36.5927}'
```

#### DELETE /buyers/{buyer_id}

Удалить покупателя.

```bash
curl -X DELETE http://localhost:8000/api/v1/buyers/buyer-obninsk
```

---

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

---

### Транспорт (Vehicles)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название транспорта |
| `capacity_kg` | float | Грузоподъемность (кг) |
| `fuel_consumption_l_per_100km` | float | Расход топлива (л/100км) |
| `fuel_price_rub_per_liter` | float | Цена топлива (₽/л) |
| `max_trips` | int | Максимум рейсов (1-10) |
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

---

## Планирование (Solver)

### POST /plan

Рассчитать оптимальные маршруты доставки.

```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "products": [...],
    "buyers": [...],
    "vehicles": [...]
  }'
```

Тело запроса:

- `products` — массив объектов Product;
- `buyers` — массив объектов Buyer;
- `vehicles` — массив объектов Vehicle.

Ответ:

```json
{
  "routes": [
    {
      "vehicle_id": "vehicle-a",
      "vehicle_name": "Газель А",
      "buyer_id": "buyer-obninsk",
      "buyer_name": "Рынок Обнинск",
      "product_id": "strawberry",
      "product_name": "Клубника",
      "quantity_kg": 200,
      "distance_km": 45,
      "travel_time_hours": 1,
      "cost": 6000
    }
  ]
}
```

---

## Health Check

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

## Коды ответов

| Код | Описание |
|-----|----------|
| `200` | Успех |
| `201` | Создано |
| `404` | Не найдено |
| `422` | Ошибка валидации |
| `500` | Внутренняя ошибка сервера |

---

<< [Архитектура системы](/doc/reference/architecture) | [Docker-конфигурация](/doc/reference/docker-reference) >>
