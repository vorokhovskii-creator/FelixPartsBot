# Railway Deployment - Изменения и конфигурация

## ✅ Выполненные задачи

### 1. ✅ Миграция БД: SQLite → PostgreSQL

**felix_hub/backend/app.py:**
- Добавлена поддержка PostgreSQL с автоматической конвертацией URL
- Сохранён fallback на SQLite для локальной разработки
- Добавлена конфигурация SECRET_KEY из environment

**Изменения:**
```python
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
```

### 2. ✅ Создан Procfile

**Файл: `Procfile`**
```
release: python felix_hub/backend/init_db.py
web: gunicorn -w 2 -b 0.0.0.0:$PORT felix_hub.backend.app:app
worker: python -m felix_hub.bot.bot
```

Три процесса:
- `release` - инициализация БД при деплое
- `web` - Flask API через gunicorn
- `worker` - Telegram бот

### 3. ✅ Обновлён requirements.txt

**Файл: `requirements.txt`** (в корне)
Содержит все зависимости:
- Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 + Flask-CORS 4.0.0
- psycopg2-binary 2.9.9 (драйвер PostgreSQL)
- python-telegram-bot 21.0
- gunicorn 21.2.0 (production WSGI сервер)
- pandas, openpyxl (экспорт в Excel)
- python-escpos, reportlab (печать)
- python-dotenv 1.0.0

### 4. ✅ Environment Variables конфигурация

**Файл: `.env.example`** (в корне)
Создан шаблон с документацией всех переменных:
- `TELEGRAM_TOKEN` - токен Telegram бота
- `ADMIN_IDS` - ID администраторов через запятую
- `BACKEND_URL` - URL Railway приложения
- `SECRET_KEY` - секретный ключ для Flask
- `DATABASE_URL` - автоматически от Railway PostgreSQL
- `FLASK_ENV` - production/development
- `ALLOWED_ORIGINS` - CORS настройки

**felix_hub/bot/config.py:**
- Добавлена валидация `TELEGRAM_TOKEN`
- Добавлена поддержка `ADMIN_IDS` из environment
- Добавлена проверка обязательных переменных

### 5. ✅ Production настройки Flask

**felix_hub/backend/app.py:**
- Порт берётся из `$PORT` environment (Railway автоматически)
- Debug отключается в production (`FLASK_ENV=production`)
- CORS настраивается через `ALLOWED_ORIGINS`

```python
port = int(os.getenv('PORT', 5000))
debug = os.getenv('FLASK_ENV') != 'production'
app.run(host='0.0.0.0', port=port, debug=debug)
```

### 6. ✅ Инициализация БД

**Файл: `felix_hub/backend/init_db.py`**
Скрипт для первого запуска:
- Создаёт все таблицы
- Добавляет базовые категории
- Безопасен для повторного запуска
- Запускается автоматически через `release` команду в Procfile

### 7. ✅ README обновлён

**README.md:**
Добавлена новая секция "🚀 Быстрый деплой на Railway.app" с:
- Пошаговыми инструкциями
- Настройкой переменных окружения
- Объяснением автоматического процесса деплоя
- Информацией о получении URL приложения

### 8. ✅ Настройка CORS для production

**felix_hub/backend/app.py:**
```python
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, origins=ALLOWED_ORIGINS)
```

Позволяет настроить разрешённые origins через environment.

### 9. ✅ Health check endpoint

**felix_hub/backend/app.py:**
Добавлен endpoint `/health`:
```python
@app.route('/health')
def health_check():
    """Health check для Railway"""
    # Проверяет статус БД
    # Возвращает JSON с timestamp
```

Railway использует это для мониторинга состояния приложения.

### 10. ✅ .gitignore обновлён

Добавлено:
- `.env.local` - локальные environment переменные
- Уже были: `.env`, `*.db`, `*.sqlite`, `__pycache__/`, `venv/`

