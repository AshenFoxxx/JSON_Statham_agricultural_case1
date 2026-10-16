# Справочник: Архитектура системы

> **Тип:** Reference (справочник)
> 
> Описание: полная структура проекта и компонентов.

---

## Общая архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────────────┐    ┌──────────────────────┐   │
│  │   Service: db        │    │   Service: backend   │   │
│  │   (PostgreSQL 16)    │    │   (FastAPI)          │   │
│  │                      │    │                      │   │
│  │  agro_logistics      │    │  main.py             │   │
│  │  ┌────────┐          │    │    ├─ CRUD API       │   │
│  │  │ farms  │          │    │    ├─ Solver API     │   │
│  │  │products│          │    │    └─ Health Check   │   │
│  │  │buyers  │          │    │                      │   │
│  │  │orders  │          │    │  SQLAlchemy ORM      │   │
│  │  │vehicles│          │    │      │               │   │
│  │  └────────┘          │    │      ▼               │   │
│  └──────────────────────┘    │  PostgreSQL          │   │
│         ▲                    │      ▲               │   │
│         │ HTTP               │      │               │   │
│  ┌──────────────────────┐    │      │               │   │
│  │   Service: frontend  │    └──────┘               │   │
│  │   (React + Vite)     │                           │   │
│  │                      │                           │   │
│  │  App.tsx             │                           │   │
│  │    ├─ Warehouse      │                           │   │
│  │    ├─ FarmPage       │                           │   │
│  │    ├─ Buyers         │                           │   │
│  │    ├─ Vehicles       │                           │   │
│  │    └─ Routes         │                           │   │
│  │                      │                           │   │
│  │  api/client.ts       │                           │   │
│  │    ├─ productsApi    │                           │   │
│  │    ├─ buyersApi      │                           │   │
│  │    ├─ vehiclesApi    │                           │   │
│  │    ├─ ordersApi      │                           │   │
│  │    └─ solverApi      │                           │   │
│  └──────────────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

---

## Структура проекта

```
Hackaton/
├── docker-compose.yml              # Оркестрация сервисов
├── README.md                       # Основная документация
├── backend/
│   ├── Dockerfile                  # Образ бэкенда
│   ├── requirements.txt            # Python-зависимости
│   └── app/
│       ├── main.py                 # FastAPI приложение + API endpoints
│       ├── models.py               # SQLAlchemy модели (Farm, Product, Buyer, Order, Vehicle)
│       ├── crud.py                 # CRUD операции с БД
│       ├── database.py             # Подключение к PostgreSQL
│       └── seed.py                 # Начальные данные
├── frontend/
│   ├── Dockerfile                  # Образ фронтенда
│   ├── package.json                # Node.js-зависимости
│   ├── vite.config.ts              # Конфигурация Vite
│   ├── tailwind.config.js          # Конфигурация Tailwind CSS
│   └── src/
│       ├── main.tsx                # Точка входа React
│       ├── App.tsx                 # Роутинг
│       ├── api/
│       │   ├── client.ts           # API клиент (REST запросы)
│       │   └── solver.ts           # Solver API
│       ├── components/
│       │   ├── Layout.tsx          # Макет приложения
│       │   ├── DataTable.tsx       | Таблица данных
│       │   └── Modal.tsx           | Модальное окно
│       ├── pages/
│       │   ├── Warehouse.tsx       # Склад продукции
│       │   ├── FarmPage.tsx        # Управление хозяйством
│       │   ├── Buyers.tsx          # Покупатели и заказы
│       │   ├── Vehicles.tsx        # Транспорт
│       │   └── Routes.tsx          # Маршруты доставки
│       ├── types/
│       │   └── index.ts            # TypeScript типы
│       └── contexts/
│           └── ThemeContext.tsx    # Тёмная/светлая тема
└── docs/
    ├── Dockerfile                  # Образ документации
    ├── server.py                   # Flask-сервер документации
    ├── toc.yaml                    # Структура оглавления
    ├── content/                    # Markdown-файлы
    ├── templates/                  # HTML-шаблоны
    └── static/                     # Статические файлы
```

---

## Зависимости

### Backend

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `fastapi` | 0.115.0 | Web-фреймворк |
| `uvicorn` | 0.30.0 | ASGI сервер |
| `sqlalchemy` | 2.0.35 | ORM |
| `psycopg2-binary` | 2.9.9 | PostgreSQL драйвер |
| `pydantic` | 2.9.0 | Валидация данных |
| `alembic` | 1.13.0 | Миграции БД |

### Frontend

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `react` | 18.x | UI библиотека |
| `typescript` | — | Типизация |
| `tailwindcss` | — | CSS-фреймворк |
| `vite` | 6.x | Сборщик |
| `react-router-dom` | — | Роутинг |

---

## Порты

| Сервис | Порт | Протокол |
|--------|------|----------|
| Frontend | `80` | HTTP |
| Backend | `8000` | HTTP |
| PostgreSQL | `5432` | TCP |
| Docs | `5001` | HTTP |

---

## volumes

| Volume | Mount | Назначение |
|--------|-------|------------|
| `pgdata` | `/var/lib/postgresql/data` | Данные PostgreSQL |
| `./backend/app:/app/app` | bind | Код бэкенда (dev) |
| `./docs/content:/app/content` | bind | Markdown-файлы (dev) |
| `./docs/static:/app/static` | bind | Статика (dev) |
| `./docs/templates:/app/templates` | bind | Шаблоны (dev) |

---

## База данных

### Таблицы

| Таблица | Описание | Ключевые поля |
|---------|----------|---------------|
| `farms` | Хозяйство (ферма) | id, name, longitude, latitude |
| `products` | Продукция | id, name, stock_kg, max_delivery_hours |
| `buyers` | Покупатели | id, name, longitude, latitude |
| `buyer_orders` | Заказы | product_id, buyer_id, demand_kg, price_per_kg |
| `vehicles` | Транспорт | id, name, capacity_kg, max_trips, max_stops |

### Связи

```
Farm 1───* Product
Buyer 1───* BuyerOrder *───1 Product
```

---

<< [Параметры конфигурации](/doc/reference/config-reference) | [API и данные](/doc/reference/api-reference) >>
