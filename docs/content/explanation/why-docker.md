# Объяснение: Почему Docker

## Контекст {#kontekst}

Проект АгроЛогистика состоит из двух независимых компонентов:

- Frontend — React-приложение с TypeScript и Tailwind CSS;
- Backend — FastAPI-сервер с CRUD API и CP-SAT solverом.

База данных — SQLite, хранится в файле и не требует отдельного сервиса.

Все компоненты имеют разные языки, зависимости и требования к окружению.

## Проблемы без Docker {#problemy}

### 1. Различия в окружениях

Разработчики используют разные ОС (macOS, Linux, Windows). Без Docker:

- у кого-то Python 3.12, у кого-то другая версия;
- node.js версии 18, 20;
- пути к файлам различаются (`/` vs `\`).

Результат: «У меня на машине работает»

### 2. Зависимости

```
# Без Docker — каждый ставит вручную:
pip install fastapi uvicorn sqlalchemy pydantic ortools httpx requests
npm install react typescript tailwindcss vite ol
```

Нет гарантии, что версии совпадают.

### 3. Запуск нескольких сервисов

```bash
# Нужно открыть 2 терминала:
cd backend && uvicorn app.main:app --reload &    # backend на порту 8000
cd frontend && npm run dev &                      # frontend на порту 3000
```

### 4. Передача проекта

```
# Без Docker:
1. Установи Python 3.12
2. Установи Node.js 20
3. Создай venv, pip install
4. npm install
5. Запусти 2 сервиса
6. ...и забудь про 5 ошибок в зависимостях

# С Docker:
docker compose up --build
```

## Решения с Docker {#resheniya}

### 1. Детерминированное окружение

```dockerfile
# Backend
FROM python:3.12-slim

# Frontend
FROM node:20-alpine AS builder
```

Одинаковый Python 3.12 и Node.js 20 на любой машине.

### 2. Инкапсуляция зависимостей

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

Зависимости зафиксированы в `requirements.txt` и `package.json`.

### 3. Единый интерфейс запуска

```bash
docker compose up --build
```

Одна команда — все сервисы запущены.

### 4. Изоляция сервисов

```yaml
services:
  backend:   # FastAPI на порту 8000
  frontend:  # React на порту 3000 (80 внутри контейнера)
```

Каждый сервис изолирован и занимает свой порт.

### 5. Повторное использование

Образы можно:

- Публиковать в Docker Hub / GHCR;
- Запускать на CI/CD;
- Деплоить на сервер.

## Почему не виртуальное окружение?

| Критерий | venv | Docker |
|----------|------|--------|
| Изоляция ОС | ❌ | ✅ |
| Один запуск всех сервисов | ❌ | ✅ |
| Передача окружения | ❌ | ✅ |
| CI/CD интеграция | ❌ | ✅ |
| Ресурсы | Легче | Тяжелее |

Venv подходит для одиночных проектов. Docker — для проектов с несколькими сервисами и командной работой.

## Trade-offs {#trade-offs}

### Плюсы

- Одинаковое окружение на всех машинах;
- Один способ запуска;
- Легкая передача проекта;
- Готовность к CI/CD и деплою.

### Минусы

- Нужно установить Docker Desktop (~4GB);
- Образы занимают место (~500MB на все образы);
- Дополнительные файлы (Dockerfile, docker-compose.yml);
- Сложнее отлаживать (нет прямого доступа к файловой системе).

<< [Параметры конфигурации](/doc/reference/config-reference) | [Как работает расчет маршрутов](/doc/explanation/how-route-calculation-works) >>
