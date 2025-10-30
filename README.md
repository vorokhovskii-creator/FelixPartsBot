# Felix Hub System

Полнофункциональная автономная система управления заказами запчастей для СТО Felix.

## 📋 Описание

Felix Hub - это комплексное решение для автоматизации процесса заказа запчастей в автосервисе. Система состоит из Telegram-бота для механиков, веб-панели для администраторов, автоматической системы уведомлений и интеграции с термопринтером для печати чеков.

### Основные возможности

- **Telegram Bot** - удобный интерфейс для механиков
  - Создание заказов через интерактивное меню
  - Выбор категорий и запчастей
  - Прикрепление фото
  - Указание оригинал/аналог
  - Получение уведомлений о готовности

- **Admin Panel** - веб-интерфейс для администраторов
  - Просмотр всех заказов в реальном времени
  - Фильтрация по статусу и механику
  - Изменение статуса заказов
  - Статистика заказов
  - Экспорт в Excel

- **Notification System** - автоматические уведомления
  - Уведомление механика при готовности заказа
  - Уведомления об изменении статуса
  - Отправка через Telegram

- **Print System** - автоматическая печать чеков
  - Поддержка ESC/POS термопринтеров
  - Автоматическая печать при готовности заказа
  - Fallback на PDF если принтер недоступен
  - Ручная печать из админ-панели

## 🚀 Быстрый старт

### Требования
- Python 3.10 или выше
- Telegram Bot токен (получить через @BotFather)
- (Опционально) ESC/POS термопринтер в локальной сети

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repo-url>
cd FelixPartsBot
```

2. **Настройте Backend:**
```bash
cd felix_hub/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

3. **Настройте Bot:**
```bash
cd ../bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Добавьте BOT_TOKEN в .env
```

4. **Запустите систему:**

Терминал 1 (Backend):
```bash
cd felix_hub/backend
source venv/bin/activate
python app.py
```

Терминал 2 (Bot):
```bash
cd felix_hub/bot
source venv/bin/activate
python bot.py
```

5. **Откройте админ-панель:**
```
http://localhost:5000/admin
```

## 📚 Документация

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Полное руководство по развёртыванию системы
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Решение распространённых проблем

### Документация по модулям

**Backend:**
- [API Documentation](felix_hub/backend/API_DOCUMENTATION.md) - Описание REST API
- [Admin Panel Guide](felix_hub/backend/ADMIN_PANEL_GUIDE.md) - Руководство по админ-панели
- [Printer Setup](felix_hub/backend/PRINTER_README.md) - Настройка принтера
- [Notification System](felix_hub/backend/NOTIFICATION_SYSTEM.md) - Система уведомлений

**Bot:**
- [Bot Features](felix_hub/bot/FEATURES.md) - Возможности бота
- [Bot README](felix_hub/bot/README.md) - Документация бота

## 🏗️ Архитектура

```
┌─────────────────┐
│  Telegram Bot   │ <- Механики создают заказы
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │ <- REST API + База данных
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│   Admin Panel   │  │  Notifications  │
│   (Web UI)      │  │  + Printer      │
└─────────────────┘  └─────────────────┘
     ▲                      │
     │                      ▼
     └──────────────────────┘
        Админ меняет         Механик получает
        статус на "готов"    уведомление + чек
```

## 🔧 Технологический стек

**Backend:**
- Flask 3.0.0 - веб-фреймворк
- SQLAlchemy 3.1.1 - ORM
- SQLite / PostgreSQL - база данных
- python-telegram-bot - Telegram API
- python-escpos - печать на термопринтерах
- pandas, openpyxl - экспорт в Excel

**Frontend (Admin Panel):**
- Vanilla JavaScript
- Fetch API
- CSS Grid/Flexbox

**Bot:**
- python-telegram-bot 21.x - асинхронный Telegram bot framework
- requests - HTTP клиент для API

## 📦 Структура проекта

