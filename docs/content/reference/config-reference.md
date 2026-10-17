# Справочник: Параметры конфигурации

> **Тип:** Reference (справочник)
> 
> Описание: все константы и параметры конфигурации проекта.

---

## Backend конфигурация

### database.py

| Параметр | Значение | Описание |
|----------|----------|----------|
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/agro_logistics` | URL подключения к PostgreSQL |

### models.py — Модели данных

#### Farm

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Идентификатор (фиксированный: `"farm"`) |
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
| `id` | String | Идентификатор (авто: `order-{product_id}-{buyer_id}`) |
| `product_id` | String | ID продукта |
| `buyer_id` | String | ID покупателя |
| `demand_kg` | Float | Спрос (кг) |
| `price_per_kg` | Float | Цена за кг (₽) |

#### Vehicle

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | String | Уникальный идентификатор |
| `name` | String | Название транспорта |
| `capacity_kg` | Float | Грузоподъёмность (кг) |
| `fuel_consumption_l_per_100km` | Float | Расход топлива (л/100км) |
| `fuel_price_rub_per_liter` | Float | Цена топлива (₽/л) |
| `max_trips` | Integer | Максимум рейсов (1-10) |
| `max_stops` | Integer | Максимум остановок (1-5) |
| `available` | Boolean | Доступен ли транспорт |

---

## Frontend конфигурация

### vite.config.ts

| Параметр | По умолчанию | Описание |
|----------|:------------:|----------|
| `server.port` | `3000` | Порт dev-сервера |

### Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|:------------:|----------|
| `VITE_API_URL` | `http://localhost:8000` | URL бэкенда |

---

## Docker Compose конфигурация

### Сервисы

| Параметр | Значение | Описание |
|----------|----------|----------|
| `db.image` | `postgres:16-alpine` | Образ PostgreSQL |
| `db.ports` | `5432:5432` | Порт базы данных |
| `backend.ports` | `8000:8000` | Порт API |
| `frontend.ports` | `80:80` | Порт веб-интерфейса |

### Переменные окружения

| Переменная | Сервис | По умолчанию | Описание |
|-----------|--------|:------------:|----------|
| `POSTGRES_USER` | db | `postgres` | Имя пользователя БД |
| `POSTGRES_PASSWORD` | db | `postgres` | Пароль БД |
| `POSTGRES_DB` | db | `agro_logistics` | Имя базы данных |
| `DATABASE_URL` | backend | `postgresql://postgres:postgres@db:5432/agro_logistics` | URL подключения к БД |
| `VITE_API_URL` | frontend | `http://localhost:8000` | URL бэкенда |

---

<< [Docker-конфигурация](/doc/reference/docker-reference) | [Почему Docker](/doc/explanation/why-docker) >>
