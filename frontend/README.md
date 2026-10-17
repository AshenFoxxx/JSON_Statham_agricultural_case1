# АгроЛогистика — Frontend

React-интерфейс для управления сельскохозяйственной логистикой: склад, хозяйство, покупатели, машины и маршруты.

## Стек

- **React 19** + **TypeScript**
- **Vite 6** — сборщик
- **Tailwind CSS 3** — стилизация
- **React Router 7** — навигация

## Структура

```
frontend/
├── src/
│   ├── api/              # API клиент
│   │   ├── client.ts     # REST запросы
│   │   └── solver.ts     # Solver API
│   ├── components/       # Переиспользуемые компоненты
│   │   ├── DataTable.tsx
│   │   ├── Layout.tsx
│   │   └── Modal.tsx
│   ├── contexts/         # React Context (тема)
│   │   └── ThemeContext.tsx
│   ├── pages/            # Страницы приложения
│   │   ├── Warehouse.tsx # Склад продукции
│   │   ├── FarmPage.tsx  # Управление хозяйством
│   │   ├── Buyers.tsx    # Покупатели и заказы
│   │   ├── Vehicles.tsx  # Транспорт
│   │   ├── Routes.tsx    # Маршруты доставки
│   │   └── Privacy.tsx   # Политика конфиденциальности
│   ├── types/            # TypeScript типы
│   └── main.tsx
├── scripts/
│   └── start-docs.sh     # Запуск docs-сервера
├── .env                  # Переменные окружения
├── package.json
└── vite.config.ts
```

## Установка

```bash
cd frontend
npm install
```

## Запуск

### Разработка

```bash
npm run dev
```

Откроется на http://localhost:3000

### С документацией

```bash
npm run dev:docs
```

Запускает фронт (порт 3000) + docs-сервер (порт 3001). Документация доступна по адресу `http://localhost:3000/doc/`.

### Сборка

```bash
npm run build
```

Результат в `dist/`

### Превью продакшена

```bash
npm run preview
```

## Переменные окружения

В `.env` должны быть:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_SOLVER_URL=http://127.0.0.1:8000
```

Без этого фронт пойдёт на порт 8001 и покажет пустой экран.

## API (Бэкенд)

Фронтенд работает с бэкендом по `POST /api/v1/plan`:

```json
{
  "farm": {
    "name": "Хозяйство Обнинск",
    "longitude": 36.6103,
    "latitude": 55.0969
  },
  "products": [
    { "id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6 }
  ],
  "buyers": [
    {
      "id": "buyer-obninsk",
      "name": "Рынок Обнинск",
      "longitude": 36.5927,
      "latitude": 54.5126,
      "orders": [
        { "product_id": "strawberry", "demand_kg": 200, "price_per_kg": 160 }
      ]
    }
  ],
  "vehicles": [
    {
      "id": "vehicle-a",
      "name": "Газель А",
      "capacity_kg": 800,
      "fuel_consumption_l_per_100km": 10,
      "fuel_price_rub_per_liter": 60,
      "max_trips": 1,
      "max_stops": 3,
      "available": true
    }
  ]
}
```

## Функции

- ✅ CRUD для продукции, покупателей, машин
- ✅ Тёмная / светлая тема (сохраняется в localStorage)
- ✅ Адаптивный дизайн
- ✅ Подключение к бэкенд-API
- ✅ Встроенная документация
