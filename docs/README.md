# Documentation Microservice

## Установка

```bash
pip install flask pyyaml markdown
```

## Запуск

```bash
cd docs
python server.py
```

Откройте: http://localhost:5001

## Параметры

```bash
python server.py --port 8080 --host 0.0.0.0
```

## Структура

```
docs/
├── server.py              # Основной скрипт
├── toc.yaml               # Структура оглавления
├── content/               # Markdown файлы
├── templates/             # HTML шаблоны
├── static/
│   ├── css/style.css      # Стили
│   └── js/nav.js          # Навигация
```