```
FelixPartsBot/
├── felix_hub/
│   ├── backend/                # Flask API и админ-панель
│   │   ├── utils/              # Утилиты (принтер, уведомления)
│   │   │   ├── notifier.py     # Отправка Telegram уведомлений
│   │   │   └── printer.py      # Печать чеков
│   │   ├── templates/          # HTML шаблоны
│   │   │   └── admin.html      # Админ-панель
│   │   ├── static/             # Статические файлы
│   │   │   ├── admin.js        # JavaScript админ-панели
│   │   │   └── style.css       # Стили
│   │   ├── app.py              # Главный файл Flask приложения
│   │   ├── models.py           # Модели базы данных
│   │   ├── requirements.txt    # Зависимости Python
│   │   └── .env.example        # Пример конфигурации
│   │
│   └── bot/                    # Telegram бот
│       ├── bot.py              # Главный файл бота
│       ├── config.py           # Конфигурация и константы
│       ├── requirements.txt    # Зависимости Python
│       └── .env.example        # Пример конфигурации
│
├── DEPLOYMENT.md               # Руководство по развёртыванию
├── TROUBLESHOOTING.md          # Решение проблем
├── README.md                   # Этот файл
└── .gitignore                  # Git ignore правила
```

## 🔄 Полный цикл работы

1. **Механик создаёт заказ через Telegram-бота:**
   - Выбирает категорию запчастей
   - Выбирает нужные запчасти
   - Вводит VIN автомобиля
   - Указывает оригинал/аналог
   - (Опционально) прикрепляет фото
   - Подтверждает заказ

2. **Заказ сохраняется в базе данных** со статусом "новый"

3. **Администратор видит заказ в админ-панели:**
   - Просматривает детали заказа
   - Проверяет информацию
   - Меняет статус на "в работе"

4. **Когда запчасти получены, админ меняет статус на "готов":**
   - Система автоматически печатает чек (или создаёт PDF)
   - Система отправляет Telegram уведомление механику
   - Флаг `printed` устанавливается в `true`

5. **Механик получает уведомление в Telegram:**
   - Видит, что заказ готов
   - Получает детали заказа
   - Идёт за запчастями

6. **После выдачи админ меняет статус на "выдан"**

## 🔐 Безопасность

- Все секретные данные хранятся в `.env` файлах (не коммитятся в Git)
- SQLite для разработки, PostgreSQL для production
- CORS настроен для безопасной работы
- Валидация всех входных данных
- Обработка ошибок без раскрытия внутренней информации

## 📊 API Endpoints

### Orders
- `POST /api/orders` - Создать заказ
- `GET /api/orders` - Получить список заказов (с фильтрами)
- `GET /api/orders/<id>` - Получить заказ по ID
- `PATCH /api/orders/<id>` - Обновить заказ
- `DELETE /api/orders/<id>` - Удалить заказ
- `POST /api/orders/<id>/print` - Напечатать чек

### Stats & Export
- `GET /api/orders/stats` - Статистика заказов
- `GET /export` - Экспорт в Excel (с фильтрами)

### Printer
- `POST /api/printer/test` - Тестовая печать

Подробнее: [API Documentation](felix_hub/backend/API_DOCUMENTATION.md)

## 🖨️ Поддерживаемые принтеры

Система поддерживает любые ESC/POS термопринтеры:
- Epson TM-T20, TM-T82, TM-T88
- Star Micronics TSP100, TSP650
- Citizen CT-S310, CT-S2000
- Bixolon SRP-350
- И другие ESC/POS совместимые принтеры

**Если принтера нет или он недоступен** - система автоматически создаст PDF файл в папке `/tmp`, который можно распечатать на любом принтере.

## 🧪 Тестирование

### Backend тесты
```bash
cd felix_hub/backend
pytest test_api.py              # Тесты API
pytest test_printer.py          # Тесты принтера
pytest test_notifier.py         # Тесты уведомлений
pytest test_comprehensive.py   # Комплексные тесты
```

