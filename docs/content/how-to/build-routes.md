# Практическое руководство: Построение маршрута

## Задача

Построить оптимальный план поставок с максимизацией прибыли (выручка минус стоимость топлива).

## Подготовка данных {#podgotovka-dannyh}

Данные создаются через веб-интерфейс или REST API. При первом запуске база автоматически заполняется демо-данными:

- Хозяйство: Обнинск
- 3 культуры: Клубника, Томаты, Огурцы
- 4 покупателя с заказами
- 3 машины: Газель А, Газель Б, Рефрижератор

Полный справочник API см. в разделе [API и данные](/doc/reference/api-reference).

## Расчет через веб-интерфейс {#cherez-veb}

1. Откройте `http://localhost:3000/routes`
2. Убедитесь, что на страницах «Склад», «Покупатели» и «Машины» созданы данные
3. Нажмите кнопку «Рассчитать»
4. Результат отобразится в таблице маршрутов и на карте

## Расчет через API {#cherez-api}

### Запрос

```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "farm": {
      "name": "Хозяйство Обнинск",
      "longitude": 36.6103,
      "latitude": 55.0969
    },
    "products": [
      {"id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6},
      {"id": "tomato", "name": "Томаты", "stock_kg": 900, "max_delivery_hours": 24},
      {"id": "cucumber", "name": "Огурцы", "stock_kg": 700, "max_delivery_hours": 18}
    ],
    "buyers": [
      {
        "id": "buyer-obninsk",
        "name": "Рынок Обнинск",
        "longitude": 36.5855,
        "latitude": 55.112,
        "orders": [
          {"product_id": "strawberry", "demand_kg": 200, "price_per_kg": 160},
          {"product_id": "tomato", "demand_kg": 250, "price_per_kg": 70}
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
        "max_trips": 1,
        "max_stops": 3,
        "available": true
      }
    ]
  }'
```

### Ответ

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

Полный справочник API см. в разделе [API и данные](/doc/reference/api-reference).

## Расчет отдельного маршрута {#otdelnyj-marshrut}

### Запрос

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

### Ответ

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

## Демо-данные {#demo-dannyh}

### Получить демо-запрос

```bash
curl http://localhost:8000/api/v1/demo
```

### Получить демо-запрос с флотом

```bash
curl http://localhost:8000/api/v1/demo/fleet
```

## Статистика плана {#statistika}

После расчёта система показывает:

| Метрика | Описание |
|---------|----------|
| Статус | optimal, feasible, infeasible, not_solved |
| Выручка | Сумма quantity_kg * price_per_kg по отгрузкам (₽) |
| Транспортные затраты | Сумма стоимости выполненных рейсов (₽) |
| Прибыль | Выручка минус транспортные затраты (₽) |
| Остатки | Запас минус отгружено по каждой культуре (кг) |

## Ошибки {#oshibki}

### Нет доступных машин

```
План рассчитан: нет доступных машин или ни одна культура не успевает до покупателей.
```

Решение: добавьте машину с `available: true`.

### OSRM недоступен

```
API error 502: OSRM service unavailable
```

Решение: проверьте подключение к интернету. OSRM используется для расчёта расстояний по дорогам.

### Невозможный план

```
status: "infeasible"
message: "Для этих данных нет допустимого плана."
```

Решение: проверьте, что время доставки культур не меньше времени в пути до покупателей.

<< [Запуск через Docker](/doc/tutorials/02-docker-quickstart) | [Развертывание сервисов](/doc/how-to/deploy-services) >>
