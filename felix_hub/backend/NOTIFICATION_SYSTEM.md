# Система Telegram-уведомлений механикам

## Обзор

Модуль для отправки уведомлений механикам через Telegram, когда их заказы готовы к выдаче.

## Реализованный функционал

### Файлы

1. **`utils/notifier.py`** - основной модуль уведомлений
2. **`app.py`** - обновлён для интеграции с системой уведомлений
3. **`test_notifier.py`** - тесты для модуля уведомлений

### Функции модуля notifier.py

#### `send_telegram_notification(chat_id, message, parse_mode='HTML')`
Базовая функция отправки уведомлений через Telegram Bot API.

**Параметры:**
- `chat_id` - Telegram ID получателя
- `message` - текст сообщения
- `parse_mode` - режим парсинга (HTML, Markdown)

**Возвращает:** `bool` - True если отправлено успешно

**Особенности:**
- Timeout 5 секунд
- Обработка всех типов ошибок (таймаут, сеть, API)
- Graceful degradation - не падает если BOT_TOKEN отсутствует

#### `notify_order_ready(order)`
Отправляет красивое уведомление механику о готовности заказа.

**Формат сообщения:**
```
✅ Заказ №{id} готов!

📦 Детали:
  • Передние колодки
  • Диски передние

🚗 VIN: 4T1BE32K
📅 Дата заказа: 29.10.2025 15:30

Забери запчасти у кладовщика! 🔧
```

#### `notify_order_status_changed(order, old_status, new_status)`
Уведомляет об изменении статуса заказа.

**Статусы с эмодзи:**
- `новый` - 🆕
- `в работе` - ⏳
- `готов` - ✅
- `выдан` - 📦

**Примечание:** Уведомления отправляются только для статусов "готов" и "выдан"

#### `send_order_delayed_notification(order)`
Уведомляет о задержке в обработке заказа.

#### `send_bulk_notification(telegram_ids, message)`
Массовая рассылка уведомлений.

**Возвращает:** `dict` со статистикой `{'success': int, 'failed': int}`

#### `send_with_retry(chat_id, message, max_retries=3)`
Отправка с повторными попытками и экспоненциальной задержкой.

## Интеграция с app.py

### Изменения в update_order endpoint

```python
@app.route('/api/orders/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    # ...
    old_status = order.status
    
    if 'status' in data:
        new_status = data['status']
        order.status = new_status
        
        # Отправка уведомлений
        if new_status == 'готов':
            notify_order_ready(order)
        elif new_status in ['в работе', 'выдан']:
            notify_order_status_changed(order, old_status, new_status)
    # ...
```

### Логирование

Обновлена конфигурация логирования для записи в файл:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('felix_hub.log'),
        logging.StreamHandler()
    ]
)
```

Все уведомления логируются с информацией:
- Успешная отправка
- Ошибки отправки (с деталями)
- Таймауты
- Сетевые ошибки

## Конфигурация

### Переменные окружения

Добавьте в файл `.env`:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

**Примечание:** Переменная уже добавлена в `.env.example`

## Обработка ошибок

Система полностью отказоустойчива:

1. **Отсутствие BOT_TOKEN** - логируется ошибка, система продолжает работу
2. **Таймауты** - логируется, возвращается False
3. **Сетевые ошибки** - логируется, возвращается False
4. **Ошибки Telegram API** - логируется с кодом ответа, возвращается False

API продолжает работать даже если Telegram недоступен.

## Тестирование

### Запуск тестов

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Запустить все тесты
python test_api.py
python test_comprehensive.py
python test_filters.py
python test_notifier.py
```

### Результаты тестов

Все тесты проходят успешно ✅:
- Базовый API тест (test_api.py)
- Комплексный тест (test_comprehensive.py)
- Тесты фильтрации (test_filters.py)
- Тесты уведомлений (test_notifier.py)

## Критерии приёмки

✅ Модуль notifier.py создан со всеми функциями  
✅ send_telegram_notification() отправляет сообщения через Bot API  
✅ notify_order_ready() формирует красивое уведомление о готовности  
✅ notify_order_status_changed() уведомляет об изменении статуса  
✅ Интеграция с app.py: уведомления отправляются при смене статуса на "готов"  
✅ Обработка ошибок (таймауты, сбои API)  
✅ Логирование всех отправок  
✅ BOT_TOKEN читается из .env  
✅ Система работает даже если Telegram API недоступен (не падает)  
✅ HTML-форматирование сообщений с эмодзи  

## Примеры использования

### Отправка простого уведомления

```python
from utils.notifier import send_telegram_notification

success = send_telegram_notification(
    chat_id='123456789',
    message='<b>Тестовое уведомление</b> ✅'
)
```

### Уведомление о готовности заказа

```python
from utils.notifier import notify_order_ready

order = Order.query.get(order_id)
notify_order_ready(order)
```

### Массовая рассылка

```python
from utils.notifier import send_bulk_notification

telegram_ids = ['123', '456', '789']
results = send_bulk_notification(
    telegram_ids,
    '🔧 <b>Внимание!</b> Склад работает по сокращённому графику.'
)
print(f"Успешно: {results['success']}, Ошибок: {results['failed']}")
```

### Отправка с повторными попытками

```python
from utils.notifier import send_with_retry

success = send_with_retry(
    chat_id='123456789',
    message='Критически важное уведомление',
    max_retries=3
)
```

## Технические детали

- **API URL:** `https://api.telegram.org/bot{BOT_TOKEN}/sendMessage`
- **Timeout:** 5 секунд
- **Parse mode:** HTML (по умолчанию)
- **Retry logic:** Экспоненциальная задержка (2^attempt секунд)
- **Logging level:** INFO
- **Log file:** felix_hub.log

## Безопасность

1. BOT_TOKEN хранится в .env (не коммитится в git)
2. .env добавлен в .gitignore
3. Валидация chat_id перед отправкой
4. Timeout для предотвращения зависаний
5. Обработка всех исключений

## Мониторинг

Все события логируются в `felix_hub.log`:

```
2025-10-29 20:04:11 - utils.notifier - INFO - Уведомление отправлено пользователю 123456789
2025-10-29 20:04:11 - utils.notifier - INFO - Уведомление о готовности заказа №5 отправлено
2025-10-29 20:04:11 - utils.notifier - ERROR - Таймаут при отправке уведомления пользователю 987654321
```
