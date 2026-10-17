# Обучение: Первые шаги

---

## Что вы узнаете

В этом руководстве вы:

1. Клонируете репозиторий
2. Запустите PostgreSQL через Docker
3. Запустите бэкенд (FastAPI) и фронтенд (React)
4. Создадите данные через API
5. Откроете веб-интерфейс в браузере

---

## Что вам понадобится

- Docker Desktop — [скачать](https://www.docker.com/products/docker-desktop/);
- Git — [скачать](https://git-scm.com/);
- Node.js 18+ — [скачать](https://nodejs.org/);
- Любой браузер.

---

## Шаг 1. Клонирование репозитория

Откройте терминал и выполните:

```bash
git clone https://github.com/AshenFoxxx/JSON_Statham_agricultural_case1.git
cd Hackaton
```

---

## Шаг 2. Запуск базы данных

PostgreSQL запускается через Docker Compose:

```bash
docker compose up -d db
```

База данных будет доступна на порту `5432`.

Дождитесь сообщения:

```
Container hackaton-db-1  Started
```

Проверьте, что база работает:

```bash
docker compose ps
```

Ожидаемый вывод:

```
NAME             STATUS       PORTS
hackaton-db-1      Up           0.0.0.0:5432->5432/tcp
```

---

## Шаг 3. Запуск бэкенда

Backend — это FastAPI-сервер с CRUD API и solverом для маршрутизации.

```bash
docker compose up -d backend
```

Бэкенд запустится на `http://localhost:8000`.

Проверьте доступность:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status": "ok"}
```

Интерактивная API-документация доступна по адресу:
`http://localhost:8000/docs`

---

## Шаг 4. Запуск фронтенда

Frontend — это React-приложение с TypeScript и Tailwind CSS.

```bash
cd frontend
npm install
npm run dev
```

Frontend запустится на `http://localhost:3000`.

---

## Шаг 5. Создание данных

Откройте `http://localhost:8000/docs` — здесь доступна интерактивная документация API.

Или используйте `curl`:

### Создать хозяйство

```bash
curl -X POST http://localhost:8000/api/v1/farm \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ООО АгроТех",
    "longitude": 54.9815,
    "latitude": 36.2523
  }'
```

### Добавить продукцию

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "id": "strawberry",
    "name": "Клубника",
    "stock_kg": 600,
    "max_delivery_hours": 6
  }'
```

### Добавить покупателя

```bash
curl -X POST http://localhost:8000/api/v1/buyers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "buyer-obninsk",
    "name": "Рынок Обнинск",
    "longitude": 54.5126,
    "latitude": 36.5927
  }'
```

### Добавить транспорт

```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "id": "vehicle-a",
    "name": "Газель А",
    "capacity_kg": 800,
    "fuel_consumption_l_per_100km": 10,
    "fuel_price_rub_per_liter": 62,
    "max_trips": 2,
    "max_stops": 3,
    "available": true
  }'
```

---

## Шаг 6. Открытие веб-интерфейса

Откройте `http://localhost:3000` — вы увидите интерфейс АгроЛогистики:

- Склад — управление продукцией;
- Хозяйство — информация о ферме;
- Покупатели — база покупателей и заказы;
- Машины — управление автопарком;
- Маршруты — планирование и расчет оптимальных маршрутов.

---

## Шаг 7. Расчет маршрутов

На странице «Маршруты» нажмите кнопку «Рассчитать оптимальные маршруты».

Это отправит данные на бэкенд для расчета оптимальных маршрутов доставки.

---

## Что дальше

- Попробуйте добавить больше продукции, покупателей и машин;
- Создайте заказы для покупателей;
- Изучите API документацию;
- Ознакомьтесь с архитектурой системы.

---

<< [Обучение: Первые шаги](/doc/tutorials/01-getting-started) | [Запуск через Docker](/doc/tutorials/02-docker-quickstart) >>
