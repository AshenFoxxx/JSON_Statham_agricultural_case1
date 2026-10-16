# 📚 Route Planner — Documentation

Документация проекта **Route Planner** — планировщика маршрутов для грузовиков.

## Структура

```
docs/
├── server.py              # Flask-сервер документации
├── toc.yaml               # Структура оглавления
├── content/               # Markdown-файлы
│   ├── tutorials/         # Обучение (Tutorials)
│   ├── how-to/            # Практические руководства (How-To)
│   ├── reference/         # Справочник (Reference)
│   └── explanation/       # Объяснения (Explanation)
├── templates/             # HTML-шаблоны (Jinja2)
│   ├── docs.html
│   └── 404.html
├── static/
│   ├── css/style.css      # Стили
│   └── js/nav.js          # Навигация
├── Dockerfile             # Образ для Docker
├── requirements.txt       # Python-зависимости
└── .dockerignore
```

## Формат документации

Документация построена по фреймворку **[Diataxis](https://diataxis.fr/)**:

| Раздел | Тип | Для кого |
|--------|-----|----------|
| **Tutorials** | Обучение | Новички — пошаговые уроки |
| **How-To** | Практические руководства | Те, кто хочет решить конкретную задачу |
| **Reference** | Справочник | Те, кто ищет точные данные (API, конфиги) |
| **Explanation** | Объяснения | Те, кто хочет понять "почему" и "как работает" |

## Запуск

### Docker (рекомендуется)

```bash
docker build -t docs .
docker run -p 5001:5001 docs
```

### Без Docker

```bash
pip install -r requirements.txt
python server.py
```

Откройте: **http://localhost:5001**

## Параметры запуска

```bash
python server.py --port 8080 --host 0.0.0.0
```

| Параметр | По умолчанию | Описание |
|----------|:------------:|----------|
| `--port` | `5001` | Порт сервера |
| `--host` | `127.0.0.1` | Адрес привязки |

## API

| Endpoint | Описание |
|----------|----------|
| `GET /` | Редирект на первую страницу |
| `GET /doc/<page>` | Рендер markdown-страницы |
| `GET /api/toc` | Структура TOC в JSON |

## Добавление страниц

1. Создайте `.md` файл в соответствующей папке `content/`
2. Добавьте запись в `toc.yaml`
3. Перезапустите сервер

## Формат toc.yaml

```yaml
- title: Название раздела
  file: path/to/page.md
  children:
    - title: Подраздел
      file: path/to/subpage.md
```

## Навигация

На каждой странице внизу есть ссылки на предыдущую и следующую страницы:

```markdown
<< [Предыдущая](/doc/page-prev) | [Следующая](/doc/page-next) >>
```

## Зависимости

| Пакет | Назначение |
|-------|-----------|
| `flask` | Web-фреймворк |
| `pyyaml` | Парсинг toc.yaml |
| `markdown` | Markdown → HTML |
