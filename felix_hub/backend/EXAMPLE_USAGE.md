# Примеры использования системы печати чеков

## Быстрый старт

### 1. Настройка окружения

Создайте файл `.env`:

```env
FLASK_SECRET_KEY=your-secret-key
BOT_TOKEN=your-telegram-token
DATABASE_URL=sqlite:///database.db

# Printer Configuration
PRINTER_ENABLED=true
PRINTER_IP=192.168.0.50
PRINTER_PORT=9100
RECEIPT_WIDTH=32
```

### 2. Установка зависимостей

```bash
cd /home/engine/project/felix_hub/backend
pip install -r requirements.txt
```

### 3. Запуск приложения

```bash
python app.py
```

## Примеры API запросов

### Пример 1: Создание заказа

```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "mechanic_name": "Иван Петров",
    "telegram_id": "123456789",
    "category": "Двигатель",
    "vin": "WVWZZZ1KZBW123456",
    "selected_parts": [
      "Фильтр масляный Mann W712/73",
      "Масло моторное Castrol 5W-40",
      "Прокладка поддона"
    ],
    "is_original": true,
    "photo_url": "https://example.com/car.jpg"
  }'
```

**Ответ:**
```json
{
  "id": 1,
  "mechanic_name": "Иван Петров",
  "telegram_id": "123456789",
  "category": "Двигатель",
  "vin": "WVWZZZ1KZBW123456",
  "selected_parts": ["Фильтр масляный Mann W712/73", "..."],
  "is_original": true,
  "photo_url": "https://example.com/car.jpg",
  "status": "новый",
  "printed": false,
  "created_at": "2023-10-29T14:30:00"
}
```

### Пример 2: Изменение статуса (автоматическая печать)

```bash
curl -X PATCH http://localhost:5000/api/orders/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "готов"}'
```

**Что происходит:**
1. ✅ Статус меняется на "готов"
2. ✅ Автоматически печатается чек
3. ✅ Поле `printed` становится `true`
4. ✅ Отправляется Telegram уведомление

**Ответ:**
```json
{
  "id": 1,
  "status": "готов",
  "printed": true,
  ...
}
```

### Пример 3: Принудительная печать

```bash
curl -X POST http://localhost:5000/api/orders/1/print
```

**Ответ (успех):**
```json
{
  "message": "Чек отправлен на печать"
}
```

**Ответ (ошибка):**
```json
{
  "error": "Ошибка печати"
}
```

### Пример 4: Тестовая печать

```bash
curl -X POST http://localhost:5000/api/printer/test
```

**Ответ:**
```json
{
  "message": "Тестовый чек напечатан"
}
```

## Примеры использования в Python

### Пример 1: Печать чека на термопринтере

```python
from models import Order
from utils.printer import print_order_receipt

# Получаем заказ
order = Order.query.get(1)

# Печатаем чек
success = print_order_receipt(order)

if success:
    print("✓ Чек напечатан на термопринтере")
else:
    print("✗ Ошибка печати")
```

### Пример 2: Генерация PDF

```python
from models import Order
from utils.printer import generate_order_pdf

# Получаем заказ
order = Order.query.get(1)

# Генерируем PDF
pdf_path = generate_order_pdf(order)

if pdf_path:
    print(f"✓ PDF создан: {pdf_path}")
    # Можно открыть в браузере или отправить на печать
else:
    print("✗ Ошибка создания PDF")
```

### Пример 3: Печать с fallback

```python
from models import Order
from utils.printer import print_order_with_fallback

# Получаем заказ
order = Order.query.get(1)

# Пробуем печать (сначала термопринтер, потом PDF)
success = print_order_with_fallback(order)

if success:
    print("✓ Чек создан (термопринтер или PDF)")
    order.printed = True
    db.session.commit()
else:
    print("✗ Не удалось создать чек")
```

### Пример 4: Тестовая печать

```python
from utils.printer import print_test_receipt

# Печатаем тестовый чек
success = print_test_receipt()

if success:
    print("✓ Тестовая печать успешна")
else:
    print("✗ Принтер недоступен")
```

### Пример 5: Перенос длинного текста

```python
from utils.printer import wrap_text

# Длинное название детали
part_name = "Фильтр масляный оригинальный Mann W712/73 для двигателей TSI"

# Переносим на строки по 32 символа
lines = wrap_text(part_name, 32)

for i, line in enumerate(lines, 1):
    if i == 1:
        print(f"1. {line}")
    else:
        print(f"   {line}")

# Вывод:
# 1. Фильтр масляный оригинальный
#    Mann W712/73 для двигателей
#    TSI
```

## Примеры workflow

### Workflow 1: Новый заказ → Готов

