# Практическое руководство: Развёртывание сервисов

> **Тип:** How-To Guide (практическое руководство)
> 
> Задача: развернуть и управлять сервисами проекта.

---

## Задача

Запустить, настроить и управлять сервисами проекта в Docker.

---

## Быстрый старт

```bash
docker compose up --build
```

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

### Только Docs-сервис

```bash
docker compose up docs
```

### Только Map (одноразовый запуск)

```bash
docker compose run map --from "55.7558,37.6173" --to "59.9343,30.3351"
```

---

## Просмотр логов

```bash
# Все логи
docker compose logs -f

# Только map
docker compose logs -f map

# Только docs
docker compose logs -f docs
```

---

## Запуск shell внутри контейнера

```bash
# Map-сервис
docker compose exec map bash

# Docs-сервис
docker compose exec docs bash
```

---

## Проверка здоровья сервисов

```bash
docker compose ps
```

Вывод:

```
NAME             STATUS       PORTS
hackaton-docs-1  Up           0.0.0.0:5001->5001/tcp
hackaton-map-1   Exit 0
```

> **Примечание:** `map` завершает работу после выполнения команды — это ожидаемое поведение.

---

## Проверка API

```bash
# Docs-сервис
curl http://localhost:5001/doc/index

# API TOC
curl http://localhost:5001/api/toc | python -m json.tool
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

### Удалить всё

```bash
docker compose down -v --rmi all --remove-orphans
```

---

## Мониторинг ресурсов

```bash
docker stats
```

---

<< [Построение маршрута](/doc/how-to/build-routes) | [Настройка конфигурации](/doc/how-to/customize-config) >>
