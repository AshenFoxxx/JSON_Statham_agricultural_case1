# Обучение: Запуск через Docker

> **Тип:** Tutorial (обучающее руководство)
> 
> Цель: подробный пошаговый запуск всех сервисов в Docker.

---

## Что вы узнаете

- Как устроен `docker-compose.yml`
- Как собрать и запустить образы
- Как проверить работоспособность сервисов
- Как остановить и перезапустить

---

## Структура Docker-файлов

```
Hackaton/
├── docker-compose.yml          # Оркестрация двух сервисов
├── map/
│   ├── Dockerfile              # Образ сервиса маршрутизации
│   └── .dockerignore
└── docs/
    ├── Dockerfile              # Образ сервиса документации
    └── .dockerignore
```

---

## Шаг 1. Проверка Docker

Убедитесь, что Docker установлен и запущен:

```bash
docker --version
docker compose version
```

---

## Шаг 2. Сборка образов

```bash
docker compose build
```

Docker соберёт два образа:

1. **`map`** — Python 3.9 + зависимости для планировщика маршрутов
2. **`docs`** — Python 3.9 + Flask для документации

---

## Шаг 3. Запуск

```bash
docker compose up
```

Сервисы запустятся в фоне. В терминале вы увидите:

```
Starting hackaton-map-1 ... done
Starting hackaton-docs-1 ... done
Attaching to hackaton-map-1, hackaton-docs-1
```

---

## Шаг 4. Проверка работоспособности

### Docs-сервис

```bash
curl http://localhost:5001
```

Ожидается: редирект на первую страницу документации.

### API TOC

```bash
curl http://localhost:5001/api/toc
```

Ожидается: JSON со структурой оглавления.

---

## Шаг 5. Построение маршрута

В отдельном терминале:

```bash
docker compose run map \
  --from "55.7558,37.6173" \
  --to "37.6173,55.7558" \
  --fuel-price 62 \
  --fuel-consumption 35
```

Результат появится в папке `output/`.

---

## Шаг 6. Остановка

```bash
docker compose down
```

Для удаления томов и пересборки:

```bash
docker compose down -v --rmi all
```

---

## Режим разработки

Для автоперезагрузки docs-сервиса при изменении файлов:

```bash
docker compose up docs
```

Flask запущен в режиме `debug=True` — при изменении `.py` или `.md` файлов сервер перезапустится автоматически.

---

## Troubleshooting

### Порт 5001 уже занят

Измените порт в `docker-compose.yml`:

```yaml
ports:
  - "8080:5001"
```

### Ошибка сборки

```bash
docker compose build --no-cache
```

### Логи сервисов

```bash
docker compose logs -f map
docker compose logs -f docs
```

---

<< [Первые шаги](/doc/tutorials/01-getting-started) | [Построение маршрута](/doc/how-to/build-routes) >>