```python
from models import Order, db
from utils.printer import print_order_with_fallback
from utils.notifier import notify_order_ready

# 1. Создаем заказ
order = Order(
    mechanic_name="Петр Сидоров",
    telegram_id="987654321",
    category="Трансмиссия",
    vin="XTA217030B0123456",
    selected_parts=["Масло АКПП", "Фильтр АКПП"],
    is_original=False
)
db.session.add(order)
db.session.commit()
print(f"✓ Заказ #{order.id} создан")

# 2. Меняем статус на "готов"
order.status = "готов"

# 3. Печатаем чек
if print_order_with_fallback(order):
    order.printed = True
    print("✓ Чек напечатан")

# 4. Отправляем уведомление
notify_order_ready(order)
print("✓ Уведомление отправлено")

# 5. Сохраняем изменения
db.session.commit()
print(f"✓ Заказ #{order.id} завершен")
```

### Workflow 2: Повторная печать

```python
from models import Order
from utils.printer import print_order_with_fallback

# Получаем заказ
order = Order.query.get(123)

if not order:
    print("✗ Заказ не найден")
else:
    # Проверяем, был ли уже напечатан
    if order.printed:
        print("⚠ Чек уже был напечатан")
        confirm = input("Напечатать повторно? (y/n): ")
        if confirm.lower() != 'y':
            exit()
    
    # Печатаем
    if print_order_with_fallback(order):
        print("✓ Чек напечатан")
        order.printed = True
        db.session.commit()
    else:
        print("✗ Ошибка печати")
```

### Workflow 3: Пакетная печать

```python
from models import Order
from utils.printer import print_order_with_fallback

# Получаем все готовые заказы, которые не были напечатаны
orders = Order.query.filter_by(
    status="готов",
    printed=False
).all()

print(f"Найдено {len(orders)} заказов для печати")

# Печатаем каждый
for order in orders:
    print(f"\nПечать заказа #{order.id}...")
    
    if print_order_with_fallback(order):
        print(f"✓ Заказ #{order.id} напечатан")
        order.printed = True
    else:
        print(f"✗ Ошибка печати заказа #{order.id}")

# Сохраняем изменения
db.session.commit()
print(f"\n✓ Печать завершена")
```

## Сценарии использования

### Сценарий 1: Принтер работает
```
Запрос: POST /api/orders/1/print
   ↓
Подключение к 192.168.0.50:9100
   ↓
Печать чека на термопринтере
   ↓
✓ Успех: "Чек отправлен на печать"
```

### Сценарий 2: Принтер недоступен (Fallback)
```
Запрос: POST /api/orders/1/print
   ↓
Попытка подключения к 192.168.0.50:9100
   ↓
✗ Connection refused
   ↓
Fallback: Генерация PDF
   ↓
Создан /tmp/felix_order_1_20231029_143000.pdf
   ↓
✓ Успех: "Чек отправлен на печать"
```

### Сценарий 3: Печать отключена
```
Запрос: POST /api/orders/1/print
   ↓
PRINTER_ENABLED=false
   ↓
Попытка создать PDF
   ↓
Создан /tmp/felix_order_1_20231029_143000.pdf
   ↓
✓ Успех: "Чек отправлен на печать"
```

## Troubleshooting

### Проблема: Принтер не печатает

**Решение:**
```bash
# 1. Проверьте доступность
ping 192.168.0.50

# 2. Проверьте порт
telnet 192.168.0.50 9100

# 3. Проверьте логи
tail -f felix_hub.log

# 4. Запустите тестовую печать
curl -X POST http://localhost:5000/api/printer/test
```

### Проблема: PDF не создается

**Решение:**
```bash
# Установите reportlab
pip install reportlab

# Проверьте права на /tmp
ls -la /tmp

# Создайте тестовый PDF
python -c "from utils.printer import generate_order_pdf; from models import Order; order = Order.query.first(); print(generate_order_pdf(order))"
```

### Проблема: Текст обрезается

**Решение:**
```env
# Для 58мм принтера
RECEIPT_WIDTH=32

# Для 80мм принтера
RECEIPT_WIDTH=48

# Экспериментируйте
RECEIPT_WIDTH=30  # если текст обрезается справа
RECEIPT_WIDTH=34  # если есть свободное место
```

## Полезные команды

```bash
# Проверка синтаксиса
python -m py_compile utils/printer.py

# Импорт модуля
python -c "from utils.printer import *"

# Тестирование
python -m unittest test_printer.py -v
python test_printer_integration.py

# Просмотр логов
tail -f felix_hub.log

# Поиск PDF файлов
ls -lh /tmp/felix_order_*.pdf

# Очистка старых PDF
rm /tmp/felix_order_*.pdf
```

## Дополнительные ресурсы

- `docs/PRINTER_SETUP.md` - Инструкция по настройке
- `PRINTER_README.md` - Документация модуля
- `PRINTER_IMPLEMENTATION.md` - Отчет о реализации
- `test_printer.py` - Unit тесты
- `test_printer_integration.py` - Интеграционные тесты

## Контакты

Разработчик: Felix Auto Service - Development Team  
Дата: 29.10.2023  
Версия: 1.0.0
