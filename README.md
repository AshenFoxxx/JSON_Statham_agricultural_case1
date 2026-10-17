# АгроЛогистика

Система планирования поставок сельскохозяйственной продукции. Приложение хранит данные хозяйства, запасов, покупателей и автопарка, строит маршруты по дорогам и выбирает план отгрузок с максимальной прибылью: выручка минус стоимость топлива.

## Возможности

- Учёт культур на складе: запас в килограммах и предельное время доставки.
- Одно хозяйство с координатами и карта расположения.
- Покупатели, заказы и закупочные цены.
- Автопарк: грузоподъёмность, расход топлива, доступность машины.
- Расчёт плана поставок (OR-Tools CP-SAT): до трёх выездов на машину, несколько остановок, возврат на хозяйство; остаток стареет, пока машина в рейсе.
- Карта всех рейсов и сценарии пересчёта (недоступность машины, изменение цены спроса).

Контракт расчёта: [backend/README.md](backend/README.md). Описание модели: [backend/SOLVER.md](backend/SOLVER.md).

## Архитектура

| Компонент | Назначение |
| --- | --- |
| `frontend` | Веб-интерфейс (React, Vite), порт 3000 |
| `backend` | REST API и решатель (FastAPI), порт 8000 |

Клиент не считает оптимум и расстояния. Он отправляет текущие данные на `POST /api/v1/plan`. Километры и время в пути запрашиваются у публичного OSRM, поэтому для расчёта нужен доступ в интернет.

## Требования

- Python 3.11 или 3.12
- Node.js 18 или новее
- доступ в интернет для расчёта маршрутов

Запуск в контейнерах: Docker Engine и Docker Compose.

## Локальный запуск

Необходимы два процесса: API и интерфейс.

### Сервер API

Windows (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

macOS и Linux:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Проверка работоспособности: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health). Схема API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Интерфейс

Windows:

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

macOS и Linux:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Приложение: [http://localhost:3000](http://localhost:3000).

Файл `frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_SOLVER_URL=http://127.0.0.1:8000
```

При отсутствии переменных клиент обращается к `http://127.0.0.1:8000`.

## Docker

```bash
docker compose up --build
```

Фоновый режим: `docker compose up --build -d`. Остановка: `docker compose down`. Удаление тома с базой: `docker compose down -v`.

| Сервис | Адрес |
| --- | --- |
| Интерфейс | [http://localhost:3000](http://localhost:3000) |
| API | [http://localhost:8000](http://localhost:8000) |

Запросы `/api` и `/docs` также проксируются через интерфейс на порту 3000. Данные SQLite хранятся в томе `agro-data`.

## База данных

По умолчанию: `sqlite:///./agro.db` относительно рабочего каталога процесса uvicorn (обычно `backend/agro.db`).

При первом запуске создаются таблицы. Если хозяйство отсутствует, загружаются демонстрационные данные: 4 культуры, 3 машины и 8 покупателей вокруг Обнинска.

Повторный запуск сервера файл не перезаписывает. Чтобы вернуться к демонстрационному набору, остановите API и удалите `backend/agro.db`.

По умолчанию драйвер PostgreSQL не устанавливается. Если нужен Postgres, задайте `DATABASE_URL` и дополнительно выполните `pip install psycopg2-binary`.

## Работа с планом

Данные склада, хозяйства, покупателей и машин сохраняются через REST API. Страница «Маршруты» собирает их в запрос `POST /api/v1/plan` и отображает рейсы, отгрузки, выручку, транспортные затраты и прибыль.

Пересчёт выполняется тем же методом после изменения входных данных. Если OSRM недоступен, API возвращает код 502.

## HTTP API

Базовый адрес: `http://127.0.0.1:8000`.

| Метод | Путь | Описание |
| --- | --- | --- |
| GET | `/health` | Проверка доступности |
| GET, POST, PUT | `/api/v1/farm` | Хозяйство |
| GET, POST, PUT, DELETE | `/api/v1/products` | Культуры |
| GET, POST, PUT, DELETE | `/api/v1/buyers` | Покупатели |
| GET, POST, PUT, DELETE | `/api/v1/orders` | Заказы |
| GET, POST, PUT, DELETE | `/api/v1/vehicles` | Транспорт |
| POST | `/api/v1/plan` | Расчёт плана поставок |
| GET | `/docs` | Интерактивная схема API |

## Стек

- сервер: Python, FastAPI, SQLAlchemy, SQLite, OR-Tools CP-SAT
- маршрутизация: OSRM
- клиент: React 19, TypeScript, Vite 6, Tailwind CSS, OpenLayers
