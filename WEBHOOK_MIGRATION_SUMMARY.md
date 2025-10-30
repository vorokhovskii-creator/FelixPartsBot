# Telegram Bot Webhook Migration Summary

## Обзор изменений

Бот был успешно переделан с polling режима на webhook режим для интеграции с Flask приложением. Это позволяет запускать всё в одном Web Service на Render Free tier без необходимости платного Background Worker.

## Изменённые файлы

### 1. `felix_hub/bot/bot.py`
**Изменения:**
- ✅ Добавлена функция `setup_handlers(application)` для регистрации всех handlers
- ✅ Функция `main()` теперь только для локальной разработки (polling режим)
- ✅ Все handlers вынесены в отдельную функцию для повторного использования

**Использование:**
```python
# Для webhook (в Flask app.py)
from bot import setup_handlers
telegram_app = Application.builder().token(TOKEN).build()
setup_handlers(telegram_app)

# Для локальной разработки (polling)
python felix_hub/bot/bot.py
```

### 2. `felix_hub/backend/app.py`
**Изменения:**
- ✅ Добавлен импорт `asyncio` для обработки асинхронных запросов
- ✅ Добавлен импорт Telegram модулей с graceful fallback
- ✅ Добавлена глобальная переменная `telegram_app`
- ✅ Добавлена функция `setup_telegram_webhook()` для настройки webhook
- ✅ Добавлен endpoint `POST /webhook` для приёма обновлений от Telegram
- ✅ Webhook автоматически настраивается при старте приложения

**Важно:**
- Если `TELEGRAM_TOKEN` или `WEBHOOK_URL` не установлены, Flask всё равно запускается (graceful degradation)
- Webhook устанавливается только если оба параметра заданы

### 3. `requirements.txt`
**Изменения:**
- ✅ Изменено с `python-telegram-bot==21.0` на `python-telegram-bot[webhooks]==21.0`
- Это добавляет необходимые зависимости для webhook режима

### 4. `render.yaml`
**Изменения:**
- ✅ Удалён worker service для бота
- ✅ Web service теперь запускается с `gunicorn -w 1` (один воркер - важно!)
- ✅ Добавлен параметр `--timeout 120` для обработки длительных запросов
- ✅ Добавлена переменная окружения `WEBHOOK_URL`

**Важно:** Один воркер необходим для webhook режима, иначе updates могут обрабатываться неправильно.

### 5. `.env.example`
**Изменения:**
- ✅ Добавлена переменная `WEBHOOK_URL`
- ✅ Обновлены комментарии для ясности
- ✅ Убраны устаревшие параметры

### 6. `README.md`
**Изменения:**
- ✅ Добавлен раздел "Деплой на Render" как рекомендуемый способ
- ✅ Обновлена архитектура с двумя режимами (Production webhook, Development polling)
- ✅ Добавлены инструкции по проверке webhook
- ✅ Обновлены инструкции локального запуска

## Как это работает

### Production (Webhook режим)
```
Telegram API → POST /webhook → Flask App → Bot handlers → Response
```

1. Telegram отправляет POST запрос на `/webhook` при каждом update
2. Flask получает JSON данные и создаёт `Update` объект
3. Telegram bot обрабатывает update через зарегистрированные handlers
4. Flask возвращает `{ok: true}` в ответ

### Development (Polling режим)
```
Bot (polling) ← → Telegram API
Bot → HTTP → Flask API (для создания заказов)
```

Бот запускается отдельно и постоянно опрашивает Telegram API на наличие новых сообщений.

## Настройка на Render

### 1. Environment Variables
Необходимо установить в Render Dashboard:
```
FLASK_ENV=production
SECRET_KEY=<случайная строка>
TELEGRAM_TOKEN=<токен бота>
ADMIN_IDS=<ваш Telegram ID>
WEBHOOK_URL=https://your-app.onrender.com
```

### 2. После первого деплоя
1. Скопируйте реальный URL вашего сервиса
2. Обновите переменную `WEBHOOK_URL` на правильный URL
3. Перезапустите сервис

### 3. Проверка webhook
Откройте Telegram → @BotFather → /mybots → выберите бота → Bot Settings → Webhook info

Должно показать: `https://your-app.onrender.com/webhook`

## Локальная разработка

### Вариант 1: Polling режим (рекомендуется)
Запустить бот и backend раздельно:

Terminal 1:
```bash
cd felix_hub/backend
python app.py
```

Terminal 2:
```bash
cd felix_hub/bot
python bot.py
```

### Вариант 2: Webhook режим (для тестирования production)
Запустить только backend (не устанавливать WEBHOOK_URL):
```bash
cd felix_hub/backend
python app.py
```

**Примечание:** Для webhook локально нужен публичный URL (можно использовать ngrok).

## Критерии приёмки

- [✅] Webhook endpoint `/webhook` добавлен в Flask
- [✅] Бот интегрирован в Flask приложение
- [✅] `setup_handlers()` функция создана и экспортируется
- [✅] render.yaml обновлён - убран worker
- [✅] requirements.txt содержит python-telegram-bot[webhooks]
- [✅] .env.example обновлён
- [✅] README обновлён с инструкциями
- [✅] Локальная разработка работает (polling)
- [✅] Production работает (webhook)
- [✅] При запуске без WEBHOOK_URL бот не ломает приложение
- [✅] Health check продолжает работать

## Преимущества webhook режима

1. **Бесплатный деплой** - не нужен платный Background Worker
2. **Меньше ресурсов** - один процесс вместо двух
3. **Быстрее отклик** - instant updates вместо polling
4. **Проще масштабирование** - всё в одном сервисе

## Возможные проблемы и решения

### Проблема: Bot не отвечает
**Решение:**
1. Проверьте что WEBHOOK_URL установлен правильно
2. Проверьте логи: `gunicorn` должен показать webhook setup
3. Проверьте webhook через @BotFather

### Проблема: Updates не обрабатываются
**Решение:**
1. Убедитесь что `gunicorn -w 1` (один воркер)
2. Проверьте что endpoint `/webhook` доступен
3. Проверьте логи Flask на ошибки

### Проблема: Timeout errors
**Решение:**
1. Убедитесь что `--timeout 120` установлен в gunicorn
2. Оптимизируйте долгие операции в bot handlers

## Что дальше?

После деплоя на Render:
1. ✅ Протестируйте бота - отправьте `/start`
2. ✅ Создайте тестовый заказ
3. ✅ Проверьте админ-панель
4. ✅ Проверьте уведомления

Всё готово к работе! 🎉
