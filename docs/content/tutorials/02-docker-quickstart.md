# Обучение: Запуск через Docker

---

## Что вы узнаете

- Как устроен `docker-compose.yml`;
- Как собрать и запустить образы;
- Как проверить работоспособность сервисов;
- Как остановить и перезапустить.

---

## Структура Docker-файлов

```
agr_case1/
├── docker-compose.yml          # Оркестрация сервисов
├── backend/
│   ├── Dockerfile              # Образ бэкенда (FastAPI)
│   ├── requirements.txt        # Python-зависимости
│   └── app/
│       ├── main.py             # FastAPI приложение
│       ├── models.py           # SQLAlchemy модели
│       ├── crud.py             # CRUD операции
│       ├── database.py         # Подключение к БД (SQLite)
│       ├── solver_cp_sat.py    # OR-Tools CP-SAT solver
│       ├── routing.py          # OSRM маршрутизация
│       ├── planning.py         # Построение плана
│       ├── schemas.py          # Pydantic схемы
│       ├── demo_data.py        # Демо-данные
│       └── seed.py             # Начальные данные
├── frontend/
│   ├── Dockerfile              # Образ фронтенда (React)
│   ├── package.json            # Node.js-зависимости
│   └── src/                    # Исходный код React
└── docs/
    ├── Dockerfile              # Образ документации
    └── .dockerignore
```

Полная структура проекта описана в разделе [Архитектура системы](/doc/reference/architecture).

---

## Шаг 1. Проверка Docker

Убедитесь, что Docker установлен и запущен:

```bash
docker --version
docker compose version
```

---

## Шаг 2. Структура сервисов

| Сервис | Описание | Порт | Зависимости |
|--------|----------|------|-------------|
| `backend` | FastAPI + CRUD + CP-SAT Solver | `8000` | — |
| `frontend` | React + Vite | `3000` | `backend` |

База данных: SQLite хранится в томе `agro-data`. Отдельный контейнер не требуется.

---

## Шаг 3. Запуск всех сервисов

```bash
docker compose up --build
```

Docker запустит:

1. Backend — API-сервер с CRUD и solverом;
2. Frontend — React-приложение.

Дождитесь сообщений:

```
backend_1        | Application startup complete.
backend_1        | Uvicorn running on http://0.0.0.0:8000
frontend_1       | Local: http://localhost:3000
```

---

## Шаг 4. Проверка работоспособности

### Backend API

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status": "ok"}
```

### API документация

Откройте `http://localhost:8000/docs` — интерактивная схема API (Swagger).

### Сайт документации

Откройте `http://localhost:3000/doc/` или `http://localhost:5001`.

### Frontend

Откройте `http://localhost:3000` — React-приложение.

---

## Шаг 5. Управление сервисами

### Запуск в фоне

```bash
docker compose up -d
```

### Перезапуск

```bash
docker compose restart
```

### Пересборка и запуск

```bash
docker compose up --build -d
```

### Остановка

```bash
docker compose down
```

### Удаление томов и образов

```bash
docker compose down -v --rmi all
```

Подробные команды управления см. в разделе [Развёртывание сервисов](/doc/how-to/deploy-services).

---

## Шаг 6. Просмотр логов

```bash
# Все логи
docker compose logs -f

# Только backend
docker compose logs -f backend

# Только frontend
docker compose logs -f frontend
```

---

## Шаг 7. Запуск shell внутри контейнера

```bash
# Backend
docker compose exec backend bash

# Frontend
docker compose exec frontend bash
```

---

## Режим разработки

### Backend с hot-reload

```bash
docker compose up backend
```

FastAPI с uvicorn автоматически перезапускается при изменении кода.

### Frontend с hot-reload

```bash
cd frontend
npm run dev
```

Vite автоматически перезагружает при изменении файлов.

Подробнее о локальной разработке см. [Развёртывание сервисов](/doc/how-to/deploy-services).

---

## Устранение неполадок

### Порт 8000 уже занят

```bash
lsof -i :8000
kill <PID>
```

### Ошибка подключения к OSRM

Если OSRM недоступен, API возвращает код 502 при расчёте маршрутов. Проверьте подключение к интернету.

### Ошибка сборки

```bash
docker compose build --no-cache
```

### Логи сервисов

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

---

<< [Первые шаги](/doc/tutorials/01-getting-started) | [Построение маршрутов](/doc/how-to/build-routes) >>
