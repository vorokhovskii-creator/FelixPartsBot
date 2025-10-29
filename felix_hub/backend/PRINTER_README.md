# Модуль печати чеков ESC/POS

## Обзор

Модуль автоматической печати чеков заказов на ESC/POS термопринтере с автоматическим fallback на PDF для обычных принтеров.

## Возможности

- ✅ Печать чеков на ESC/POS термопринтерах (58мм, 80мм)
- ✅ Автоматическая печать при изменении статуса заказа на "готов"
- ✅ Принудительная печать через API
- ✅ Тестовая печать для проверки принтера
- ✅ Автоматический fallback на PDF при недоступности принтера
- ✅ QR-код с ID заказа на чеке
- ✅ Перенос длинных названий деталей
- ✅ Полное логирование всех операций

## Архитектура

### Файлы

```
felix_hub/backend/
├── utils/
│   └── printer.py              # Основной модуль печати
├── app.py                      # Flask приложение (с интеграцией печати)
├── docs/
│   └── PRINTER_SETUP.md       # Инструкция по настройке
└── .env.example               # Пример конфигурации
```

### Функции модуля printer.py

#### `print_order_receipt(order) -> bool`
Печатает чек заказа на термопринтере ESC/POS.

**Параметры:**
- `order`: Объект Order из базы данных

**Возвращает:**
- `True` если печать успешна
- `False` при ошибке

**Формат чека:**
```
================================
        СТО Felix
   Автосервис премиум класса
================================

Заказ №123
Дата: 29.10.2023 14:30
Механик: Иван Иванов
VIN: WVWZZZ1KZBW123456
Категория: Двигатель
================================
Запчасти:
1. Фильтр масляный оригинальный
2. Свечи зажигания NGK
3. Прокладка клапанной крышки
================================
Тип: ✨ Оригинал
Статус: ГОТОВ
📸 Фото прикреплено
================================

Спасибо за работу!
Felix Auto Service
Напечатано: 29.10.2023 14:30

[QR-код: FELIX-ORDER-123]
```

#### `wrap_text(text, width) -> list`
Переносит длинный текст на несколько строк.

**Параметры:**
- `text`: Исходный текст
- `width`: Максимальная ширина строки

**Возвращает:**
- Список строк

#### `print_test_receipt() -> bool`
Печатает тестовый чек для проверки принтера.

**Возвращает:**
- `True` если печать успешна

#### `generate_order_pdf(order, output_path=None) -> Optional[str]`
Генерирует PDF-чек для печати на обычном принтере.

**Параметры:**
- `order`: Объект Order
- `output_path`: Путь для сохранения PDF (опционально)

**Возвращает:**
- Путь к созданному PDF или `None` при ошибке

**Формат имени файла:**
- `/tmp/felix_order_{ORDER_ID}_{TIMESTAMP}.pdf`
- Пример: `/tmp/felix_order_123_20231029_143000.pdf`

#### `print_order_with_fallback(order) -> bool`
Пытается напечатать на термопринтере, при ошибке создает PDF.

**Параметры:**
- `order`: Объект Order

**Возвращает:**
- `True` если хотя бы один метод сработал

**Логика:**
1. Пробует печать на термопринтере
2. Если не получилось → создает PDF
3. Возвращает `True` если хотя бы один метод сработал

## API Endpoints

### POST /api/orders/\<id\>/print
Принудительная печать чека заказа.

**Пример запроса:**
```bash
curl -X POST http://localhost:5000/api/orders/123/print
```

**Успешный ответ (200):**
```json
{
  "message": "Чек отправлен на печать"
}
```

**Ошибка (500):**
```json
{
  "error": "Ошибка печати"
}
```

### POST /api/printer/test
Тестовая печать для проверки принтера.

**Пример запроса:**
```bash
curl -X POST http://localhost:5000/api/printer/test
```

**Успешный ответ (200):**
```json
{
  "message": "Тестовый чек напечатан"
}
```

### PATCH /api/orders/\<id\>
Обновление заказа (включает автоматическую печать при статусе "готов").

**Пример запроса:**
```bash
curl -X PATCH http://localhost:5000/api/orders/123 \
  -H "Content-Type: application/json" \
  -d '{"status": "готов"}'
```

При изменении статуса на "готов":
1. Печатается чек (термопринтер или PDF)
2. Поле `printed` устанавливается в `true`
3. Отправляется уведомление

