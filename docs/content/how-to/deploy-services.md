# Практическое руководство: Развертывание сервисов

---

## Быстрый старт

```bash
docker compose up --build
```

---

## Структура сервисов

| Сервис | Описание | Порт | Зависимости |
|--------|----------|------|-------------|
| `db` | PostgreSQL 16 | `5432` | — |
| `backend` | FastAPI + CRUD + Solver | `8000` | `db` |
| `frontend` | React + Vite | `80` | `backend` |

---

## Управление сервисами

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

---

## Управление отдельными сервисами

### Только база данных

```bash
docker compose up db
```

### Только Backend

```bash
docker compose up backend
```

### Только Frontend (локально)

```bash
cd frontend
npm run dev
```

---

## Просмотр логов

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

## Запуск shell внутри контейнера

```bash
# Backend
docker compose exec backend bash

# Frontend
docker compose exec frontend bash

# База данных
docker compose exec db psql -U postgres -d agro_logistics
```

---

## Проверка здоровья сервисов

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

## Проверка API

```bash
# Health check
curl http://localhost:8000/health

# Получить список продуктов
curl http://localhost:8000/api/v1/products

# Получить список покупателей
curl http://localhost:8000/api/v1/buyers

# Получить список транспорта
curl http://localhost:8000/api/v1/vehicles
```

---

## Очистка

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

---

## Мониторинг ресурсов

```bash
docker stats
```

---

## Локальная разработка

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

---

<< [Построение маршрутов](/doc/how-to/build-routes) | [Настройка конфигурации](/doc/how-to/customize-config) >>
