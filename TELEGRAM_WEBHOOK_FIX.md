# Telegram Webhook Event Loop Fix

## Проблема
При работе через webhook возникала ошибка:
```
telegram.error.NetworkError: Unknown error in HTTP implementation: RuntimeError('Event loop is closed')
```

Ошибка происходила при попытке отправки сообщений Telegram ботом через webhook.

## Причины

1. **Неправильная инициализация**: Application вызывал `start()` который предназначен для polling режима, а не для webhook
2. **Неправильное управление event loop**: Event loop создавался и закрывался сразу, не давая завершиться всем асинхронным задачам
3. **Отсутствие обработки pending tasks**: При закрытии loop не ожидалось завершение всех отправленных задач

## Исправления

### 1. Инициализация Telegram Application (`app.py:740-794`)

**Было:**
```python
async def init_and_set_webhook():
    await telegram_app.initialize()
    await telegram_app.start()  # ❌ Неправильно для webhook режима
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
```

**Стало:**
```python
async def init_and_set_webhook():
    await telegram_app.initialize()  # ✅ Только инициализация для webhook
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
```

**Объяснение:** Метод `start()` запускает polling механизм и предназначен только для polling режима. В webhook режиме нужна только инициализация.

### 2. Webhook Handler - Обработка Updates (`app.py:797-865`)

**Было:**
```python
def process_update_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telegram_app.process_update(update))
    loop.close()  # ❌ Закрывается сразу, не дожидаясь pending tasks
```

**Стало:**
```python
def process_update_async():
    """Обработать update с правильным управлением event loop"""
    try:
        # ✅ asyncio.run() правильно управляет жизненным циклом loop
        asyncio.run(telegram_app.process_update(update))
        logger.info(f"✅ Update processed successfully")
        
    except RuntimeError as e:
        if 'Event loop is closed' in str(e):
            # Fallback с явным управлением loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(telegram_app.process_update(update))
            finally:
                # ✅ Дать время завершить все pending tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
```

**Объяснение:**
- `asyncio.run()` автоматически создаёт event loop, выполняет корутину, ждёт все pending tasks и корректно закрывает loop
- Fallback обработчик на случай RuntimeError явно ждёт завершения всех задач перед закрытием loop
- Добавлено подробное логирование с `exc_info=True` для отладки

### 3. Graceful Shutdown (`app.py:868-879`)

**Добавлено:**
```python
def cleanup_telegram_app():
    """Gracefully shutdown telegram application"""
    global telegram_app
    if telegram_app:
        try:
            async def shutdown():
                await telegram_app.shutdown()
            asyncio.run(shutdown())
            logger.info("✅ Telegram application shut down successfully")
        except Exception as e:
            logger.error(f"❌ Error shutting down telegram app: {e}", exc_info=True)

atexit.register(cleanup_telegram_app)
```

**Объяснение:** Правильное завершение работы приложения при остановке сервера, закрытие всех соединений.

### 4. Улучшенный Error Handler (`bot.py:664-679`)

**Было:**
```python
logger.error(f"❌ Error: {context.error}")
traceback.print_exc()
```

**Стало:**
```python
logger.error(f"❌ Error: {context.error}", exc_info=context.error)

# Дополнительная информация для отладки
if update:
    logger.error(f"Update data: {update.to_dict() if hasattr(update, 'to_dict') else str(update)}")
```

**Объяснение:** Более подробное логирование с полным stack trace и информацией об update для упрощения отладки.

### 5. Улучшенное логирование во всех местах

Добавлено:
- `exc_info=True` для всех error логов
- Информативные сообщения о ходе обработки
- Уникальные идентификаторы для потоков обработки updates

## Как это работает теперь

1. **При старте приложения:**
   - Создаётся Telegram Application
   - Регистрируются handlers
   - Application инициализируется (БЕЗ start())
   - Устанавливается webhook URL

2. **При получении update от Telegram:**
   - Flask получает POST запрос на `/webhook`
   - Сразу возвращает 200 OK (чтобы Telegram не ждал)
   - Запускает обработку в фоновом потоке
   - В потоке: `asyncio.run()` создаёт новый event loop, обрабатывает update, ждёт все задачи, закрывает loop

3. **При отправке сообщения ботом:**
   - Все async методы (`await context.bot.send_message()`, `await update.message.reply_text()`) выполняются внутри активного event loop
   - Event loop не закрывается пока все задачи не завершены
   - Сообщения отправляются успешно

4. **При остановке приложения:**
   - `atexit` вызывает `cleanup_telegram_app()`
   - Application корректно завершается через `shutdown()`

## Тестирование

Для тестирования исправлений:

1. Запустить бота в webhook режиме
2. Отправить команду `/start`
3. Создать заказ через бота
4. Проверить что все сообщения отправляются без ошибок
5. Проверить логи на отсутствие "Event loop is closed"

## Критерии приёмки

✅ Бот отправляет сообщения через webhook без ошибки "Event loop is closed"  
✅ Все асинхронные операции выполняются корректно  
✅ Добавлен error handling для предотвращения падений  
✅ Добавлено подробное логирование с полным stack trace  
✅ Graceful shutdown при остановке приложения  

## Дополнительные улучшения

- Thread-safe обработка updates с уникальными именами потоков
- Fallback механизм на случай проблем с event loop
- Подробное логирование на каждом этапе для отладки
- Правильная очистка ресурсов при завершении

## Ссылки

- [python-telegram-bot webhook docs](https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html#telegram.ext.Application.run_webhook)
- [asyncio event loop](https://docs.python.org/3/library/asyncio-eventloop.html)
