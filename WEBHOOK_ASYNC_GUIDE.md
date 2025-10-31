# Telegram Webhook Async/Await Guide

## Краткая справка для разработчиков

### Правильная работа с python-telegram-bot v21+ в webhook режиме

#### ✅ DO (Делать так)

```python
# 1. Инициализация для webhook режима
async def init_webhook():
    await application.initialize()  # ✅ Только инициализация
    await application.bot.set_webhook(url)

asyncio.run(init_webhook())

# 2. Обработка updates в webhook handler
def process_update_async():
    asyncio.run(application.process_update(update))  # ✅ Правильное управление loop

# 3. Async handlers в боте
async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет")  # ✅ Всегда await
    await context.bot.send_message(chat_id, text)  # ✅ Всегда await

# 4. Error handling с полным логированием
logger.error(f"Error: {e}", exc_info=True)  # ✅ Полный stack trace

# 5. Graceful shutdown
async def shutdown():
    await application.shutdown()

atexit.register(lambda: asyncio.run(shutdown()))
```

#### ❌ DON'T (Не делать так)

```python
# 1. НЕ вызывать start() в webhook режиме
async def init_webhook():
    await application.initialize()
    await application.start()  # ❌ Это для polling, не для webhook!

# 2. НЕ управлять loop вручную без ожидания pending tasks
loop = asyncio.new_event_loop()
loop.run_until_complete(coro())
loop.close()  # ❌ Pending tasks не завершены!

# 3. НЕ забывать await
update.message.reply_text("Hi")  # ❌ Не работает! Нужен await

# 4. НЕ использовать bot без context manager
bot = Bot(token)
bot.send_message(chat_id, text)  # ❌ Нет event loop!
```

## Частые ошибки и решения

### Error: "Event loop is closed"

**Причина:** Loop закрыт до завершения всех асинхронных операций

**Решение:**
```python
# Вместо:
loop.run_until_complete(task())
loop.close()

# Используйте:
asyncio.run(task())  # Автоматически ждёт все pending tasks

# Или явно:
loop.run_until_complete(task())
pending = asyncio.all_tasks(loop)
if pending:
    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
loop.close()
```

### Error: "no running event loop"

**Причина:** Попытка выполнить async операцию вне event loop

**Решение:**
```python
# В sync контексте (Flask route):
def webhook():
    def process():
        asyncio.run(async_task())  # ✅ Создаёт loop
    Thread(target=process).start()

# В async контексте (bot handler):
async def handler(update, context):
    await async_task()  # ✅ Уже в loop
```

### Webhook возвращает 200, но сообщения не отправляются

**Причина:** Обработка в background thread завершается слишком рано

**Решение:**
```python
# Убедитесь что asyncio.run() ждёт все tasks
asyncio.run(application.process_update(update))  # ✅

# Не используйте daemon threads для critical operations
thread = Thread(target=process)
thread.daemon = True  # OK для webhook, т.к. быстро отвечаем
thread.start()
```

## Архитектура webhook обработки

```
Telegram → Flask /webhook endpoint
           ↓
           Сразу вернуть 200 OK (< 100ms)
           ↓
           Запустить background Thread
           ↓
           asyncio.run(process_update())
           ↓
           Bot handlers выполняются
           ↓
           Все async операции (send_message и т.д.)
           ↓
           asyncio.run() ждёт завершения всех tasks
           ↓
           Loop закрывается
           ↓
           Thread завершается
```

## Debug советы

### 1. Включить подробное логирование

```python
logging.basicConfig(
    level=logging.DEBUG,  # Вместо INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. Логировать все этапы обработки

```python
logger.info(f"📨 Received update {update_id}")
logger.info(f"✅ Update {update_id} processed")
logger.error(f"❌ Error: {e}", exc_info=True)  # Полный traceback
```

### 3. Проверить pending tasks

```python
pending = asyncio.all_tasks(loop)
logger.debug(f"Pending tasks: {len(pending)}")
for task in pending:
    logger.debug(f"  - {task.get_name()}: {task}")
```

### 4. Мониторить потоки

```python
thread = Thread(
    target=process,
    name=f"TelegramUpdate-{update_id}"  # Уникальное имя
)
```

## Тестирование

### Unit тесты для async функций

```python
import asyncio
import unittest

class TestBot(unittest.TestCase):
    def test_async_handler(self):
        async def run_test():
            result = await my_async_function()
            self.assertEqual(result, expected)
        
        asyncio.run(run_test())
```

### Интеграционные тесты webhook

```python
import requests

# Симулировать webhook от Telegram
response = requests.post(
    'http://localhost:5000/webhook',
    json={
        'update_id': 123,
        'message': {...}
    }
)

assert response.status_code == 200
```

## Production checklist

- [ ] Application.initialize() вызван (БЕЗ start())
- [ ] Webhook URL установлен через set_webhook()
- [ ] asyncio.run() используется для обработки updates
- [ ] Все bot handlers используют async/await
- [ ] Error handler зарегистрирован
- [ ] Логирование настроено с exc_info=True
- [ ] Graceful shutdown настроен через atexit
- [ ] Timeout-ы настроены для HTTP requests (10-30 сек)
- [ ] Webhook возвращает 200 OK быстро (< 100ms)

## Полезные ссылки

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Telegram Bot API](https://core.telegram.org/bots/api)