## 🔧 Технические детали

### Импорты модулей
Добавлены `sys.path` манипуляции для корректной работы:
- `felix_hub/backend/app.py` - добавляет backend директорию в path
- `felix_hub/bot/bot.py` - добавляет bot директорию в path
- Позволяет импортировать модули как при локальной разработке, так и через gunicorn

### Структура пакетов
Созданы `__init__.py` файлы:
- `felix_hub/__init__.py`
- `felix_hub/backend/__init__.py`
- `felix_hub/bot/__init__.py`

Это делает директории правильными Python пакетами.

### SQLAlchemy совместимость
Используется современный синтаксис для SQLAlchemy 1.4+:
```python
from sqlalchemy import text
with db.engine.connect() as conn:
    conn.execute(text('SELECT 1'))
```

## 🧪 Тестирование

**Файл: `test_railway_setup.py`**
Комплексный тест-скрипт проверяет:
- ✅ Наличие всех необходимых файлов
- ✅ Импорт всех модулей
- ✅ Конфигурацию базы данных
- ✅ Работу health endpoint
- ✅ Конвертацию PostgreSQL URL

Запуск: `python test_railway_setup.py`

## 📋 Критерии приёмки - ВЫПОЛНЕНО

- ✅ PostgreSQL поддержка добавлена (с fallback на SQLite локально)
- ✅ Procfile создан с web + worker + release процессами
- ✅ requirements.txt содержит все зависимости включая gunicorn и psycopg2
- ✅ Environment variables загружаются через python-dotenv
- ✅ .env.example создан с документацией
- ✅ init_db.py скрипт создан для инициализации
- ✅ README обновлён с инструкциями деплоя
- ✅ CORS настроен правильно
- ✅ Health check endpoint добавлен
- ✅ .gitignore обновлён
- ✅ Код работает локально с SQLite (для разработки)
- ✅ Код готов к деплою на Railway с PostgreSQL

## 🚀 Деплой на Railway - Инструкция

### Шаг 1: Подготовка
1. Создайте аккаунт на [Railway.app](https://railway.app)
2. Получите токен через @BotFather в Telegram

### Шаг 2: Создание проекта
1. Railway Dashboard → **New Project**
2. **Deploy from GitHub repo** → выберите FelixPartsBot
3. **Add PostgreSQL** для базы данных

### Шаг 3: Environment Variables
В Railway Dashboard → Variables добавьте:
```
TELEGRAM_TOKEN=<ваш токен>
ADMIN_IDS=<ID админов через запятую>
SECRET_KEY=<случайная длинная строка>
FLASK_ENV=production
```

### Шаг 4: Деплой
Railway автоматически:
1. ✅ Установит зависимости из requirements.txt
2. ✅ Запустит release команду (init_db.py)
3. ✅ Запустит web и worker процессы

### Шаг 5: Настройка URL
1. Скопируйте URL приложения от Railway
2. Добавьте переменную: `BACKEND_URL=<ваш URL>`

### Готово! 🎉

## 🔒 Безопасность

- ✅ .env файлы не коммитятся в Git
- ✅ Секретные ключи хранятся в environment
- ✅ PostgreSQL credentials автоматически от Railway
- ✅ CORS настраивается для конкретных origins
- ✅ Валидация входных данных сохранена

## 📝 Локальная разработка

Продолжает работать как раньше:

```bash
# Backend
cd felix_hub/backend
python app.py

# Bot
python -m felix_hub.bot.bot
```

Использует SQLite автоматически, если `DATABASE_URL` не задан.

## 🔄 Обратная совместимость

- ✅ Старые .env переменные работают (BOT_TOKEN → TELEGRAM_TOKEN)
- ✅ Локальная разработка не затронута
- ✅ Существующие скрипты продолжают работать
- ✅ Все тесты проходят успешно

---

**Статус:** ✅ Готово к деплою на Railway.app
