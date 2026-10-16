# Практическое руководство: Построение маршрута

> **Тип:** How-To Guide (практическое руководство)
> 
> Задача: как построить маршрут между двумя точками.

---

## Задача

Построить маршрут для грузовика между двумя географическими точками и получить интерактивную карту.

---

## Базовое использование

```bash
docker compose run map \
  --from "LON_START,LAT_START" \
  --to "LON_END,LAT_END"
```

**Пример — Москва → Казань:**

```bash
docker compose run map \
  --from "55.7558,37.6173" \
  --to "55.7879,49.1219"
```

---

## С кастомными параметрами топлива

```bash
docker compose run map \
  --from "55.7558,37.6173" \
  --to "59.9343,30.3351" \
  --fuel-price 65 \
  --fuel-consumption 40
```

| Аргумент | Описание | По умолчанию |
|----------|----------|--------------|
| `--from` | Начальная точка `lon,lat` | **обязательный** |
| `--to` | Конечная точка `lon,lat` | **обязательный** |
| `--fuel-price` | Цена топлива, руб/л | `62.0` |
| `--fuel-consumption` | Расход топлива, л/100км | `35.0` |
| `--output` | Папка для выходных файлов | `output` |

---

## Выходные файлы

После выполнения в папке `output/` появятся:

| Файл | Описание |
|------|----------|
| `route.json` | JSON с ключевыми метриками маршрута |
| `route_geometry.json` | GeoJSON геометрия маршрута |
| `route_map.html` | Интерактивная карта (Leaflet) |
| `route_map.js` | JavaScript для карты |
| `frontend/index.html` | Standalone-просмотрщик |

### route.json

```json
{
  "distance_km": 708.42,
  "duration_hours": 8.4,
  "fuel_liters": 247.95,
  "fuel_cost_rub": 15372.90
}
```

### route_geometry.json

```json
{
  "type": "LineString",
  "coordinates": [
    [37.6173, 55.7558],
    [37.7, 55.8],
    ...
  ]
}
```

---

## Просмотр карты

### Вариант 1: route_map.html

Откройте `output/route_map.html` в браузере — это полноценная интерактивная карта с тёмной темой.

### Вариант 2: frontend/index.html

Стандарный просмотрщик, который загружает данные из JSON:

```bash
# Запуск HTTP-сервера для фронтенда
python -m http.server 8080 --directory output
```

Откройте `http://localhost:8080/frontend/index.html`.

---

## Несколько маршрутов

Запустите команду несколько раз с разными координатами — каждый раз будут созданы новые файлы в `output/`.

```bash
docker compose run map --from "55.7558,37.6173" --to "55.7879,49.1219"
docker compose run map --from "55.7879,49.1219" --to "56.8519,60.6122"
```

---

## Ошибки

### OSRM API не нашёл маршрут

```
RuntimeError: OSRM API не нашёл маршрут
```

Проверьте:
- Координаты указаны в правильном формате `lon,lat`
- Точки существуют и связаны дорожной сетью
- Интернет-соединение активно

### Timeout

```
requests.exceptions.Timeout
```

OSRM Public API может быть медленным. Попробуйте ещё раз.

---

<< [Запуск через Docker](/doc/tutorials/02-docker-quickstart) | [Развёртывание сервисов](/doc/how-to/deploy-services) >>
