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
│  │   Service: map       │    │   Service: docs      │   │
│  │   (Route Planner)    │    │   (Documentation)    │   │
│  │                      │    │                      │   │
│  │  main.py             │    │  server.py (Flask)   │   │
│  │    │                 │    │    │                 │   │
│  │    ├─ route_planner  │    │    ├─ toc.yaml       │   │
│  │    │    │            │    │    ├─ content/*.md   │   │
│  │    │    ▼            │    │    ├─ templates/     │   │
│  │    │  OSRM API       │    │    └─ static/        │   │
│  │    │                │    │                      │   │
│  │    ├─ map_generator  │    └──────────────────────┘   │
│  │    │    │            │               │              │
│  │    │    ▼            │               ▼              │
│  │    │  HTML + JS     │         http://localhost:5001 │
│  │    │  + JSON        │                              │
│  │    └────┬───────────┘                              │
│  │         ▼                                          │
│  │    output/                                         │
│  │    ├── route.json                                 │
│  │    ├── route_geometry.json                        │
│  │    ├── route_map.html                             │
│  │    └── frontend/index.html                        │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Структура проекта

```
Hackaton/
├── docker-compose.yml              # Оркестрация сервисов
├── map/
│   ├── Dockerfile                  # Образ map-сервиса
│   ├── .dockerignore
│   ├── main.py                     # CLI entry point
│   ├── config.py                   # Константы конфигурации
│   ├── route_planner.py            # OSRM + fuel calculation
│   ├── map_generator.py            # Leaflet HTML generation
│   ├── frontend/
│   │   └── index.html              # Standalone map viewer
│   └── output/                     # Выходные данные (gitignored)
│       ├── route.json
│       ├── route_geometry.json
│       ├── route_map.html
│       └── route_map.js
├── docs/
│   ├── Dockerfile                  # Образ docs-сервиса
│   ├── server.py                   # Flask-сервер документации
│   ├── toc.yaml                    # Структура оглавления
│   ├── content/                    # Markdown-файлы
│   │   ├── tutorials/
│   │   ├── how-to/
│   │   ├── reference/
│   │   └── explanation/
│   ├── templates/
│   │   ├── docs.html               # Основной шаблон
│   │   └── 404.html                # Страница ошибки
│   └── static/
│       ├── css/style.css           # Стили
│       └── js/nav.js               # Навигация
└── JSON_Statham_agricultural_case1/
    └── Map/                        # Исходный проект (git repo)
```

---

## Зависимости

### Map-сервис

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `requests` | latest | HTTP-клиент для OSRM API |

### Docs-сервис

| Пакет | Версия | Назначение |
|-------|--------|------------|
| `flask` | latest | Web-фреймворк |
| `pyyaml` | latest | Парсинг toc.yaml |
| `markdown` | latest | Markdown → HTML |

### Внешние зависимости

| Сервис | URL | Назначение |
|--------|-----|------------|
| OSRM Public API | `router.project-osrm.org` | Построение маршрутов |
| OpenStreetMap | `tile.openstreetmap.org` | Картотайлы |
| Leaflet.js | `unpkg.com/leaflet` | Библиотека карт |
| Font Awesome | `cdnjs.cloudflare.com` | Иконки |
| Highlight.js | `cdnjs.cloudflare.com` | Подсветка кода |

---

## Порты

| Сервис | Порт | Протокол |
|--------|------|----------|
| docs | `5001` | HTTP |

> **Примечание:** Map-сервис не имеет открытого порта — это CLI-инструмент.

---

## volumes

| Volume | Mount | Назначение |
|--------|-------|------------|
| `./output:/app/output` | bind | Выходные файлы маршрутов |
| `./docs/content:/app/content` | bind | Markdown-файлы (dev) |
| `./docs/static:/app/static` | bind | Статика (dev) |
| `./docs/templates:/app/templates` | bind | Шаблоны (dev) |

---

<< [Параметры конфигурации](/doc/how-to/customize-config) | [API и данные](/doc/reference/api-reference) >>
