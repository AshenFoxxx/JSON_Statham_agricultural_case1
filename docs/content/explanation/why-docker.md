# Объяснение: Почему Docker

---

## Контекст

Проект АгроЛогистика состоит из трех независимых компонентов:

- Frontend — React-приложение с TypeScript и Tailwind CSS;
- Backend — FastAPI-сервер с CRUD API и solverом маршрутизации;
- PostgreSQL — реляционная база данных.

Все три компонента имеют разные языки, зависимости и требования к окружению.

---

## Проблемы без Docker

### 1. Различия в окружениях

Разработчики используют разные ОС (macOS, Linux, Windows). Без Docker:

- у кого-то Python 3.11, у кого-то 3.12;
- node.js версии 18, 20, 22;
- postgresql установлен локально или отсутствует;
- пути к файлам различаются (`/` vs `\`).

Результат: «У меня на машине работает»

### 2. Зависимости

```
# Без Docker — каждый ставит вручную:
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic alembic
npm install react typescript tailwindcss vite
# + установить PostgreSQL
```

Нет гарантии, что версии совпадают.

### 3. Запуск нескольких сервисов

```bash
# Нужно открыть 3 терминала:
cd backend && uvicorn app.main:app --reload &    # backend на порту 8000
cd frontend && npm run dev &                      # frontend на порту 3000
# + запустить PostgreSQL
```

### 4. Делегирование

Передача проекта новому разработчику:

```
# Без Docker:
1. Установи Python 3.11
2. Установи Node.js 18
3. Установи PostgreSQL
4. Создай venv, pip install
5. npm install
6. Настрой базу данных
7. Запусти 3 сервиса
8. ...и забудь про 5 ошибок в зависимостях

# С Docker:
docker compose up --build
```

---

## Решения с Docker

### 1. Детерминированное окружение

```dockerfile
# Backend
FROM python:3.11-slim

# Frontend
FROM node:18-alpine AS builder
```

Одинаковый Python 3.11 и Node.js 18 на любой машине.

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

Одна команда — все три сервиса запущены.

### 4. Изоляция сервисов

```yaml
services:
  db:      # PostgreSQL на порту 5432
  backend: # FastAPI на порту 8000
  frontend: # React на порту 80
```

Каждый сервис изолирован и занимает свой порт.

### 5. Повторное использование

Образы можно:

- Публиковать в Docker Hub / GHCR;
- Запускать на CI/CD;
- Деплоить на сервер.

---

## Почему не виртуальное окружение?

| Критерий | venv | Docker |
|----------|------|--------|
| Изоляция ОС | ❌ | ✅ |
| Один запуск всех сервисов | ❌ | ✅ |
| Передача окружения | ❌ | ✅ |
| CI/CD интеграция | ❌ | ✅ |
| Ресурсы | Легче | Тяжелее |

Venv подходит для одиночных проектов. Docker — для проектов с несколькими сервисами и командной работой.

---

## Trade-offs

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

---

<< [Параметры конфигурации](/doc/reference/config-reference) | [Как работает расчет маршрутов](/doc/explanation/how-route-calculation-works) >>
