# Справочник: Docker-конфигурация

> **Тип:** Reference (справочник)
> 
> Описание: параметры Dockerfile и docker-compose.yml.

---

## docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: agro_logistics
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/agro_logistics
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

### Параметры services.db

| Параметр | Значение | Описание |
|----------|----------|----------|
| `image` | `postgres:16-alpine` | Образ PostgreSQL 16 |
| `POSTGRES_USER` | `postgres` | Имя пользователя |
| `POSTGRES_PASSWORD` | `postgres` | Пароль |
| `POSTGRES_DB` | `agro_logistics` | Имя базы данных |
| `ports` | `5432:5432` | Маппинг порта |
| `volumes` | `pgdata` | Персистентное хранилище |

### Параметры services.backend

| Параметр | Значение | Описание |
|----------|----------|----------|
| `build.context` | `./backend` | Контекст сборки |
| `ports` | `8000:8000` | Маппинг порта API |
| `environment` | `DATABASE_URL=...` | Подключение к БД |
| `depends_on` | `db` | Зависимость от БД |

### Параметры services.frontend

| Параметр | Значение | Описание |
|----------|----------|----------|
| `build.context` | `./frontend` | Контекст сборки |
| `ports` | `80:80` | Маппинг порта веб-интерфейса |
| `depends_on` | `backend` | Зависимость от бэкенда |

---

## Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Базовый образ

`python:3.11-slim` — минимальный образ Python 3.11.

### Слои образа

1. `python:3.11-slim` — базовый образ
2. Установка зависимостей через pip
3. Копирование исходного кода

---

## Frontend Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Многоступенчатая сборка

1. **Builder** — Node.js собирает React-приложение
2. **Nginx** — раздаёт статические файлы

---

## .dockerignore

### Для backend/

```
__pycache__/
*.pyc
*.egg-info/
venv/
.env
```

### Для frontend/

```
node_modules/
dist/
.env
```

---

## Команды Docker

### Сборка

```bash
docker compose build
docker compose build --no-cache    # без кэша
docker compose build backend        # один сервис
```

### Запуск

```bash
docker compose up                   # foreground
docker compose up -d                # background
docker compose up --build -d        # пересобрать и запустить
```

### Остановка

```bash
docker compose down                 # остановить
docker compose down -v              # + удалить тома
docker compose down -v --rmi all    # + удалить образы
```

### Логи

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
docker compose logs -f              # все сервисы
```

### Exec

```bash
docker compose exec backend bash
docker compose exec frontend bash
docker compose exec db psql -U postgres -d agro_logistics
```

---

## Переменные окружения

| Переменная | Сервис | Описание |
|-----------|--------|----------|
| `DATABASE_URL` | backend | URL подключения к PostgreSQL |
| `VITE_API_URL` | frontend | URL бэкенда |
| `FLASK_ENV` | docs | Режим Flask (`development`) |

---

<< [API и данные](/doc/reference/api-reference) | [Параметры конфигурации](/doc/reference/config-reference) >>
