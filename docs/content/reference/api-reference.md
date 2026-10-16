# Справочник: API и данные

> **Тип:** Reference (справочник)
> 
> Описание: форматы запросов, ответов и файлов данных.

---

## OSRM API

### Endpoint

```
GET http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}
```

### Параметры запроса

| Параметр | Описание | Пример |
|----------|----------|--------|
| `overview` | Уровень детализации | `simplified` / `full` |
| `geometries` | Формат геометрии | `geojson` |

### Пример запроса

```
GET http://router.project-osrm.org/route/v1/driving/37.6173,55.7558;30.3351,59.9343?overview=simplified&geometries=geojson
```

### Ответ OSRM

```json
{
  "routes": [
    {
      "distance": 708420.5,
      "duration": 30240.3,
      "geometry": {
        "type": "LineString",
        "coordinates": [
          [37.6173, 55.7558],
          [37.7, 55.8],
          [30.3351, 59.9343]
        ]
      }
    }
  ],
  "code": "Ok"
}
```

### Коды ответа

| Код | Описание |
|-----|----------|
| `Ok` | Успех |
| `NoRoute` | Маршрут не найден |
| `Unknown` | Неизвестная ошибка |

---

## Форматы выходных данных

### route.json

```json
{
  "distance_km": 708.42,
  "duration_hours": 8.4,
  "fuel_liters": 247.95,
  "fuel_cost_rub": 15372.90
}
```

| Поле | Тип | Описание |
|------|-----|----------|
| `distance_km` | float | Расстояние в километрах |
| `duration_hours` | float | Время в пути в часах |
| `fuel_liters` | float | Расход топлива в литрах |
| `fuel_cost_rub` | float | Стоимость топлива в рублях |

### route_geometry.json

```json
{
  "type": "LineString",
  "coordinates": [
    [37.6173, 55.7558],
    [37.7, 55.8],
    [30.3351, 59.9343]
  ]
}
```

Формат GeoJSON LineString.

### route_map.html

Самодостаточный HTML-файл с:
- Leaflet.js (CDN)
- Inline CSS (тёмная тема)
- Inline JavaScript
- Встроенные данные маршрута

### frontend/index.html

Стандарный HTML-просмотрщик, загружающий `route.json` и `route_geometry.json` через `fetch()`.

---

## Docs API

### GET /

Редирект на первую страницу TOC.

### GET /doc/{page_name}

Рендеринг markdown-страницы.

| Параметр | Описание |
|----------|----------|
| `page_name` | Имя страницы (stem файла) |

Пример: `/doc/architecture` → `reference/architecture.md`

### GET /api/toc

Возвращает структуру TOC в JSON.

**Ответ:**

```json
{
  "toc": [
    {
      "title": "Обучение",
      "file": "tutorials/01-getting-started.md",
      "children": [...]
    }
  ],
  "flat": [
    {
      "title": "Первые шаги",
      "file": "tutorials/01-getting-started.md",
      "url": "/doc/tutorials/01-getting-started"
    }
  ]
}
```

---

<< [Архитектура системы](/doc/reference/architecture) | [Docker-конфигурация](/doc/reference/docker-reference) >>
