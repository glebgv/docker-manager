# Docker Manager Pro 🐳

**Профессиональное веб-приложение для управления Docker контейнерами**

## 🎯 Возможности

### 📊 Dashboard
- Real-time мониторинг контейнеров (Running/Stopped)
- Статистика по образам и томам
- Графики использования ресурсов (CPU, Memory)
- Диаграмма статуса контейнеров (Doughnut chart)
- Быстрые действия (Prune, Clean, Diagnostics, Backup)

### 📦 Containers Management
- Полный список всех контейнеров
- Просмотр деталей (ID, Image, Port, Status, Logs)
- Создание новых контейнеров (modal форма)
- Start/Stop/Delete операции
- Просмотр логов в real-time

### 🖼️ Images Management
- Список всех доступных образов
- Информация о размере и тегах
- Pull/Delete операции
- Просмотр истории загрузки

### 🌐 Networks & 💾 Volumes
- Управление сетями (bridge, host, custom)
- Просмотр подключенных контейнеров
- Управление томами (создание, удаление, инспект)
- Информация о размерах и монтировках

## 🚀 Быстрый старт

### Option 1: Прямое открытие в браузере
```bash
# Просто откройте файл в браузере
open index.html
# или
firefox index.html
# или
chrome index.html
```

### Option 2: Local Server (рекомендуется)
```bash
# Python 3
python -m http.server 8000

# Node.js
npx http-server

# PHP
php -S localhost:8000
```

Откройте браузер: `http://localhost:8000`

## 📋 Структура проекта

```
docker-manager-pro/
├── index.html              # Главное приложение (все-в-одном)
├── README.md              # Документация
├── INSTALL.md             # Инструкции установки
├── config.json            # Конфигурация (для backend)
├── docker-compose.yml     # Docker Compose для развертывания
├── server.js              # Backend (Node.js) - опционально
├── requirements.txt       # Python зависимости
└── docs/
    ├── API.md             # API документация
    ├── FEATURES.md        # Полный список функций
    └── ARCHITECTURE.md    # Архитектура приложения
```

## 🛠️ Установка Backend (опционально)

### Node.js Backend
```bash
npm install
npm start
# Server запустится на http://localhost:3000
```

### Python Backend
```bash
pip install -r requirements.txt
python server.py
# Server запустится на http://localhost:5000
```

## 📡 API Endpoints (при использовании backend)

```
GET  /api/containers          # Список контейнеров
GET  /api/containers/:id      # Деталь контейнера
POST /api/containers          # Создать контейнер
POST /api/containers/:id/start    # Запустить
POST /api/containers/:id/stop     # Остановить
DELETE /api/containers/:id    # Удалить

GET  /api/images              # Список образов
POST /api/images/:id/pull     # Скачать образ
DELETE /api/images/:id        # Удалить образ

GET  /api/networks            # Список сетей
GET  /api/volumes             # Список томов
```

## 🎨 Дизайн & Стиль

- **Темное оформление** (Dark Mode) с градиентами
- **Responsive дизайн** (мобильная оптимизация)
- **Smooth анимации** и переходы
- **Chart.js** для графиков ресурсов
- **Модальные окна** для управления

## ⚙️ Конфигурация

### `config.json`
```json
{
  "apiUrl": "http://localhost:3000/api",
  "refreshInterval": 5000,
  "maxContainers": 100,
  "theme": "dark"
}
```

## 🔐 Безопасность

- **Фронтенд**: CORS политика для API запросов
- **Backend**: Валидация всех входных данных
- **Docker**: Подключение через Unix socket (безопаснее)
- **Auth**: JWT токены (для production версии)

## 💡 Особенности реализации

### Фронтенд
- ✅ Zero external dependencies (кроме Chart.js)
- ✅ Чистый JavaScript (ES6+)
- ✅ Модульная архитектура
- ✅ Локальное хранилище данных (localStorage)
- ✅ Кросс-браузерная совместимость

### Backend (опционально)
- ✅ Express.js / Flask
- ✅ Docker SDK интеграция
- ✅ RESTful API
- ✅ Real-time обновления (WebSocket)

## 🐛 Трублшутинг

### Приложение не загружается
```bash
# Проверьте в консоли браузера (F12)
# Убедитесь, что браузер поддерживает ES6
# Используйте современный браузер (Chrome, Firefox, Safari, Edge)
```

### Backend не подключается
```bash
# Проверьте, что backend запущен
# Убедитесь, что CORS включен
# Проверьте URL в config.json
```

### Docker доступ запрещен
```bash
# Linux: добавьте пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# macOS/Windows: используйте Docker Desktop
```

## 📚 Документация

- **INSTALL.md** - Полная инструкция установки
- **API.md** - REST API справка
- **FEATURES.md** - Полный список функций
- **ARCHITECTURE.md** - Техническая архитектура

## 🤝 Контрибьюция

Проект открыт для улучшений!

Идеи:
- [ ] WebSocket для real-time обновлений
- [ ] Docker Swarm поддержка
- [ ] Kubernetes интеграция
- [ ] Аутентификация (OAuth, JWT)
- [ ] Docker Registry управление
- [ ] Контейнер логирование (ELK, Loki)
- [ ] Мониторинг (Prometheus, Grafana)

## 📄 Лицензия

MIT License - свободно используйте в своих проектах!

## 👨‍💻 Автор

Создано для DevOps инженеров и разработчиков.

---

**Версия**: 1.0.0  
**Последнее обновление**: 2025-01-15  
**Статус**: Production Ready 🚀
