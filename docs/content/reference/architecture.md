# Справочник: Архитектура системы

## Общая архитектура {#obschaya}

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│                                                          │
│  ┌──────────────────────┐    ┌──────────────────────┐   │
│  │   Service: backend   │    │   Service: frontend  │   │
│  │   (FastAPI)          │    │   (React + Vite)     │   │
│  │                      │    │                      │   │
│  │  main.py             │    │  App.tsx             │   │
│  │    ├─ CRUD API       │    │    ├─ Warehouse      │   │
│  │    ├─ Solver API     │    │    ├─ FarmPage       │   │
│  │    ├─ Route API      │    │    ├─ Buyers         │   │
│  │    └─ Health Check   │    │    ├─ Vehicles       │   │
│  │                      │    │    └─ Routes         │   │
│  │  CP-SAT Solver       │    │                      │   │
│  │  (OR-Tools)          │    │  api/client.ts       │   │
│  │                      │    │  api/solver.ts       │   │
│  │  SQLite ORM          │    │  components/         │   │
│  │                      │    │    ├─ Layout.tsx     │   │
│  │  SQLite Database     │    │    ├─ DataTable.tsx  │   │
│  │  (agro.db)           │    │    ├─ Modal.tsx      │   │
│  │                      │    │    ├─ LocationMap.ts │   │
│  │                      │    │    └─ AllRoutesMap.ts│   │
│  │  OSRM Client         │    │  contexts/           │   │
│  │  (routing.py)        │    │    └─ ThemeContext.ts│   │
│  └──────────────────────┘    └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Структура проекта {#struktura}

```
Hackaton/
├── docker-compose.yml              # Оркестрация сервисов
├── README.md                       # Основная документация
├── backend/
│   ├── Dockerfile                  # Образ бэкенда
│   ├── requirements.txt            # Python-зависимости
│   └── app/
│       ├── main.py                 # FastAPI приложение + API endpoints
│       ├── models.py               # SQLAlchemy модели
│       ├── crud.py                 # CRUD операции с БД
│       ├── database.py             # Подключение к SQLite
│       ├── schemas.py              # Pydantic схемы
│       ├── solver_cp_sat.py        # OR-Tools CP-SAT solver
│       ├── routing.py              # OSRM маршрутизация
│       ├── planning.py             # Построение плана
│       ├── demo_data.py            # Демо-данные
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
│       │   ├── DataTable.tsx       # Таблица данных
│       │   ├── Modal.tsx           # Модальное окно
│       │   ├── LocationMap.tsx     # Карта локации
│       │   ├── PointPickMap.tsx    # Карта выбора точек
│       │   ├── RouteLineMap.tsx    # Карта маршрутов
│       │   └── AllRoutesMap.tsx    # Карта всех рейсов
│       ├── pages/
│       │   ├── Warehouse.tsx       # Склад продукции
│       │   ├── FarmPage.tsx        # Управление хозяйством
│       │   ├── Buyers.tsx          # Покупатели и заказы
│       │   ├── Vehicles.tsx        # Транспорт
│       │   ├── Routes.tsx          # Маршруты доставки
│       │   └── Privacy.tsx         # Политика конфиденциальности
│       ├── types/
│       │   └── index.ts            # TypeScript типы
│       └── contexts/
│           └── ThemeContext.tsx    # Темная/светлая тема
├── demo-map/                       # Отдельная карта маршрутов
└── docs/
    ├── Dockerfile                  # Образ документации
    ├── server.py                   # Flask-сервер документации
    ├── toc.yaml                    # Структура оглавления
    ├── content/                    # Markdown-файлы
    ├── templates/                  # HTML-шаблоны
    └── static/                     # Статические файлы
```

## Зависимости {#zavisimosti}

### Backend

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `fastapi` | >=0.115 | Web-фреймворк |
| `uvicorn` | >=0.32 | ASGI сервер |
| `sqlalchemy` | >=2.0 | ORM |
| `pydantic` | >=2.0 | Валидация данных |
| `ortools` | >=9.10 | OR-Tools CP-SAT solver |
| `httpx` | >=0.27 | HTTP клиент |
| `requests` | >=2.32 | HTTP клиент для OSRM |
| `pytest` | >=8.0 | Тестирование |

### Frontend

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `react` | >=19.0.0 | UI библиотека |
| `react-dom` | >=19.0.0 | ReactDOM |
| `react-router-dom` | >=7.1.0 | Роутинг |
| `ol` | >=10.11.0 | Карты (OpenLayers) |
| `typescript` | >=5.6.0 | Типизация |
| `vite` | >=6.0.0 | Сборщик |
| `tailwindcss` | >=3.4.17 | CSS-фреймворк |
| `@vitejs/plugin-react` | >=4.3.4 | Плагин Vite |
| `postcss` | >=8.4.49 | CSS обработка |
| `autoprefixer` | >=10.4.20 | CSS префиксы |

### Docs

| Пакет | Назначение |
|-------|------------|
| `flask` | Web-фреймворк |
| `pyyaml` | Парсинг toc.yaml |
| `markdown` | Markdown-to-HTML |

## Порты {#porty}

| Сервис | Порт (хост) | Порт (контейнер) | Протокол |
|--------|-------------|------------------|----------|
| Frontend | `3000` | `80` | HTTP |
| Backend | `8000` | `8000` | HTTP |
| Demo-map | `8000/map` | — | HTTP |
| Docs | `5001` | `5001` | HTTP |

## Volumes {#volumes}

| Volume | Mount | Назначение |
|--------|-------|------------|
| `agro-data` | `/data` | Данные SQLite (agro.db) |

## База данных {#baza}

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

## OSRM {#osrm}

OSRM (Open Source Routing Machine) — публичный API для расчёта расстояний и маршрутов по реальным дорогам.

| Эндпоинт | URL | Назначение |
|----------|-----|------------|
| Route | `http://router.project-osrm.org/route/v1/driving` | Маршрут между точками |
| Table | `http://router.project-osrm.org/table/v1/driving` | Матрица расстояний |

API требует подключения к интернету. При недоступности API возвращается HTTP 502.

## CP-SAT Solver {#cp-sat}

CP-SAT (Constraint Programming - SAT) — решатель ограничений от Google OR-Tools. Использует edge-переменные O(n^2) вместо O(n!).

### Переменные модели

| Переменная | Тип | Описание |
|-----------|-----|----------|
| `x[v,t,i,j]` | Bool | Машина v, рейс t, ребро i->j |
| `y[v,t,j]` | Bool | Машина v, рейс t, покупатель j посещён |
| `z[v,t,j,pi]` | Int | Кг продукта pi покупателю j машиной v, рейс t |

### Ограничения

- `AddCircuit` — обход без подциклов, с self-loops для пропущенных узлов
- `max_trips = 1` — один выезд на машину
- `max_stops <= 5` — до 5 покупателей за выезд
- Грузоподъёмность, запас, спрос, время доставки

### Целевая функция

Максимизация прибыли: `revenue - transport_cost`

### Параметры решения

| Параметр | Значение | Описание |
|----------|----------|----------|
| `max_time_in_seconds` | 120 | Лимит времени поиска |
| `num_workers` | 4 | Количество потоков |

## Ограничения {#ogranicheniya}

### Технические ограничения

- OSRM требует подключения к интернету для расчёта расстояний
- При недоступности OSRM API возвращается HTTP 502
- Лимит времени solverа: 120 секунд
- `max_trips` жёстко ограничен значением 1 для всех машин
- База данных — SQLite, не предназначена для высокой нагрузки

### Ограничения модели

- Один выезд со склада на каждую машину (max_trips = 1)
- Машина возвращается на хозяйство после выезда
- Погрузка на хозяйстве не входит в срок культуры
- Отсчёт срока начинается в момент выезда со двора
- Время разгрузки линейно: секунды на килограмм
- Нет учёта пробок и дорожных работ
- Нет учёта погодных условий
- Нет ограничений по весу/высоте для мостов
- Нет учёта времени работы покупателей
- Нет учёта топливных станций по маршруту
- Невывезенный объём остаётся остатком, потеря — только объём, который нельзя доставить ни одному покупателю в срок

### Ограничения API

- Идентификатор `farm` зарезервирован для хозяйства
- У покупателя не может быть одной культуры дважды
- Идентификаторы культур, покупателей и машин должны быть уникальными

<< [Параметры конфигурации](/doc/reference/config-reference) | [API и данные](/doc/reference/api-reference) >>
