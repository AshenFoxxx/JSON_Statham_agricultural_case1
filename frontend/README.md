# АгроЛогистика — Frontend

Современный веб-интерфейс для управления сельскохозяйственной логистикой. Управление продукцией на складе, покупателями и транспортными средствами.

## Стек

- **React 19** + **TypeScript**
- **Vite 6** — сборщик
- **Tailwind CSS 3** — стилизация
- **React Router 7** — навигация
- **Docker** — деплой

## Структура

```
frontend/
├── src/
│   ├── components/       # Переиспользуемые компоненты
│   │   ├── Layout.tsx    # Макет с навигацией и хедером
│   │   ├── DataTable.tsx # Универсальная таблица
│   │   └── Modal.tsx     # Модальное окно
│   ├── contexts/         # React Context (тема)
│   │   └── ThemeContext.tsx
│   ├── data/             # Моковые данные
│   │   └── mockData.ts
│   ├── pages/            # Страницы приложения
│   │   ├── Warehouse.tsx   # Склад — продукция (культуры, запас кг, срок годности)
│   │   ├── Buyers.tsx      # Покупатели — заказы, спрос, цена
│   │   └── Vehicles.tsx    # Машины — грузоподъёмность, стоимость, расход топлива
│   ├── types/            # TypeScript типы
│   │   └── index.ts
│   ├── App.tsx           # Роутинг
│   ├── main.tsx          # Точка входа
│   └── index.css         # Tailwind стили
├── Dockerfile
├── nginx.conf
├── package.json
└── vite.config.ts
```

## Сущности

### Продукция (Склад)
| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название культуры (Клубника, Томаты, Огурцы) |
| `stock_kg` | number | Запас на складе, кг |
| `max_delivery_hours` | number | Максимальное время доставки, ч (срок годности) |

### Покупатели
| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название (Рынок Обнинск, Рестораны Москва) |
| `coordinates` | `{lat, lng}` | Координаты |
| `travel_time_hours` | number | Время в пути от склада, ч |
| `orders[]` | BuyerOrder[] | Список заказов |
| `orders[].product_id` | string | ID культуры |
| `orders[].demand_kg` | number | Спрос, кг |
| `orders[].price_per_kg` | number | Цена, ₽/кг |

### Машины (Водители/Транспорт)
| Поле | Тип | Описание |
|------|-----|----------|
| `id` | string | Уникальный идентификатор |
| `name` | string | Название (Газель А, Рефрижератор) |
| `capacity_kg` | number | Грузоподъёмность одного рейса, кг |
| `cost_per_trip` | number | Стоимость одного рейса, ₽ |
| `max_trips` | number | Максимальное количество рейсов |
| `fuel_consumption_l_per_100km` | number | Средний расход топлива, л/100км |
| `available` | boolean | Доступна для заказов |

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

### Сборка

```bash
npm run build
```

Результат в `dist/`

### Превью продакшена

```bash
npm run preview
```

## Docker

### Сборка образа

```bash
docker build -t agro-logistics-frontend .
```

### Запуск

```bash
docker run -p 80:80 agro-logistics-frontend
```

### Docker Compose (с бэкендом)

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
```

## API (Бэкенд)

Фронтенд работает с бэкендом по `POST /api/v1/plan`:

```json
{
  "products": [
    { "id": "strawberry", "name": "Клубника", "stock_kg": 600, "max_delivery_hours": 6 }
  ],
  "buyers": [
    {
      "id": "buyer-obninsk",
      "name": "Рынок Обнинск",
      "travel_time_hours": 1,
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
      "cost_per_trip": 6000,
      "max_trips": 2,
      "fuel_consumption_l_per_100km": 10,
      "available": true
    }
  ]
}
```

## Функции

- ✅ CRUD для продукции, покупателей, машин
- ✅ Тёмная / светлая тема (сохраняется в localStorage)
- ✅ Адаптивный дизайн
- ✅ Готовность к подключению бэкенд-API
- ✅ Docker-деплой

## Лицензия

MIT
