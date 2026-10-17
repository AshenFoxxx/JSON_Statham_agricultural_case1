# Справочник: Docker-конфигурация

## docker-compose.yml {#docker-compose-yml}

```yaml
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - agro-data:/data
    environment:
      DATABASE_URL: sqlite:////data/agro.db
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: ""
        VITE_SOLVER_URL: ""
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  agro-data:
```

### Параметры services.backend

| Параметр | Значение | Описание |
|----------|----------|----------|
| `build.context` | `.` (корень проекта) | Контекст сборки |
| `build.dockerfile` | `backend/Dockerfile` | Файл сборки |
| `ports` | `8000:8000` | Маппинг порта API |
| `volumes` | `agro-data:/data` | Том для SQLite базы |
| `environment` | `sqlite:////data/agro.db` | Подключение к SQLite |
| `restart` | `unless-stopped` | Политика перезапуска |

### Параметры services.frontend

| Параметр | Значение | Описание |
|----------|----------|----------|
| `build.context` | `./frontend` | Контекст сборки |
| `build.args` | `VITE_API_URL`, `VITE_SOLVER_URL` | Переменные сборки |
| `ports` | `3000:80` | Маппинг порта веб-интерфейса |
| `depends_on` | `backend` | Зависимость от бэкенда |
| `restart` | `unless-stopped` | Политика перезапуска |

## Backend Dockerfile {#backend-dockerfile}

```dockerfile
FROM python:3.12-slim

WORKDIR /app
RUN mkdir -p /data

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY demo-map /demo-map

ENV DATABASE_URL=sqlite:////data/agro.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Базовый образ

`python:3.12-slim` — минимальный образ Python 3.12.

### Слои образа

1. `python:3.12-slim` — базовый образ
2. Создание каталога `/data` для тома
3. Установка зависимостей через pip
4. Копирование кода бэкенда и demo-map
5. Запуск uvicorn

### Контекст сборки

Dockerfile находится в `backend/`, но контекст сборки — корень проекта. Поэтому пути копирования: `backend/requirements.txt`, `backend/ .`, `demo-map /demo-map`.

## Frontend Dockerfile {#frontend-dockerfile}

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=
ARG VITE_SOLVER_URL=
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SOLVER_URL=$VITE_SOLVER_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Многоступенчатая сборка

1. Builder — Node.js 20 собирает React-приложение
2. Nginx — раздает статические файлы
3. Nginx проксирует `/api/`, `/docs`, `/map/` на бэкенд

### Proxy в Nginx

| Путь | Куда проксируется | Порт бэкенда |
|------|-------------------|-------------|
| `/api/` | `http://backend:8000/api/` | 180s timeout |
| `/health` | `http://backend:8000/health` | — |
| `/docs` | `http://backend:8000/docs` | Swagger UI |
| `/openapi.json` | `http://backend:8000/openapi.json` | — |
| `/redoc` | `http://backend:8000/redoc` | — |
| `/map/` | `http://backend:8000/map/` | Статика |

## Docs Dockerfile {#docs-dockerfile}

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
ENV PYTHONUNBUFFERED=1
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "5001"]
```

Docs-сервис запускается отдельно от docker-compose. Это Flask-приложение на порту 5001.

## .dockerignore {#dockerignore}

### Для backend/

```
__pycache__/
*.pyc
*.egg-info/
venv/
.env
agro.db
```

### Для frontend/

```
node_modules/
dist/
.env
```

## Команды Docker {#komandy}

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
docker compose logs -f              # все сервисы
```

### Exec

```bash
docker compose exec backend bash
docker compose exec frontend bash
```

## Локальный запуск без Docker

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

### Docs

```bash
cd docs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

## Переменные окружения {#peremennye}

| Переменная | Сервис | Описание |
|-----------|--------|----------|
| `DATABASE_URL` | backend | URL подключения к SQLite |
| `VITE_API_URL` | frontend | URL бэкенда (для сборки и runtime) |
| `VITE_SOLVER_URL` | frontend | URL solver API (для сборки и runtime) |
| `FLASK_ENV` | docs | Режим Flask (`development`) |

<< [API и данные](/doc/reference/api-reference) | [Параметры конфигурации](/doc/reference/config-reference) >>
