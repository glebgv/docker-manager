# 📦 Инструкция Установки - Docker Manager Pro

## Требования

- **Браузер**: Chrome, Firefox, Safari, Edge (современная версия)
- **Docker**: v20.10+ (если используете backend)
- **Node.js**: v16+ (для backend)
- **Python**: 3.8+ (альтернатива backend)

## Быстрый Старт (Фронтенд только)

### Шаг 1: Получить файлы
```bash
# Скачайте index.html
# или клонируйте архив
```

### Шаг 2: Запустить локальный сервер
```bash
# Python 3 (рекомендуется)
python -m http.server 8000

# или Node.js
npx http-server

# или PHP
php -S localhost:8000
```

### Шаг 3: Открыть в браузере
```
http://localhost:8000
```

---

## Полная Установка (с Backend)

### Node.js Backend

#### 1. Установить зависимости
```bash
npm install
```

#### 2. Настроить окружение
```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

#### 3. Запустить сервер
```bash
npm start
# или для разработки
npm run dev
```

#### 4. Проверить подключение
```bash
curl http://localhost:3000/api/containers
```

### Python Backend

#### 1. Создать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

#### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

#### 3. Запустить сервер
```bash
python server.py
# или
flask run
```

#### 4. Проверить подключение
```bash
curl http://localhost:5000/api/containers
```

---

## Docker Deployment

### Docker контейнер

```bash
# Собрать образ
docker build -t docker-manager-pro .

# Запустить контейнер
docker run -d \
  -p 8000:80 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name docker-manager \
  docker-manager-pro
```

### Docker Compose

```bash
# Запустить с Docker Compose
docker-compose up -d

# Проверить логи
docker-compose logs -f

# Остановить
docker-compose down
```

---

## Конфигурация

### config.json
```json
{
  "apiUrl": "http://localhost:3000/api",
  "refreshInterval": 5000,
  "maxContainers": 100,
  "theme": "dark",
  "language": "en",
  "autoConnect": true
}
```

### Переменные окружения

```env
# Backend
PORT=3000
DOCKER_HOST=unix:///var/run/docker.sock
LOG_LEVEL=info

# Frontend
REACT_APP_API_URL=http://localhost:3000
REACT_APP_DEBUG=false
```

---

## Проверка установки

### Фронтенд
```bash
# Открыть браузер и проверить
# http://localhost:8000
# Должна загрузиться панель управления
```

### Backend (Node.js)
```bash
# Проверить статус API
curl http://localhost:3000/api/health

# Получить список контейнеров
curl http://localhost:3000/api/containers
```

### Backend (Python)
```bash
# Проверить статус API
curl http://localhost:5000/api/health

# Получить список контейнеров
curl http://localhost:5000/api/containers
```

### Docker
```bash
# Проверить подключение к Docker daemon
docker ps

# Проверить логи приложения
docker logs docker-manager
```

---

## Трублшутинг

### Port уже занят
```bash
# Использовать другой port
python -m http.server 8080
# или
PORT=3001 npm start
```

### CORS ошибки
```
Убедитесь, что backend запущен и доступен
Проверьте URL в config.json
Включите CORS в backend коде
```

### Docker доступ запрещен
```bash
# Linux
sudo usermod -aG docker $USER
newgrp docker

# Проверить
docker ps
```

### Приложение не загружается
```bash
# Откройте DevTools (F12)
# Проверьте консоль на ошибки
# Убедитесь, что JavaScript включен
# Очистите кеш браузера (Ctrl+Shift+Delete)
```

### WebSocket отключен
```bash
# Это нормально - приложение работает без WebSocket
# Для real-time обновлений включите WebSocket в backend
```

---

## Production развертывание

### Nginx
```nginx
server {
    listen 80;
    server_name docker-manager.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:3000/api;
    }
}
```

### SSL/TLS (Let's Encrypt)
```bash
certbot certonly --webroot -w /var/www/html -d docker-manager.example.com
# Настроить Nginx на использование сертификата
```

### Systemd Service
```ini
[Unit]
Description=Docker Manager Pro
After=network.target

[Service]
Type=simple
User=docker-manager
WorkingDirectory=/opt/docker-manager-pro
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Обновления

```bash
# Получить новую версию
git pull origin main

# Обновить зависимости
npm install
# или
pip install -r requirements.txt

# Перезапустить приложение
npm restart
# или
systemctl restart docker-manager
```

---

## Поддержка

Для вопросов и проблем:
- Проверьте документацию
- Откройте GitHub issue
- Свяжитесь с автором

---

**Happy Docker Management! 🚀**