## Конфигурация

### Переменные окружения (.env)

```env
# Включение/отключение печати
PRINTER_ENABLED=true

# IP-адрес принтера в локальной сети
PRINTER_IP=192.168.0.50

# Порт принтера (обычно 9100 для ESC/POS)
PRINTER_PORT=9100

# Ширина чека в символах (32 для 58мм, 48 для 80мм)
RECEIPT_WIDTH=32
```

### Значения по умолчанию

Если переменные не установлены, используются значения по умолчанию:
- `PRINTER_ENABLED`: `false`
- `PRINTER_IP`: `192.168.0.50`
- `PRINTER_PORT`: `9100`
- `RECEIPT_WIDTH`: `32`

## Установка зависимостей

```bash
cd /home/engine/project/felix_hub/backend
pip install -r requirements.txt
```

Основные зависимости:
- `python-escpos==3.0` - для ESC/POS принтеров
- `reportlab==4.0.7` - для генерации PDF

## Поддерживаемые принтеры

- Любые ESC/POS принтеры (58мм, 80мм)
- Epson TM-T20, TM-T88
- Xprinter XP-58, XP-80
- Rongta RP58, RP80
- И другие ESC/POS совместимые принтеры

## Логирование

Все операции логируются в `felix_hub.log` и консоль.

### Примеры логов

**Успешная печать:**
```
INFO: Подключение к принтеру 192.168.0.50:9100
INFO: Чек заказа №123 успешно напечатан
```

**Принтер отключен:**
```
INFO: Печать отключена (PRINTER_ENABLED=false)
```

**Ошибка подключения:**
```
ERROR: Ошибка печати заказа №123: Connection refused
WARNING: Термопринтер недоступен, создаю PDF для заказа №123
INFO: PDF-чек для заказа №123 создан: /tmp/felix_order_123_20231029_143000.pdf
```

**QR-код не поддерживается:**
```
WARNING: Не удалось напечатать QR-код: QR code not supported
```

## Тестирование

### Запуск unit-тестов

```bash
cd /home/engine/project/felix_hub/backend
python -m unittest test_printer.py -v
```

### Тестовая печать

1. Убедитесь, что принтер включен и подключен к сети
2. Настройте переменные окружения в `.env`
3. Запустите тестовую печать:

```bash
curl -X POST http://localhost:5000/api/printer/test
```

## Примеры использования

### Пример 1: Автоматическая печать при изменении статуса

```python
from models import Order, db
from utils.printer import print_order_with_fallback

@app.route('/api/orders/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if 'status' in data and data['status'] == 'готов':
        # Печать чека
        if print_order_with_fallback(order):
            order.printed = True
    
    db.session.commit()
    return jsonify(order.to_dict()), 200
```

### Пример 2: Принудительная печать

```python
from utils.printer import print_order_with_fallback

order = Order.query.get(123)
success = print_order_with_fallback(order)

if success:
    print("Чек напечатан")
else:
    print("Ошибка печати")
```

### Пример 3: Только PDF (без принтера)

```python
from utils.printer import generate_order_pdf

order = Order.query.get(123)
pdf_path = generate_order_pdf(order)

if pdf_path:
    print(f"PDF создан: {pdf_path}")
```

## Troubleshooting

См. подробную информацию в `docs/PRINTER_SETUP.md`

### Быстрые решения

**Ошибка подключения:**
```bash
ping 192.168.0.50  # Проверьте доступность принтера
```

**Текст обрезается:**
- Измените `RECEIPT_WIDTH` в `.env`
- Для 58мм: 30-34
- Для 80мм: 46-50

**Принтер не отвечает:**
- Перезагрузите принтер
- Проверьте бумагу
- Проверьте крышку

**Отключить печать:**
```env
PRINTER_ENABLED=false
```

## Безопасность

- Используйте изолированную VLAN для принтеров
- Ограничьте доступ к порту 9100
- Регулярно обновляйте прошивку принтера
- Логируйте все операции печати

## Производительность

- Печать одного чека: ~2-3 секунды
- Генерация PDF: ~1 секунда
- Fallback: автоматический при таймауте

## Совместимость

- Python 3.8+
- Flask 3.0+
- SQLAlchemy 3.1+
- Работает на Linux, Windows, macOS

## Лицензия

Часть проекта Felix Hub (СТО Felix)

## Авторы

Felix Auto Service - Development Team
