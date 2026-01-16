#!/bin/bash

echo "🔍 ДИАГНОСТИКА DOCKER ПОДКЛЮЧЕНИЯ"
echo "=================================="
echo ""

echo "1️⃣  Проверка Docker сокета:"
ls -la /var/run/docker.sock 2>/dev/null || echo "❌ Сокет не найден"
echo ""

echo "2️⃣  Текущий пользователь:"
whoami
echo ""

echo "3️⃣  Группы пользователя:"
groups
echo ""

echo "4️⃣  Проверка docker group:"
getent group docker
echo ""

echo "5️⃣  Может ли текущий пользователь читать сокет:"
if [ -w /var/run/docker.sock ]; then
    echo "✅ Есть права записи (write)"
elif [ -r /var/run/docker.sock ]; then
    echo "✅ Есть права чтения (read)"
else
    echo "❌ НЕТ ПРАВ доступа к сокету!"
    echo ""
    echo "🔧 РЕШЕНИЕ:"
    echo "  sudo chmod 666 /var/run/docker.sock"
    echo "  ИЛИ"
    echo "  sudo usermod -aG docker \$USER && newgrp docker"
fi
echo ""

echo "6️⃣  Проверка docker daemon:"
sudo systemctl status docker 2>/dev/null | grep Active || echo "Не удалось проверить статус"
echo ""

echo "7️⃣  Попытка подключения Docker CLI:"
docker ps -q 2>/dev/null && echo "✅ docker ps работает" || echo "❌ docker ps не работает"
echo ""

echo "8️⃣  Проверка Python Docker SDK:"
python3 -c "import docker; c = docker.from_env(); c.ping(); print('✅ Python Docker SDK работает')" 2>&1 || echo "❌ Python Docker SDK не работает"

