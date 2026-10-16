# Справочник: Docker-конфигурация

> **Тип:** Reference (справочник)
> 
> Описание: параметры Dockerfile и docker-compose.yml.

---

## docker-compose.yml

```yaml
version: "3.9"

services:
  map:
    build:
      context: ./map
      dockerfile: Dockerfile
    volumes:
      - ./output:/app/output
    working_dir: /app

  docs:
    build:
      context: ./docs
      dockerfile: Dockerfile
    ports:
      - "5001:5001"
    volumes:
      - ./docs/content:/app/content
      - ./docs/static:/app/static
      - ./docs/templates:/app/templates
    working_dir: /app
    command: python server.py --host 0.0.0.0 --port 5001
```

### Параметры services.map

| Параметр | Значение | Описание |
|----------|----------|----------|
| `build.context` | `./map` | Контекст сборки |
| `build.dockerfile` | `Dockerfile` | Файл Dockerfile |
| `volumes` | `./output:/app/output` | Монтирование выходных файлов |
| `working_dir` | `/app` | Рабочая директория |

### Параметры services.docs

| Параметр | Значение | Описание |
|----------|----------|----------|
| `build.context` | `./docs` | Контекст сборки |
| `build.dockerfile` | `Dockerfile` | Файл Dockerfile |
| `ports` | `5001:5001` | Маппинг порта |
| `volumes` | bind mounts | Hot-reload при разработке |
| `command` | `python server.py --host 0.0.0.0` | Запуск сервера |

---

## Map Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
```

### Базовый образ

`python:3.9-slim` — минимальный образ Python 3.9 (~100MB).

### Слои образа

1. `python:3.9-slim` — базовый образ
2. Установка `requests` через pip
3. Копирование исходного кода

---

## Docs Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "5001"]
```

### Базовый образ

`python:3.9-slim` — минимальный образ Python 3.9.

### Слои образа

1. `python:3.9-slim` — базовый образ
2. Установка `flask`, `pyyaml`, `markdown`
3. Копирование кода и шаблонов

---

## .dockerignore

### Для map/

```
__pycache__/
*.pyc
output/
.git/
```

### Для docs/

```
__pycache__/
*.pyc
.git/
```

---

## Команды Docker

### Сборка

```bash
docker compose build
docker compose build --no-cache    # без кэша
docker compose build map            # один сервис
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
docker compose logs -f map
docker compose logs -f docs
docker compose logs -f              # все сервисы
```

### Exec

```bash
docker compose exec map bash
docker compose exec docs bash
```

---

## Переменные окружения

| Переменная | Сервис | Описание |
|-----------|--------|----------|
| `OSRM_API_URL` | map | URL OSRM API |
| `FUEL_PRICE` | map | Цена топлива |
| `FUEL_CONSUMPTION` | map | Расход топлива |
| `FLASK_ENV` | docs | Режим Flask (`development`) |

---

<< [API и данные](/doc/reference/api-reference) | [Параметры конфигурации](/doc/reference/config-reference) >>
