# Решение проблем Felix Hub

Это руководство поможет решить наиболее распространённые проблемы при работе с системой Felix Hub.

## Содержание
- [Бот не отвечает](#бот-не-отвечает)
- [Уведомления не приходят](#уведомления-не-приходят)
- [Принтер не печатает](#принтер-не-печатает)
- [Заказы не отображаются в админке](#заказы-не-отображаются-в-админке)
- [База данных не создаётся](#база-данных-не-создаётся)
- [Backend не запускается](#backend-не-запускается)
- [Ошибки при создании заказа](#ошибки-при-создании-заказа)
- [Проблемы с фото](#проблемы-с-фото)
- [Ошибки зависимостей](#ошибки-зависимостей)
- [Проблемы производительности](#проблемы-производительности)

---

## Бот не отвечает

### Симптомы
- Бот не реагирует на команду `/start`
- Сообщения в бот не доставляются
- Бот показывается офлайн в Telegram

### Решение

#### 1. Проверьте правильность BOT_TOKEN

```bash
cd felix_hub/bot
cat .env
```

Убедитесь, что `BOT_TOKEN` совпадает с токеном, полученным от @BotFather.

Проверить токен можно через API:
```bash
curl https://api.telegram.org/bot<ВАШ_ТОКЕН>/getMe
```

Должен вернуть информацию о боте. Если ошибка - токен неверный.

#### 2. Убедитесь, что backend запущен

```bash
curl http://localhost:5000/api/orders
```

Должен вернуть массив (пустой или с заказами). Если ошибка соединения - backend не запущен.

#### 3. Проверьте логи бота

```bash
cd felix_hub/bot
python bot.py
```

Смотрите на вывод в терминале. Типичные ошибки:
- `Unauthorized` - неверный токен
- `Connection refused` - backend не запущен
- `Module not found` - не установлены зависимости

#### 4. Проверьте сетевое соединение

```bash
ping api.telegram.org
```

Если пинг не проходит - проблемы с интернет-соединением или файрволом.

#### 5. Убедитесь, что используете правильного бота

В Telegram найдите бота по username, который указан в @BotFather. Возможно, вы используете другого бота.

---

## Уведомления не приходят

### Симптомы
- При изменении статуса на "готов" уведомление не приходит в Telegram
- Механик не получает сообщения о готовности заказа

### Решение

#### 1. Проверьте BOT_TOKEN в backend

```bash
cd felix_hub/backend
cat .env | grep BOT_TOKEN
```

Убедитесь, что `BOT_TOKEN` в backend/.env совпадает с токеном бота.

#### 2. Проверьте telegram_id механика

Telegram ID должен быть числом (например, `123456789`). Проверьте в базе данных:

```bash
cd felix_hub/backend
sqlite3 felix_hub.db
SELECT id, mechanic_name, telegram_id FROM orders;
.quit
```

Если `telegram_id` неверный, механик не получит уведомление.

**Как узнать свой telegram_id:**
1. Напишите боту @userinfobot
2. Он вернёт ваш ID
3. Убедитесь, что это число совпадает с `telegram_id` в заказе

#### 3. Убедитесь, что механик использует того же бота

Механик должен хотя бы раз написать боту `/start`, чтобы бот мог ему отправлять сообщения.

#### 4. Проверьте логи backend

```bash
cd felix_hub/backend
tail -f felix_hub.log
```

Найдите строки с `notify_order_ready`. Если есть ошибки:
- `Chat not found` - механик не общался с ботом
- `Unauthorized` - неверный токен
- `Bot was blocked by the user` - механик заблокировал бота

#### 5. Тест уведомления вручную

Откройте Python REPL:
```bash
cd felix_hub/backend
source venv/bin/activate
python
```

```python
from utils.notifier import notify_order_ready
from models import db, Order
from app import app

with app.app_context():
    order = Order.query.first()
    if order:
        notify_order_ready(order)
    else:
        print("No orders found")
```

Смотрите на ошибки в выводе.

---

## Принтер не печатает

### Симптомы
- При изменении статуса на "готов" чек не печатается
- Тестовая печать не работает
- Система создаёт PDF вместо печати

### Решение

#### 1. Проверьте PRINTER_ENABLED

```bash
cd felix_hub/backend
cat .env | grep PRINTER
```

Должно быть `PRINTER_ENABLED=true`. Если `false` - система работает в режиме PDF.

#### 2. Проверьте доступность принтера

```bash
ping <PRINTER_IP>
# Например: ping 192.168.0.50
```

Если пинг не проходит:
- Принтер выключен
- Неверный IP адрес
- Принтер не в той же сети

#### 3. Проверьте порт принтера

```bash
telnet <PRINTER_IP> 9100
```

Если соединение успешно, нажмите Ctrl+] потом `quit`. Если ошибка:
- Порт неверный (возможно 9100, 9101, 9102)
- Firewall блокирует соединение
- Принтер не поддерживает network printing

#### 4. Проверьте IP адрес принтера

IP адрес мог измениться (если используется DHCP). Найдите текущий IP:
- Распечатайте конфигурацию (обычно кнопка на принтере)
- Зайдите в веб-интерфейс роутера
- Используйте утилиту сканирования сети (nmap, Fing)

Обновите `PRINTER_IP` в `.env` и перезапустите backend.

#### 5. Посмотрите логи

```bash
cd felix_hub/backend
tail -f felix_hub.log | grep -i print
```

Типичные ошибки:
- `Connection refused` - принтер недоступен
- `Connection timeout` - принтер не отвечает
- `USB printer not found` - неверная конфигурация (ожидается сетевой принтер)

#### 6. Тестовая печать

```bash
curl -X POST http://localhost:5000/api/printer/test
```

Если возвращает ошибку, смотрите сообщение и логи.

#### 7. Fallback на PDF

Если принтер временно недоступен, система автоматически создаст PDF:

**Linux/Mac:**
```bash
ls -la /tmp/felix_*.pdf
```

**Windows:**
```bash
dir C:\Temp\felix_*.pdf
```

PDF можно распечатать вручную на любом принтере.

#### 8. Проверьте модель принтера

Убедитесь, что ваш принтер поддерживает ESC/POS команды. Список совместимых принтеров:
- Epson TM-T20, TM-T82, TM-T88
- Star Micronics TSP100, TSP650
- Citizen CT-S310
- и большинство других чековых термопринтеров

Если ваш принтер не поддерживает ESC/POS, используйте режим PDF (`PRINTER_ENABLED=false`).

---

## Заказы не отображаются в админке

### Симптомы
- Админ-панель открывается, но заказы не загружаются
- Таблица пустая, хотя заказы были созданы
- Бесконечная загрузка

### Решение

#### 1. Откройте DevTools (F12) -> Console

Смотрите на ошибки JavaScript. Типичные проблемы:
- `Failed to fetch` - backend не отвечает
- `CORS error` - проблема с CORS настройками
- `JSON parse error` - backend вернул невалидный JSON

#### 2. Проверьте backend API вручную

```bash
curl http://localhost:5000/api/orders
```

Должен вернуть JSON массив. Если ошибка:
- `Connection refused` - backend не запущен
- `500 Internal Server Error` - ошибка в backend (смотрите логи)

#### 3. Проверьте CORS

В `felix_hub/backend/app.py` должна быть строка:
```python
CORS(app)
```

Если её нет, добавьте после `app = Flask(__name__)`.

#### 4. Проверьте логи backend

```bash
cd felix_hub/backend
tail -f felix_hub.log
```

Перезагрузите админ-панель и смотрите на ошибки.

#### 5. Проверьте базу данных

```bash
cd felix_hub/backend
sqlite3 felix_hub.db
SELECT COUNT(*) FROM orders;
.quit
```

Если возвращает 0 - заказов нет в базе. Создайте тестовый заказ через бота.

#### 6. Очистите кэш браузера

Нажмите Ctrl+Shift+R (или Cmd+Shift+R на Mac) для жёсткого обновления страницы.

#### 7. Проверьте путь к API

Откройте `felix_hub/backend/static/admin.js` и убедитесь, что `API_URL` правильный:
```javascript
const API_URL = '/api/orders';
```

Если используете proxy или нестандартный порт, обновите путь.

---

## База данных не создаётся

### Симптомы
- Backend запускается, но файл `felix_hub.db` не появляется
- Ошибка `no such table: orders`
- Ошибка `unable to open database file`

### Решение

#### 1. Проверьте DATABASE_URL

```bash
cd felix_hub/backend
cat .env | grep DATABASE_URL
```

Должно быть `DATABASE_URL=sqlite:///felix_hub.db` (три слэша для относительного пути).

#### 2. Проверьте права на запись

```bash
cd felix_hub/backend
touch test_write.txt
```

Если ошибка - нет прав на запись в папку. Исправьте права:
```bash
chmod 755 /path/to/felix_hub/backend
```

#### 3. Удалите старую БД и пересоздайте

```bash
cd felix_hub/backend
rm felix_hub.db  # если существует
python app.py
```

Должна появиться надпись `Database initialized`.

#### 4. Проверьте, что SQLAlchemy установлен

```bash
cd felix_hub/backend
source venv/bin/activate
pip list | grep -i sql
```

Должны быть:
- `SQLAlchemy`
- `Flask-SQLAlchemy`

Если нет, установите:
```bash
pip install -r requirements.txt
```

#### 5. Проверьте models.py

```bash
cd felix_hub/backend
python
```

```python
from models import db, Order
from app import app

with app.app_context():
    db.create_all()
    print("Database created successfully")
```

Если ошибка - проблема в models.py или app.py.

---

## Backend не запускается

### Симптомы
- `python app.py` завершается с ошибкой
- Port already in use
- Module not found

### Решение

#### 1. Ошибка "Address already in use"

Порт 5000 уже занят. Найдите процесс:

**Linux/Mac:**
```bash
lsof -i :5000
kill <PID>
```

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

Или измените порт в app.py:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

#### 2. Ошибка "ModuleNotFoundError"

Не установлены зависимости:
```bash
cd felix_hub/backend
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Ошибка с .env файлом

```bash
cd felix_hub/backend
cp .env.example .env
# Отредактируйте .env
```

#### 4. Ошибка с импортами

Убедитесь, что структура папок правильная:
```
felix_hub/backend/
├── app.py
├── models.py
├── utils/
│   ├── __init__.py
│   ├── notifier.py
│   └── printer.py
```

Файл `utils/__init__.py` должен существовать (может быть пустым).

---

## Ошибки при создании заказа

### Симптомы
- Бот показывает ошибку при отправке заказа
- Backend возвращает 400 или 500
- Заказ не сохраняется в базе

### Решение

#### 1. Проверьте формат данных

Backend ожидает JSON с полями:
- `mechanic_name` (строка)
- `telegram_id` (число)
- `category` (строка)
- `vin` (строка, минимум 4 символа)
- `selected_parts` (массив строк, не пустой)
- `is_original` (boolean, опционально)
- `photo_url` (строка, опционально)

#### 2. Проверьте VIN

VIN должен быть минимум 4 символа. Если короче - ошибка 400.

#### 3. Проверьте selected_parts

Массив не должен быть пустым. Должен содержать хотя бы одну запчасть.

#### 4. Смотрите логи backend

```bash
cd felix_hub/backend
tail -f felix_hub.log
```

Создайте заказ через бота и смотрите на ошибки в логах.

#### 5. Тест API вручную

```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "mechanic_name": "Test User",
    "telegram_id": 123456789,
    "category": "Тормоза",
    "vin": "TEST1234",
    "selected_parts": ["Передние колодки"],
    "is_original": true
  }'
```

Должен вернуть JSON с созданным заказом и status 201.

---

## Проблемы с фото

### Симптомы
- Фото не загружается через бота
- Фото не отображается в админке
- Ошибка при отправке фото

### Решение

#### 1. Проверьте размер фото

Telegram ограничивает размер файлов. Максимальный размер:
- Фото: 10 MB (как photo)
- Документ: 20 MB (как document)

Если фото больше, попросите механика уменьшить размер.

#### 2. Проверьте URL фото

В админке откройте DevTools (F12), найдите элемент `<img>` с фото, проверьте атрибут `src`.

Если URL начинается с `https://api.telegram.org/file/bot...` - это правильный формат.

#### 3. Проверьте BOT_TOKEN

Для доступа к файлам Telegram нужен правильный токен. Убедитесь, что `BOT_TOKEN` в `.env` правильный.

#### 4. Фото опционально

Если фото не критично, можно пропустить этот шаг. Система работает без фото.

---

## Ошибки зависимостей

### Симптомы
- `ModuleNotFoundError`
- `ImportError`
- Ошибки при установке зависимостей

### Решение

#### 1. Убедитесь, что используете виртуальное окружение

```bash
cd felix_hub/backend  # или bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 2. Обновите pip

```bash
pip install --upgrade pip
```

#### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

#### 4. Проблемы с python-escpos

Если ошибка при установке `python-escpos`:

**Linux:**
```bash
sudo apt-get install libusb-1.0-0-dev
pip install python-escpos
```

**Mac:**
```bash
brew install libusb
pip install python-escpos
```

**Windows:**
```bash
pip install python-escpos
```

#### 5. Проблемы с pandas/openpyxl

```bash
pip install pandas openpyxl
```

#### 6. Конфликты версий

Очистите и переустановите:
```bash
pip uninstall -y -r <(pip freeze)
pip install -r requirements.txt
```

---

## Проблемы производительности

### Симптомы
- Админ-панель медленно загружается
- Backend долго отвечает
- База данных растёт

### Решение

#### 1. Ограничьте количество заказов

В admin.js измените лимит:
```javascript
const response = await fetch(`${API_URL}?limit=50`);
```

#### 2. Переключитесь на PostgreSQL

SQLite не оптимален для production. Используйте PostgreSQL для больших объёмов данных.

#### 3. Добавьте индексы

Если используете PostgreSQL:
```sql
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_telegram_id ON orders(telegram_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

#### 4. Архивируйте старые заказы

Периодически перемещайте старые заказы в архивную таблицу:
```sql
-- Создать архивную таблицу
CREATE TABLE orders_archive AS SELECT * FROM orders WHERE 1=0;

-- Переместить старые заказы (старше 6 месяцев)
INSERT INTO orders_archive SELECT * FROM orders 
WHERE created_at < NOW() - INTERVAL '6 months';

DELETE FROM orders WHERE created_at < NOW() - INTERVAL '6 months';
```

#### 5. Отключите DEBUG режим

В app.py измените:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

#### 6. Используйте production WSGI сервер

Вместо встроенного сервера Flask используйте gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Получение дополнительной помощи

Если проблема не решена:

1. **Соберите информацию:**
   - Версия Python (`python --version`)
   - ОС (Linux/Mac/Windows)
   - Логи backend (`felix_hub/backend/felix_hub.log`)
   - Логи бота (вывод в терминале)
   - Текст ошибки полностью

2. **Проверьте документацию:**
   - `DEPLOYMENT.md` - инструкции по развёртыванию
   - `felix_hub/backend/API_DOCUMENTATION.md` - документация API
   - `felix_hub/backend/README.md` - информация о backend

3. **Создайте issue в репозитории** с подробным описанием проблемы

4. **Проверьте существующие issues** - возможно, проблема уже решена

---

## Полезные команды

### Проверка статуса системы
```bash
# Backend
curl http://localhost:5000/api/orders/stats

# Бот (проверить, что работает)
curl https://api.telegram.org/bot<TOKEN>/getMe
```

### Очистка базы данных (для тестирования)
```bash
cd felix_hub/backend
rm felix_hub.db
python app.py
```

### Экспорт логов
```bash
cd felix_hub/backend
tail -n 500 felix_hub.log > debug_logs.txt
```

### Проверка сетевых соединений
```bash
# Backend API
netstat -an | grep 5000

# Принтер
nc -zv <PRINTER_IP> 9100

# Telegram API
ping api.telegram.org
```
