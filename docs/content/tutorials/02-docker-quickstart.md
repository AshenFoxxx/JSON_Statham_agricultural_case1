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
Hackaton/
├── docker-compose.yml          # Оркестрация сервисов
├── backend/
│   ├── Dockerfile              # Образ бэкенда (FastAPI)
│   ├── requirements.txt        # Python-зависимости
│   └── app/
│       ├── main.py             # FastAPI приложение
│       ├── models.py           # SQLAlchemy модели
│       ├── crud.py             # CRUD операции
│       ├── database.py         # Подключение к БД
│       └── seed.py             # Начальные данные
├── frontend/
│   ├── Dockerfile              # Образ фронтенда (React)
│   ├── package.json            # Node.js-зависимости
│   └── src/                    # Исходный код React
└── docs/
    ├── Dockerfile              # Образ документации
    └── .dockerignore
```

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
| `db` | PostgreSQL 16 | `5432` | — |
| `backend` | FastAPI + CRUD + Solver | `8000` | `db` |
| `frontend` | React + Vite | `80` | `backend` |

---

## Шаг 3. Запуск всех сервисов

```bash
docker compose up --build
```

Docker запустит:

1. PostgreSQL — база данных
2. Backend — API-сервер с CRUD и solverом
3. Frontend — React-приложение

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

Откройте `http://localhost:8000/docs` — интерактивная документация Swagger UI.

### Frontend

Откройте `http://localhost:80` — React-приложение.

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

---

## Шаг 6. Просмотр логов

```bash
# Все логи
docker compose logs -f

# Только backend
docker compose logs -f backend

# Только frontend
docker compose logs -f frontend

# Только база данных
docker compose logs -f db
```

---

## Шаг 7. Запуск shell внутри контейнера

```bash
# Backend
docker compose exec backend bash

# Frontend
docker compose exec frontend bash

# База данных
docker compose exec db psql -U postgres -d agro_logistics
```

---

## Шаг 8. Проверка здоровья сервисов

```bash
docker compose ps
```

Ожидаемый вывод:

```
NAME                    STATUS       PORTS
hackaton-db-1           Up           0.0.0.0:5432->5432/tcp
hackaton-backend-1      Up           0.0.0.0:8000->8000/tcp
hackaton-frontend-1     Up           0.0.0.0:80->80/tcp
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

---

## Устранение неполадок

### Порт 8000 уже занят

```bash
lsof -i :8000
kill <PID>
```

### Порт 5432 уже занят

```bash
lsof -i :5432
kill <PID>
```

### Ошибка подключения к БД

Убедитесь, что база запущена:

```bash
docker compose ps db
```

Перезапустите базу:

```bash
docker compose up -d db
sleep 5
docker compose up -d backend
```

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
