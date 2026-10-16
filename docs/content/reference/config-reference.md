# Справочник: Параметры конфигурации

> **Тип:** Reference (справочник)
> 
> Описание: все константы и параметры конфигурации проекта.

---

## config.py

### OSRM

| Константа | Значение | Описание |
|-----------|----------|----------|
| `OSRM_API_URL` | `"http://router.project-osrm.org/route/v1/driving"` | Базовый URL OSRM API |

### Топливо

| Константа | Значение | Описание |
|-----------|----------|----------|
| `DEFAULT_FUEL_CONSUMPTION_L_PER_100KM` | `35.0` | Расход топлива по умолчанию (л/100км) |
| `DEFAULT_FUEL_PRICE_PER_LITER` | `62.0` | Цена топлива по умолчанию (руб/л) |

### Вывод

| Константа | Значение | Описание |
|-----------|----------|----------|
| `OUTPUT_DIR` | `"output"` | Папка для выходных файлов |
| `OUTPUT_JSON_FILE` | `"route.json"` | Имя JSON-файла |
| `OUTPUT_HTML_FILE` | `"route_map.html"` | Имя HTML-файла карты |
| `GEOMETRY_FILE` | `"route_geometry.json"` | Имя GeoJSON-файла |
| `FRONTEND_DIR` | `"frontend"` | Папка фронтенда |

---

## CLI-аргументы (main.py)

| Аргумент | Тип | Обязательный | По умолчанию | Описание |
|----------|-----|:-----------:|--------------|----------|
| `--from` | string | **да** | — | Начальная точка `lon,lat` |
| `--to` | string | **да** | — | Конечная точка `lon,lat` |
| `--fuel-price` | float | нет | `62.0` | Цена топлива, руб/л |
| `--fuel-consumption` | float | нет | `35.0` | Расход, л/100км |
| `--output` | string | нет | `"output"` | Папка вывода |

---

## Форматы координат

Формат: `longitude,latitude` (долгота, широта)

| Город | Координаты |
|-------|-----------|
| Москва | `55.7558,37.6173` |
| Санкт-Петербург | `59.9343,30.3351` |
| Казань | `55.7879,49.1219` |
| Нижний Новгород | `56.2965,43.9361` |
| Екатеринбург | `56.8389,60.5975` |

---

## Формулы расчёта

### Расход топлива

```
fuel_liters = (distance_km / 100) * fuel_consumption
```

### Стоимость

```
fuel_cost = fuel_liters * fuel_price
```

### Время в пути

```
duration_hours = duration_seconds / 3600
```

---

## Переменные окружения

| Переменная | Сервис | Тип | По умолчанию | Описание |
|-----------|--------|-----|:------------:|----------|
| `OSRM_API_URL` | map | string | `http://router.project-osrm.org/route/v1/driving` | URL OSRM API |
| `FUEL_PRICE` | map | float | `62.0` | Цена топлива, руб/л |
| `FUEL_CONSUMPTION` | map | float | `35.0` | Расход, л/100км |
| `FLASK_ENV` | docs | string | `development` | Режим Flask |

---

<< [Docker-конфигурация](/doc/reference/docker-reference) | [Почему Docker](/doc/explanation/why-docker) >>
