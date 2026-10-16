# АгроЛогистика — Backend API

FastAPI-сервер для управления данными сельскохозяйственной логистики.

## Что хранит база

Только вводные данные, которые вводит человек. Расстояния, время в пути, топливо, маршруты — результат расчёта, не хранятся.

| Сущность | Поля |
|----------|------|
| **Farm** (хозяйство) | name, longitude, latitude |
| **Product** (культура) | id, name, stock_kg, max_delivery_hours |
| **Buyer** (покупатель) | id, name, longitude, latitude |
| **BuyerOrder** (заказ) | product_id, buyer_id, demand_kg, price_per_kg |
| **Vehicle** (машина) | id, name, capacity_kg, fuel_consumption_l_per_100km, fuel_price_rub_per_liter, max_trips, max_stops, available |

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

### Локально (PostgreSQL)

```bash
# Запустить PostgreSQL
# Mac: brew install postgresql && brew services start postgresql

# Создать базу
createdb agro_logistics

# Инициализировать таблицы
python -c "from app.database import Base; from app.models import *; Base.metadata.create_all(bind=engine)"

# Заполнить моковыми данными
python -m app.seed

# Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
docker compose up --build
```

Сервер: http://localhost:8000
API docs: http://localhost:8000/docs

## API Endpoints

### Хозяйство

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/farm` | Получить хозяйство |
| POST | `/api/v1/farm` | Создать/обновить хозяйство |
| PUT | `/api/v1/farm` | Обновить хозяйство |

### Продукция

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/products` | Список культур |
| POST | `/api/v1/products` | Добавить культуру |
| PUT | `/api/v1/products/{id}` | Обновить культуру |
| DELETE | `/api/v1/products/{id}` | Удалить культуру |

### Покупатели

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/buyers` | Список покупателей |
| POST | `/api/v1/buyers` | Добавить покупателя |
| PUT | `/api/v1/buyers/{id}` | Обновить покупателя |
| DELETE | `/api/v1/buyers/{id}` | Удалить покупателя |

### Заказы

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/orders` | Список заказов |
| POST | `/api/v1/orders` | Добавить заказ |
| PUT | `/api/v1/orders/{product_id}/{buyer_id}` | Обновить заказ |
| DELETE | `/api/v1/orders/{product_id}/{buyer_id}` | Удалить заказ |

### Машины

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/vehicles` | Список машин |
| POST | `/api/v1/vehicles` | Добавить машину |
| PUT | `/api/v1/vehicles/{id}` | Обновить машину |
| DELETE | `/api/v1/vehicles/{id}` | Удалить машину |

### Планирование

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/v1/plan` | Рассчитать план поставок |

### Health

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка работоспособности |

## Пример запроса на расчёт

```bash
curl -X POST http://localhost:8000/api/v1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "farm": { "name": "Хозяйство Обнинск", "longitude": 36.6103, "latitude": 55.0969 },
    "products": [
      { "id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6 }
    ],
    "buyers": [
      {
        "id": "buyer-kaluga",
        "name": "Сеть Калуга",
        "longitude": 36.2754,
        "latitude": 54.5293,
        "orders": [
          { "product_id": "strawberry", "demand_kg": 250, "price_per_kg": 210 }
        ]
      }
    ],
    "vehicles": [
      {
        "id": "vehicle-a",
        "name": "Газель А",
        "capacity_kg": 800,
        "fuel_consumption_l_per_100km": 10,
        "fuel_price_rub_per_liter": 60,
        "max_trips": 2,
        "max_stops": 3,
        "available": true
      }
    ]
  }'
```

## Структура

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI приложение + API endpoints
│   ├── models.py        # SQLAlchemy модели
│   ├── database.py      # Подключение к PostgreSQL
│   ├── crud.py          # Операции CRUD
│   └── seed.py          # Моковые данные
├── alembic/             # Миграции БД
├── requirements.txt
├── Dockerfile
└── .gitignore
```

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **PostgreSQL** — база данных
- **Pydantic** — валидация
- **Uvicorn** — ASGI сервер
