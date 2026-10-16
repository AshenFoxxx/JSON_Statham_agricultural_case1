# Практическое руководство: Расчёт оптимальных маршрутов

> **Тип:** How-To Guide (практическое руководство)
> 
> Задача: как рассчитать оптимальные маршруты доставки продукции.

---

## Задача

Рассчитать оптимальные маршруты доставки продукции от фермы к покупателям с учётом:

- Запасов продукции на складе
- Запросов покупателей (количество, цена)
- Доступного транспорта (грузоподъёмность, количество рейсов)
- Координат фермы и покупателей

---

## Подготовка данных

Перед расчётом маршрутов необходимо создать данные в системе.

### 1. Создать хозяйство (ферму)

```bash
curl -X POST http://localhost:8000/api/v1/farm \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ООО АгроТех",
    "longitude": 54.9815,
    "latitude": 36.2523
  }'
```

### 2. Добавить продукцию

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "id": "strawberry",
    "name": "Клубника",
    "stock_kg": 600,
    "max_delivery_hours": 6
  }'

curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "id": "tomato",
    "name": "Томаты",
    "stock_kg": 900,
    "max_delivery_hours": 24
  }'

curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cucumber",
    "name": "Огурцы",
    "stock_kg": 700,
    "max_delivery_hours": 18
  }'
```

### 3. Добавить покупателей

```bash
curl -X POST http://localhost:8000/api/v1/buyers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "buyer-obninsk",
    "name": "Рынок Обнинск",
    "longitude": 54.5126,
    "latitude": 36.5927
  }'

curl -X POST http://localhost:8000/api/v1/buyers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "buyer-kaluga",
    "name": "Сеть Калуга",
    "longitude": 54.5293,
    "latitude": 36.2754
  }'
```

### 4. Создать заказы для покупателей

```bash
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "strawberry",
    "buyer_id": "buyer-obninsk",
    "demand_kg": 200,
    "price_per_kg": 160
  }'

curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "tomato",
    "buyer_id": "buyer-obninsk",
    "demand_kg": 250,
    "price_per_kg": 70
  }'
```

### 5. Добавить транспорт

```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "id": "vehicle-a",
    "name": "Газель А",
    "capacity_kg": 800,
    "fuel_consumption_l_per_100km": 10,
    "fuel_price_rub_per_liter": 62,
    "max_trips": 2,
    "max_stops": 3,
    "available": true
  }'
```

---

## Расчёт маршрутов через API

### Запрос

```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {"id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6},
      {"id": "tomato", "name": "Томаты", "stock_kg": 900, "max_delivery_hours": 24},
      {"id": "cucumber", "name": "Огурцы", "stock_kg": 700, "max_delivery_hours": 18}
    ],
    "buyers": [
      {"id": "buyer-obninsk", "name": "Рынок Обнинск", "longitude": 54.5126, "latitude": 36.5927},
      {"id": "buyer-kaluga", "name": "Сеть Калуга", "longitude": 54.5293, "latitude": 36.2754}
    ],
    "vehicles": [
      {"id": "vehicle-a", "name": "Газель А", "capacity_kg": 800, "fuel_consumption_l_per_100km": 10, "fuel_price_rub_per_liter": 62, "max_trips": 2, "max_stops": 3, "available": true}
    ]
  }'
```

### Ответ

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

## Расчёт через веб-интерфейс

1. Откройте **http://localhost:3000/routes**
2. Убедитесь, что на страницах «Склад», «Покупатели» и «Машины» созданы данные
3. Нажмите кнопку **«Рассчитать оптимальные маршруты»**
4. Результат отобразится в таблице маршрутов

---

## Статистика маршрутов

После расчёта система показывает:

| Метрика | Описание |
|---------|----------|
| **Всего груза** | Суммарный вес продукции в маршрутах (кг) |
| **Общая стоимость** | Суммарная стоимость доставки (₽) |
| **Общая дистанция** | Суммарное расстояние (км) |
| **Маршрутов** | Количество рассчитанных маршрутов |

---

## Ошибки

### Нет данных для расчёта

```
API error 400: Missing products, buyers, or vehicles
```

Решение: создайте хотя бы по одному продукту, покупателю и транспортному средству.

### Сервер недоступен

```
API error 503: Backend is not running
```

Решение: запустите бэкенд:

```bash
docker compose up -d backend
```

### Ошибка solver'а

```
API error 500: Solver calculation failed
```

Решение: проверьте логи бэкенда:

```bash
docker compose logs -f backend
```

---

<< [Запуск через Docker](/doc/tutorials/02-docker-quickstart) | [Развёртывание сервисов](/doc/how-to/deploy-services) >>