### Bot тесты
```bash
cd felix_hub/bot
pytest test_bot.py
```

## 🌐 Production развёртывание

### Быстрый деплой на Railway.app

Railway.app предоставляет простой способ развернуть Felix Hub в production с PostgreSQL, автоматическим масштабированием и SSL.

#### Шаг 1: Подготовка
1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Получите токен Telegram-бота через @BotFather

#### Шаг 2: Создание проекта
1. В Railway Dashboard нажмите **New Project**
2. Выберите **Deploy from GitHub repo** → выберите FelixPartsBot
3. Нажмите **Add PostgreSQL** для добавления базы данных

#### Шаг 3: Настройка переменных окружения
В Railway Dashboard → Variables, добавьте:

```env
TELEGRAM_TOKEN=<ваш токен от @BotFather>
ADMIN_IDS=<ID администраторов через запятую>
SECRET_KEY=<случайная длинная строка>
FLASK_ENV=production
```

**Примечание:** `DATABASE_URL` создаётся автоматически при добавлении PostgreSQL.

#### Шаг 4: Деплой
Railway автоматически:
1. Установит зависимости из `requirements.txt`
2. Запустит `release` команду для инициализации БД
3. Запустит процессы `web` (Flask API) и `worker` (Telegram бот)

#### Шаг 5: Получить URL приложения
1. После успешного деплоя Railway предоставит публичный URL
2. Скопируйте URL (например: `https://felixpartsbot-production.up.railway.app`)
3. Добавьте переменную окружения `BACKEND_URL=<ваш URL>`

#### Готово! 🎉
Ваш бот работает в production окружении с PostgreSQL и автоматическими бэкапами.

### Другие варианты развёртывания

Для развёртывания на собственном сервере:

1. **Использовать PostgreSQL** вместо SQLite
2. **Настроить systemd** для автозапуска сервисов
3. **Использовать NGINX** как reverse proxy
4. **Настроить HTTPS** через Let's Encrypt
5. **Использовать gunicorn** вместо встроенного сервера Flask
6. **Настроить резервное копирование** базы данных

Подробные инструкции: [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔧 Настройка переменных окружения

### Backend (.env)
```env
FLASK_SECRET_KEY=<случайная строка>
DATABASE_URL=sqlite:///felix_hub.db
BOT_TOKEN=<токен от @BotFather>
PRINTER_ENABLED=false
PRINTER_IP=192.168.0.50
PRINTER_PORT=9100
RECEIPT_WIDTH=32
```

### Bot (.env)
```env
BOT_TOKEN=<тот же токен от @BotFather>
BACKEND_URL=http://localhost:5000
```

**Важно:** Используйте один и тот же `BOT_TOKEN` в обоих .env файлах!

## 📝 Логирование

Backend записывает все события в `felix_hub/backend/felix_hub.log`:
- Создание, обновление, удаление заказов
- Отправка уведомлений
- Печать чеков
- Ошибки и предупреждения

Просмотр логов в реальном времени:
```bash
tail -f felix_hub/backend/felix_hub.log
```

## 🐛 Решение проблем

Если что-то не работает, смотрите [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

Наиболее частые проблемы:
- **Бот не отвечает** - проверьте BOT_TOKEN и доступность backend
- **Уведомления не приходят** - убедитесь, что механик написал боту `/start`
- **Принтер не печатает** - проверьте IP адрес и доступность принтера
- **Заказы не отображаются** - откройте DevTools (F12) и проверьте консоль

## 🤝 Вклад в проект

Если вы хотите улучшить проект:
1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте ветку (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📄 Лицензия

Этот проект создан для СТО Felix. Все права защищены.

## 📞 Контакты

Если у вас есть вопросы или предложения, создайте issue в репозитории.

---

**Сделано с ❤️ для СТО Felix**
