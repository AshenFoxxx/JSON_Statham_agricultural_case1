# АгроЛогистика — интерфейс

Веб-клиент склада, хозяйства, покупателей, автопарка и расчёта маршрутов. Данные читаются и пишутся через API на порту 8000. Оптимум и километры считает сервер.

Общий запуск: [корневой README](../README.md). Контракт `POST /api/v1/plan`: [backend/README.md](../backend/README.md).

## Стек

React 19, TypeScript, Vite 6, Tailwind CSS, React Router 7, OpenLayers.

## Запуск

```bash
cd frontend
cp .env.example .env   # Windows: copy .env.example .env
npm install
npm run dev
```

Адрес: [http://localhost:3000](http://localhost:3000).

`frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_SOLVER_URL=http://127.0.0.1:8000
```

Сборка: `npm run build` (каталог `dist/`). Просмотр сборки: `npm run preview`.

Контейнеры всего продукта: из корня репозитория `docker compose up --build`.

## Структура

```
frontend/src/
├── api/client.ts          REST и расчёт плана
├── components/            макет, таблица, модальные окна, карты
├── contexts/ThemeContext.tsx
├── pages/                 склад, хозяйство, покупатели, машины, маршруты
├── App.tsx
└── main.tsx
```

## Данные

Координаты — `longitude` и `latitude`. Время в пути и фиксированная цена рейса клиент не хранит: их возвращает `POST /api/v1/plan`.

| Сущность | Основные поля |
| --- | --- |
| Культура | `id`, `name`, `stock_kg`, `max_delivery_hours` (предел часов в пути) |
| Хозяйство | `name`, `longitude`, `latitude` |
| Покупатель | `id`, `name`, `longitude`, `latitude` |
| Заказ | `product_id`, `buyer_id`, `demand_kg`, `price_per_kg` |
| Машина | `id`, `name`, `capacity_kg`, `fuel_consumption_l_per_100km`, `fuel_price_rub_per_liter`, `max_stops`, `available` |

`max_trips` на стороне API всегда равен 1.
