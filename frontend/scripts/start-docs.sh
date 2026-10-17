#!/bin/bash
# Запуск docs-сервера вместе с frontend
# Docs сервер запускается на порту 3001, Vite проксирует /docs/ к нему

cd "$(dirname "$0")/.."
FRONTEND_DIR="$(pwd)"
DOCS_DIR="$FRONTEND_DIR/../docs"

# Запуск docs-сервера в фоне
echo "📖 Запуск документации на порту 3001..."
python "$DOCS_DIR/server.py" --port 3001 --host 127.0.0.1 &
DOCS_PID=$!

# Очистка при остановке
cleanup() {
  echo "⏹️  Остановка docs-сервера..."
  kill $DOCS_PID 2>/dev/null
  exit
}
trap cleanup EXIT INT TERM

# Запуск frontend
echo "🖥️  Запуск frontend на порту 3000..."
npm run dev
