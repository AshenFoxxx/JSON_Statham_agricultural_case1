# Практическое руководство: Настройка конфигурации

> **Тип:** How-To Guide (практическое руководство)
> 
> Задача: изменить параметры проекта под свои нужды.

---

## Задача

Настроить параметры топлива, API и вывода через Docker.

---

## Параметры топлива

### Через CLI-аргументы

```bash
docker compose run map \
  --from "55.7558,37.6173" \
  --to "59.9343,30.3351" \
  --fuel-price 65 \
  --fuel-consumption 40
```

### Через переменные окружения

В `docker-compose.yml` добавьте:

```yaml
services:
  map:
    environment:
      - FUEL_PRICE=65
      - FUEL_CONSUMPTION=40
```

> **Примечание:** CLI-аргументы имеют приоритет над переменными окружения.

---

## Изменение API OSRM

### Production-сервер

По умолчанию используется публичный OSRM:

```
http://router.project-osrm.org/route/v1/driving
```

Для production-использования запустите свой OSRM-сервер:

```bash
# Скачать данные OpenStreetMap
wget http://download.geofabrik.de/europe/russia-central.zip
unzip russian*.zip

# Запустить OSRM
docker run -p 5000:5000 ghcr.io/project-osrm/osrm-backend osrm-routed \
  --algorithm mld /data/russia-central.osrm
```

Затем укажите URL в `config.py`:

```python
OSRM_API_URL = "http://localhost:5000/route/v1/driving"
```

Или через переменную окружения:

```yaml
services:
  map:
    environment:
      - OSRM_API_URL=http://host.docker.internal:5000/route/v1/driving
```

---

## Настройка Docs-сервиса

### Изменение порта

В `docker-compose.yml`:

```yaml
services:
  docs:
    ports:
      - "8080:5001"
```

### Изменение хоста

```yaml
services:
  docs:
    command: python server.py --host 0.0.0.0 --port 5001
```

---

## Настройка вывода

### Папка вывода

```bash
docker compose run map \
  --from "55.7558,37.6173" \
  --to "59.9343,30.3351" \
  --output /app/output
```

### Формат геометрии

В `route_planner.py` строка 26:

```python
# simplified — упрощённая геометрия (меньше данных)
url = f"{OSRM_API_URL}/{coords}?overview=simplified&geometries=geojson"

# full — полная геометрия (больше точек)
url = f"{OSRM_API_URL}/{coords}?overview=full&geometries=geojson"
```

---

## Настройка Docker Compose

### Режим разработки

```yaml
services:
  docs:
    volumes:
      - ./docs/content:/app/content    # Hot-reload markdown
      - ./docs/static:/app/static      # Hot-reload CSS/JS
      - ./docs/templates:/app/templates # Hot-reload templates
    command: python server.py --host 0.0.0.0
```

### Режим продакшн

```yaml
services:
  docs:
    command: gunicorn --bind 0.0.0.0:5001 server:app
```

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `OSRM_API_URL` | URL OSRM API | `http://router.project-osrm.org/route/v1/driving` |
| `FUEL_PRICE` | Цена топлива, руб/л | `62.0` |
| `FUEL_CONSUMPTION` | Расход, л/100км | `35.0` |
| `OUTPUT_DIR` | Папка вывода | `output` |

---

<< [Развёртывание сервисов](/doc/how-to/deploy-services) | [Архитектура системы](/doc/reference/architecture) >>
