# Felix Hub - Quick Start Guide

Быстрая установка и запуск системы Felix Hub за 5 минут.

## Шаг 1: Получите Telegram Bot Token

1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота (например, "Felix Parts Bot")
   - Введите username (например, "felix_parts_bot")
4. Сохраните токен, который вам выдаст BotFather (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Шаг 2: Клонируйте и настройте

```bash
# Клонируйте репозиторий
git clone <repo-url>
cd FelixPartsBot

# Настройте Backend
cd felix_hub/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Создайте .env из примера
cp .env.example .env

# Отредактируйте .env - минимально нужно установить:
# BOT_TOKEN=<ваш_токен_от_BotFather>
nano .env  # или любой другой редактор

# Настройте Bot
cd ../bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создайте .env
cp .env.example .env

# Установите тот же BOT_TOKEN
nano .env
```

## Шаг 3: Запустите систему

Откройте 2 терминала:

### Терминал 1 - Backend
```bash
cd FelixPartsBot/felix_hub/backend
source venv/bin/activate
python app.py
```

Вы увидите:
```
* Running on http://0.0.0.0:5000
* Database initialized
```

### Терминал 2 - Bot
```bash
cd FelixPartsBot/felix_hub/bot
source venv/bin/activate
python bot.py
```

Вы увидите:
```
Bot started successfully
Listening for orders...
```

## Шаг 4: Тестирование

### 1. Проверьте админ-панель
Откройте в браузере: http://localhost:5000/admin

### 2. Протестируйте бота
1. Откройте Telegram
2. Найдите вашего бота по username
3. Отправьте `/start`
4. Создайте тестовый заказ

### 3. Проверьте интеграцию
1. В админ-панели найдите созданный заказ
2. Измените статус на "готов"
3. Проверьте, что пришло уведомление в Telegram

## ✅ Готово!

Система запущена и готова к использованию!

## Что дальше?

- **Настройка принтера:** См. [DEPLOYMENT.md](DEPLOYMENT.md#шаг-5-настройка-принтера-опционально)
- **Production развёртывание:** См. [DEPLOYMENT.md](DEPLOYMENT.md#шаг-7-production-развёртывание)
- **Решение проблем:** См. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Минимальная конфигурация .env

### backend/.env
```env
FLASK_SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///felix_hub.db
BOT_TOKEN=<ваш_токен_от_BotFather>
PRINTER_ENABLED=false
PRINTER_IP=192.168.0.50
PRINTER_PORT=9100
RECEIPT_WIDTH=32
```

### bot/.env
```env
BOT_TOKEN=<тот_же_токен_от_BotFather>
BACKEND_URL=http://localhost:5000
```

## Важные замечания

1. **BOT_TOKEN должен быть одинаковым** в backend/.env и bot/.env
2. **PRINTER_ENABLED=false** по умолчанию (система будет создавать PDF вместо печати)
3. **База данных создаётся автоматически** при первом запуске backend
4. **Логи пишутся** в `felix_hub/backend/felix_hub.log`

## Порты

- Backend API: **5000**
- Admin Panel: **5000/admin**

Убедитесь, что порт 5000 свободен.

## Частые вопросы

**Q: Бот не отвечает**  
A: Проверьте, что BOT_TOKEN правильный и backend запущен

**Q: Уведомления не приходят**  
A: Убедитесь, что механик написал боту `/start` хотя бы раз

**Q: Админ-панель не загружается**  
A: Проверьте, что backend запущен (curl http://localhost:5000/api/orders)

**Q: Принтер не печатает**  
A: Это нормально, если PRINTER_ENABLED=false. Система создаст PDF в /tmp

## Помощь

Если что-то не работает:
1. Проверьте логи: `tail -f felix_hub/backend/felix_hub.log`
2. См. подробное руководство: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Создайте issue в репозитории с описанием проблемы
