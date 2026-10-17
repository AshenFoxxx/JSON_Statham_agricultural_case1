#!/usr/bin/env python3
"""
AgroLogistics — запуск всего проекта одной командой.

Запускает:
  1. Backend (FastAPI) — порт 8000
  2. Frontend (Vite) — порт 3000
  3. Документация (Flask) — порт 5001

Использование:
  python start.py
"""

import os
import signal
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Конфигурация
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
DOCS_DIR = BASE_DIR / "docs"

SERVICES = [
    {
        "name": "Backend",
        "dir": BACKEND_DIR,
        "cmd": ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        "port": 8000,
    },
    {
        "name": "Frontend",
        "dir": FRONTEND_DIR,
        "cmd": ["npm", "run", "dev"],
        "port": 3000,
    },
    {
        "name": "Документация",
        "dir": DOCS_DIR,
        "cmd": ["python", "server.py", "--port", "5001", "--host", "127.0.0.1"],
        "port": 5001,
    },
]


def check_python():
    """Проверка Python 3.11+."""
    try:
        import sysconfig
        version = sysconfig.get_config_var("VERSION")
        if not version:
            version = f"{sys.version_info.major}.{sys.version_info.minor}"
        major, minor = map(int, version.split("."))
        if major < 3 or (major == 3 and minor < 11):
            print("❌ Нужен Python 3.11+")
            return False
    except Exception:
        pass
    return True


def check_node():
    """Проверка Node.js 18+."""
    try:
        result = subprocess.run(
            ["node", "-v"], capture_output=True, text=True, timeout=5
        )
        version = result.stdout.strip().lstrip("v")
        major, minor = map(int, version.split("."))
        if major < 18:
            print("❌ Нужен Node.js 18+")
            return False
    except FileNotFoundError:
        print("❌ Node.js не найден. Установите Node.js 18+")
        return False
    except Exception:
        pass
    return True


def check_dependencies():
    """Проверка и установка зависимостей."""
    print("\n📦 Проверка зависимостей...")

    # Backend
    req_file = BACKEND_DIR / "requirements.txt"
    if req_file.exists():
        print("  Backend: pip install...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            cwd=str(BACKEND_DIR),
        )

    # Frontend
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("  Frontend: npm install...")
        subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR))

    # Docs
    docs_req = DOCS_DIR / "requirements.txt"
    if docs_req.exists():
        print("  Docs: pip install...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(docs_req)],
            cwd=str(DOCS_DIR),
        )


def start_service(service):
    """Запуск одного сервиса."""
    print(f"\n🚀 Запуск {service['name']}...")
    print(f"   Порт: {service['port']}")

    process = subprocess.Popen(
        service["cmd"],
        cwd=str(service["dir"]),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return process


def main():
    """Главная функция."""
    print("=" * 60)
    print("  🌾 АгроЛогистика — запуск проекта")
    print("=" * 60)

    # Проверки
    if not check_python():
        sys.exit(1)
    if not check_node():
        sys.exit(1)

    # Зависимости
    check_dependencies()

    # Запуск сервисов
    print("\n" + "=" * 60)
    print("  Запуск сервисов...")
    print("=" * 60)

    processes = []
    for service in SERVICES:
        process = start_service(service)
        processes.append((service["name"], process))

    # Информация
    print("\n" + "=" * 60)
    print("  ✅ Все сервисы запущены!")
    print("=" * 60)
    print()
    for name, _ in processes:
        if name == "Backend":
            print(f"  📡 Backend:    http://127.0.0.1:8000")
            print(f"  📚 API Docs:   http://127.0.0.1:8000/docs")
            print(f"  🗺️  Карта:      http://127.0.0.1:8000/map/")
        elif name == "Frontend":
            print(f"  🖥️  Frontend:   http://localhost:3000")
        elif name == "Документация":
            print(f"  📖 Docs:       http://127.0.0.1:5001")
    print()
    print("  Нажмите Ctrl+C для остановки всех сервисов")
    print("=" * 60 + "\n")

    # Ожидание и обработка остановки
    try:
        for _, process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Остановка всех сервисов...")
        for name, process in processes:
            print(f"  Остановка {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ Все сервисы остановлены.")


if __name__ == "__main__":
    main()
