# Практическое руководство: Настройка конфигурации

## Переменные окружения бэкенда {#peremennye}

### База данных

В `docker-compose.yml` бэкенда:

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=sqlite:////data/agro.db
```

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `DATABASE_URL` | URL подключения к SQLite | `sqlite:////data/agro.db` (Docker) |
| `DATABASE_URL` | URL подключения к SQLite | `sqlite:///./agro.db` (локально) |

### Использование PostgreSQL

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/agrologistics
```

## Настройка Docker Compose {#docker-compose}

### Изменение портов

```yaml
services:
  backend:
    ports:
      - "9000:8000"   # Backend на порту 9000

  frontend:
    ports:
      - "3000:80"     # Frontend на порту 3000
```

### Режим разработки

```yaml
services:
  backend:
    volumes:
      - ./backend/app:/app/app    # Hot-reload кода
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Режим продакшн

```yaml
services:
  backend:
    command: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Настройка Frontend {#frontend}

### Переменные окружения

Создайте файл `.env` в директории `frontend`:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_SOLVER_URL=http://127.0.0.1:8000
```

### Изменение порта

В `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    port: 3000,
  },
})
```

## Переменные окружения {#spisok}

### Backend

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `DATABASE_URL` | URL подключения к БД | `sqlite:///./agro.db` |

### Frontend

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `VITE_API_URL` | URL бэкенда | `http://127.0.0.1:8000` |
| `VITE_SOLVER_URL` | URL solver API | `http://127.0.0.1:8000` |

## База данных {#baza}

### SQLite

По умолчанию используется SQLite. Файл базы данных: `backend/agro.db`.

### Сброс данных

Остановите API и удалите `backend/agro.db`. При следующем запуске данные загрузятся заново.

<< [Развертывание сервисов](/doc/how-to/deploy-services) | [Архитектура системы](/doc/reference/architecture) >>
