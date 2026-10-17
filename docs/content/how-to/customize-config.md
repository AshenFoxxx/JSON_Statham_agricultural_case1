# Практическое руководство: Настройка конфигурации

> **Тип:** How-To Guide (практическое руководство)
> 
> Задача: изменить параметры проекта под свои нужды.

---

## Задача

Настроить параметры базы данных, API и переменные окружения.

---

## Переменные окружения бэкенда

### База данных

В `docker-compose.yml` бэкенда:

```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/agro_logistics
```

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres@db:5432/agro_logistics` |

### Изменение параметров БД

```yaml
services:
  db:
    environment:
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
      POSTGRES_DB: mydb
  backend:
    environment:
      - DATABASE_URL=postgresql://myuser:mypassword@db:5432/mydb
```

---

## Настройка Docker Compose

### Изменение портов

```yaml
services:
  db:
    ports:
      - "5433:5432"   # БД на порту 5433
  
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

---

## Настройка базы данных

### Подключение к БД

```bash
docker compose exec db psql -U postgres -d agro_logistics
```

### Создание резервной копии

```bash
docker compose exec db pg_dump -U postgres agro_logistics > backup.sql
```

### Восстановление из резервной копии

```bash
cat backup.sql | docker compose exec -T db psql -U postgres agro_logistics
```

### Сброс данных

```bash
docker compose down -v
docker compose up -d db
docker compose up -d backend
```

---

## Настройка Frontend

### Переменные окружения

Создайте файл `.env` в директории `frontend`:

```env
VITE_API_URL=http://localhost:8000
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

---

## Настройка PostgreSQL

### Изменение параметров

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: agro_logistics
    command: >
      postgres
      -c max_connections=100
      -c shared_buffers=256MB
      -c effective_cache_size=512MB
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
```

---

## Переменные окружения

### Backend

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql://postgres:postgres@db:5432/agro_logistics` |

### Frontend

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `VITE_API_URL` | URL бэкенда | `http://localhost:8000` |

---

<< [Развёртывание сервисов](/doc/how-to/deploy-services) | [Архитектура системы](/doc/reference/architecture) >>
