# Справочник: Параметры конфигурации

## Backend конфигурация {#backend}

### database.py

| Параметр | Значение | Описание |
|----------|----------|----------|
| `DATABASE_URL` | `sqlite:///./agro.db` | URL подключения к SQLite (локально) |
| `DATABASE_URL` | `sqlite:////data/agro.db` | URL подключения к SQLite (Docker) |

### models.py — Модели данных {#modeli}

#### Farm

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Идентификатор (фиксированный: "farm") |
| `name` | String | Название хозяйства |
| `longitude` | Float | Долгота |
| `latitude` | Float | Широта |

#### Product

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Уникальный идентификатор |
| `name` | String | Название культуры |
| `stock_kg` | Float | Запас на складе (кг) |
| `max_delivery_hours` | Float | Максимальное время доставки (часы) |

#### Buyer

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Уникальный идентификатор |
| `name` | String | Название покупателя |
| `longitude` | Float | Долгота |
| `latitude` | Float | Широта |

#### BuyerOrder

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Идентификатор (авто: UUID) |
| `product_id` | String | ID продукта |
| `buyer_id` | String | ID покупателя |
| `demand_kg` | Float | Спрос (кг) |
| `price_per_kg` | Float | Цена за кг (₽) |

#### Vehicle

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Уникальный идентификатор |
| `name` | String | Название транспорта |
| `capacity_kg` | Float | Грузоподъемность (кг) |
| `fuel_consumption_l_per_100km` | Float | Расход топлива (л/100км) |
| `fuel_price_rub_per_liter` | Float | Цена топлива (₽/л) |
| `max_trips` | Integer | Максимум рейсов (жестко: 1) |
| `max_stops` | Integer | Максимум остановок (1-5) |
| `available` | Boolean | Доступен ли транспорт |

## Frontend конфигурация {#frontend}

### vite.config.ts

| Параметр | По умолчанию | Описание |
|----------|:------------:|----------|
| `server.port` | `3000` | Порт dev-сервера |

### Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|:------------:|----------|
| `VITE_API_URL` | `http://localhost:8000` | URL бэкенда |

## Docker Compose конфигурация {#docker-compose}

### Сервисы

| Параметр | Значение | Описание |
|----------|----------|----------|
| `backend.ports` | `8000:8000` | Порт API |
| `frontend.ports` | `3000:80` | Порт веб-интерфейса |

### Переменные окружения

| Переменная | Сервис | По умолчанию | Описание |
|-----------|--------|:------------:|----------|
| `DATABASE_URL` | backend | `sqlite:////data/agro.db` | URL подключения к БД (Docker) |
| `DATABASE_URL` | backend | `sqlite:///./agro.db` | URL подключения к БД (локально) |
| `VITE_API_URL` | frontend | `http://localhost:8000` | URL бэкенда |
| `VITE_SOLVER_URL` | frontend | `http://localhost:8000` | URL solver API |

<< [Docker-конфигурация](/doc/reference/docker-reference) | [Почему Docker](/doc/explanation/why-docker) >>
