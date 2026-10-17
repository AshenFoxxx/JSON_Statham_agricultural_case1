# Практическое руководство: Развертывание сервисов

## Быстрый старт {#bystryj-start}

```bash
docker compose up --build
```

## Структура сервисов {#struktura}

| Сервис | Описание | Порт (хост) | Зависимости |
|--------|----------|-------------|-------------|
| `backend` | FastAPI + CRUD + CP-SAT Solver | `8000` | — |
| `frontend` | React + Nginx | `3000` | `backend` |

База данных: SQLite хранится в томе `agro-data`. Отдельный контейнер не требуется.

## Управление сервисами {#upravlenie}

### Запуск в фоне

```bash
docker compose up -d
```

### Остановка

```bash
docker compose down
```

### Перезапуск

```bash
docker compose restart
```

### Пересборка и запуск

```bash
docker compose up --build -d
```

## Управление отдельными сервисами {#otdelnye}

### Только Backend

```bash
docker compose up backend
```

### Только Frontend (локально)

```bash
cd frontend
npm run dev
```

## Просмотр логов {#logi}

```bash
# Все логи
docker compose logs -f

# Только backend
docker compose logs -f backend

# Только frontend
docker compose logs -f frontend
```

## Запуск shell внутри контейнера {#shell}

```bash
# Backend
docker compose exec backend bash

# Frontend
docker compose exec frontend bash
```

## Проверка здоровья сервисов {#proverka}

```bash
docker compose ps
```

Ожидаемый вывод:

```
NAME                    STATUS       PORTS
hackaton-backend-1      Up           0.0.0.0:8000->8000/tcp
hackaton-frontend-1     Up           0.0.0.0:3000->80/tcp
```

## Проверка API {#api-check}

```bash
# Health check
curl http://localhost:8000/health

# Получить демо-данные
curl http://localhost:8000/api/v1/demo

# То же тело, что seed (4 культуры, 8 покупателей)
curl http://localhost:8000/api/v1/demo/fleet
```

Полный справочник API см. в разделе [API и данные](/doc/reference/api-reference).

## Очистка {#ochistka}

### Удалить контейнеры и тома

```bash
docker compose down -v
```

### Удалить образы

```bash
docker compose down -v --rmi all
docker system prune -f
```

### Удалить все

```bash
docker compose down -v --rmi all --remove-orphans
```

## Мониторинг ресурсов {#monitoring}

```bash
docker stats
```

## Локальная разработка {#lokalnoe}

### Backend без Docker

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend без Docker

```bash
cd frontend
npm install
npm run dev
```

## База данных {#baza}

По умолчанию используется SQLite. Файл базы данных: `backend/agro.db`.

### Инициализация

При первом запуске создаются таблицы и загружаются демо-данные.

### Сброс данных

Остановите API и удалите `backend/agro.db`. При следующем запуске данные загрузятся заново.

## Docker Compose {#docker-compose}

### Переменные окружения

| Переменная | Сервис | По умолчанию | Описание |
|-----------|--------|:------------:|----------|
| `DATABASE_URL` | backend | `sqlite:///./agro.db` | URL базы данных |

<< [Построение маршрутов](/doc/how-to/build-routes) | [Настройка конфигурации](/doc/how-to/customize-config) >>
