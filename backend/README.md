# АгроЛогистика — API

Сервер на FastAPI: хранение склада в SQLite и расчёт плана поставок. Клиент не считает оптимум и расстояния: он передаёт текущие данные, сервер возвращает план и линии рейсов.

Базовый адрес: `http://127.0.0.1:8000`. Схема: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). CORS разрешён для любого origin.

Модель решателя: [SOLVER.md](SOLVER.md). Запуск всего продукта: [корневой README](../README.md).

## Запуск

Windows:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

macOS и Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

При старте создаются таблицы SQLite. Если хозяйства нет, загружаются демонстрационные данные: 4 культуры, 3 машины, 8 покупателей. Файл базы: `agro.db` в рабочем каталоге процесса.

## Эндпоинты

| Метод | Путь | Назначение |
| --- | --- | --- |
| GET | `/health` | Проверка доступности |
| GET, POST, PUT | `/api/v1/farm` | Хозяйство |
| GET, POST, PUT, DELETE | `/api/v1/products` | Культуры |
| GET, POST, PUT, DELETE | `/api/v1/buyers` | Покупатели |
| GET, POST, PUT, DELETE | `/api/v1/orders` | Заказы |
| GET, POST, PUT, DELETE | `/api/v1/vehicles` | Транспорт |
| GET | `/api/v1/demo` | Пример тела `POST /plan` (тот же набор, что seed) |
| GET | `/api/v1/demo/fleet` | То же тело, что `/demo` |
| POST | `/api/v1/matrix` | Прогрев кэша матрицы OSRM |
| POST | `/api/v1/plan` | Расчёт плана и геометрии рейсов |
| POST | `/api/v1/route` | Маршрут по заданному порядку точек |

`POST /api/v1/plan` запрашивает OSRM. Матрица часов и километров кэшируется, пока не изменятся идентификаторы и координаты точек. Страница «Маршруты» греет этот кэш заранее (`POST /api/v1/matrix`). При недоступности сервиса ответ **502**. Некорректное тело — **422**. В обоих случаях план не возвращается.

## Тело `POST /api/v1/plan`

```json
{
  "farm": {
    "name": "Хозяйство Обнинск",
    "longitude": 36.6103,
    "latitude": 55.0969
  },
  "products": [
    {
      "id": "strawberry",
      "name": "Клубника",
      "stock_kg": 600,
      "max_delivery_hours": 6
    }
  ],
  "buyers": [
    {
      "id": "buyer-kaluga",
      "name": "Сеть Калуга",
      "longitude": 36.2613,
      "latitude": 54.5138,
      "orders": [
        {
          "product_id": "strawberry",
          "demand_kg": 250,
          "price_per_kg": 210
        }
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
}
```

- `farm` — одно хозяйство. В ответе его точка имеет `id` = `farm`.
- `products` — не меньше одной культуры. `stock_kg` и `max_delivery_hours` больше 0. Лимит часов относится только ко времени в пути, не к хранению на складе.
- `buyers` — не меньше одного покупателя, у каждого не меньше одного заказа. Координаты обязательны. В заказах одного покупателя `product_id` не повторяется.
- `vehicles` — не меньше одной машины. `max_trips` от 1 до 3: следующий выезд после возврата. Водитель возвращается на хозяйство не позже 12 часов с начала смены. `max_stops` от 1 до 5. При `available: false` машина в план не входит. Стоимость выезда — топливо: `(км / 100) × расход × цена литра`.
- `unload_seconds_per_kg` — секунды разгрузки на килограмм, по умолчанию 0. Погрузка на хозяйстве в срок культуры не входит.
- `time_limit_seconds` — лимит поиска CP-SAT, по умолчанию 25, от 5 до 600. По истечении возвращается лучший найденный план (`feasible`), если оптимум не доказан. Линии рейсов после этого ещё запрашиваются у OSRM.
- Координаты: долгота, широта. Идентификатор покупателя не может быть `farm`.

Полный пример: `GET /api/v1/demo`.

## Ответ `POST /api/v1/plan`

`status`: `optimal`, `feasible`, `infeasible`, `not_solved`.

`objective` — `maximize_profit`.

Денежные поля в рублях:

- `revenue` — сумма `quantity_kg * price_per_kg`;
- `transport_cost` — топливо всех рейсов туда и обратно;
- `profit` — `revenue - transport_cost`.

`shipments` — отгрузки (культура, покупатель, машина, килограммы).

`trips` — выезды: порядок остановок, время до конца разгрузки, километры, стоимость топлива, `waypoints` и GeoJSON `geometry`.

`search_seconds` — сколько секунд заняли сбор модели и поиск CP-SAT (без запросов OSRM).

`balances` по культурам: `stock_kg`, `shipped_kg`, `leftover_kg` (запас минус отгружено), `loss_kg` (равно остатку: невывезенное в этом плане — порча).

`assumptions` — текст допущений модели. `message` — краткий статус расчёта.

## Модель

Цель — максимум прибыли. Культуру можно выгрузить, если прибытие с начала смены (путь плюс разгрузка, плюс ожидание возврата этой машины с прошлых выездов) не превышает `max_delivery_hours`. Машина с `available: false` пропускается.
