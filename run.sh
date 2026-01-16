#!/bin/bash

# Docker Manager Pro Launcher
# Автоматически находит Docker сокет и запускает сервер

echo "🔍 Поиск Docker сокета..."

# Попробовать различные пути
DOCKER_SOCKETS=(
    "/var/run/docker.sock"
    "/run/docker.sock"
    "$HOME/.docker/run/docker.sock"
)

for socket in "${DOCKER_SOCKETS[@]}"; do
    if [ -S "$socket" ]; then
        echo "✅ Найден Docker сокет: $socket"
        export DOCKER_HOST="unix://$socket"
        break
    fi
done

# Если сокет не найден
if [ -z "$DOCKER_HOST" ]; then
    echo "⚠️  Docker сокет не найден по стандартным путям"
    echo ""
    echo "Попробуйте:"
    echo "  1. Перезагрузите WSL/bash"
    echo "  2. Выполните: sudo systemctl restart docker"
    echo "  3. Или установите переменную вручную:"
    echo "     export DOCKER_HOST=unix:///var/run/docker.sock"
    exit 1
fi

echo ""
echo "🐳 Docker Manager Pro v1.0.0"
echo "================================"
echo ""
echo "Docker подключен: $DOCKER_HOST"
echo ""

# Активировать venv если существует
if [ -d "venv" ]; then
    # НЕ вызывать activate.sh - просто добавить в PATH
    export PATH="$(pwd)/venv/bin:$PATH"
    echo "✅ Виртуальное окружение активировано"
fi

echo "🚀 Запуск сервера на http://localhost:5000"
echo ""

# ВАЖНО: Передать DOCKER_HOST в подпроцесс
python server.py

