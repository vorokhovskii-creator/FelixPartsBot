# Развёртывание Felix Hub System

## Требования
- Python 3.10+
- (Опционально) ESC/POS термопринтер в локальной сети
- Telegram Bot токен (получить через @BotFather)

## Шаг 1: Клонирование репозитория
```bash
git clone <repo-url>
cd FelixPartsBot
```

## Шаг 2: Настройка Backend
```bash
cd felix_hub/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env файл
```

### Настройка .env для Backend
Откройте `backend/.env` и настройте следующие параметры:

```env
# Flask
FLASK_SECRET_KEY=<сгенерируйте случайную строку>
DATABASE_URL=sqlite:///felix_hub.db

# Telegram Bot
BOT_TOKEN=<ваш токен от @BotFather>

# Printer (ESC/POS) - если используете принтер
PRINTER_ENABLED=false  # установите true если есть принтер
PRINTER_IP=192.168.0.50  # IP адрес принтера в локальной сети
PRINTER_PORT=9100
RECEIPT_WIDTH=32
```

## Шаг 3: Настройка Telegram Bot
```bash
cd ../bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Добавьте BOT_TOKEN в .env
```

### Настройка .env для Bot
Откройте `bot/.env` и добавьте:

```env
BOT_TOKEN=<ваш токен от @BotFather>
BACKEND_URL=http://localhost:5000
```

**Важно:** Используйте один и тот же `BOT_TOKEN` как в backend, так и в bot!

## Шаг 4: Запуск системы

### Терминал 1: Backend
```bash
cd felix_hub/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```
Backend запустится на **http://localhost:5000**

Вы должны увидеть:
```
* Running on http://0.0.0.0:5000
* Database initialized
```

### Терминал 2: Telegram Bot
```bash
cd felix_hub/bot
source venv/bin/activate  # Windows: venv\Scripts\activate
python bot.py
```

Вы должны увидеть:
```
Bot started successfully
Listening for orders...
```

## Шаг 5: Настройка принтера (опционально)

### Если у вас есть ESC/POS термопринтер:

1. Подключите принтер к локальной сети (Ethernet или WiFi)
2. Найдите IP-адрес принтера:
   - Посмотрите в настройках принтера
   - Или найдите в списке устройств роутера
   - Или распечатайте тестовую страницу (обычно кнопка на принтере)

3. Проверьте доступность принтера:
```bash
ping <IP_принтера>
# Например: ping 192.168.0.50
```

4. В `backend/.env` установите:
```env
PRINTER_ENABLED=true
PRINTER_IP=<IP принтера>
PRINTER_PORT=9100
RECEIPT_WIDTH=32
```

5. Перезапустите backend:
```bash
# Ctrl+C для остановки
python app.py
```

### Если принтера нет:

Система будет работать в режиме fallback - чеки будут сохраняться как PDF файлы в папке `/tmp` (Linux/Mac) или `C:\Temp` (Windows).

## Шаг 6: Тестирование

### 1. Проверка Backend API
Откройте новый терминал и выполните:
```bash
curl http://localhost:5000/api/orders
```
Должен вернуть пустой массив: `[]`

### 2. Тестирование Telegram Bot
1. Откройте Telegram
2. Найдите вашего бота по username (тот, что вы создали через @BotFather)
3. Отправьте команду `/start`
4. Бот должен ответить приветственным сообщением

### 3. Создание тестового заказа
1. В боте нажмите "📦 Создать заказ"
2. Выберите категорию (например, "🔧 Тормоза")
3. Выберите запчасти
4. Введите VIN (например, `TEST1234`)
5. Выберите оригинал/аналог
6. Пропустите фото (или загрузите любое)
7. Подтвердите заказ

### 4. Проверка админ-панели
1. Откройте браузер
2. Перейдите на **http://localhost:5000/admin**
3. Вы должны увидеть созданный заказ в таблице

### 5. Тестирование уведомлений и печати
1. В админ-панели найдите тестовый заказ
2. Измените статус на "готов" (выпадающий список)
3. Проверьте:
   - В Telegram пришло уведомление о готовности заказа
   - Если принтер включен - распечатался чек
   - Если принтер выключен - создался PDF файл в `/tmp` (Linux/Mac)

### 6. Тестовая печать (если используете принтер)
```bash
curl -X POST http://localhost:5000/api/printer/test
```
Должен распечататься тестовый чек с текущей датой и временем.

## Шаг 7: Production развёртывание

### Использование PostgreSQL (рекомендуется для production)

1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE felix_hub;
CREATE USER felix_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE felix_hub TO felix_user;
```

3. В `backend/.env` измените:
```env
DATABASE_URL=postgresql://felix_user:secure_password@localhost:5432/felix_hub
```

4. Установите драйвер PostgreSQL:
```bash
pip install psycopg2-binary
```

### Настройка через systemd (Linux)

#### Backend Service
Создайте файл `/etc/systemd/system/felix-backend.service`:

```ini
[Unit]
Description=Felix Hub Backend
After=network.target

[Service]
Type=simple
User=<ваш_пользователь>
WorkingDirectory=/path/to/FelixPartsBot/felix_hub/backend
Environment="PATH=/path/to/FelixPartsBot/felix_hub/backend/venv/bin"
ExecStart=/path/to/FelixPartsBot/felix_hub/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Bot Service
Создайте файл `/etc/systemd/system/felix-bot.service`:

```ini
[Unit]
Description=Felix Hub Telegram Bot
After=network.target

[Service]
Type=simple
User=<ваш_пользователь>
WorkingDirectory=/path/to/FelixPartsBot/felix_hub/bot
Environment="PATH=/path/to/FelixPartsBot/felix_hub/bot/venv/bin"
ExecStart=/path/to/FelixPartsBot/felix_hub/bot/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Запуск сервисов
```bash
sudo systemctl daemon-reload
sudo systemctl enable felix-backend felix-bot
sudo systemctl start felix-backend felix-bot
sudo systemctl status felix-backend felix-bot
```

### Настройка NGINX (reverse proxy)

Создайте файл `/etc/nginx/sites-available/felix-hub`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/FelixPartsBot/felix_hub/backend/static;
        expires 30d;
    }
}
```

Активируйте конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/felix-hub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Настройка HTTPS с Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Certbot автоматически настроит HTTPS и обновит конфигурацию NGINX.

### Настройка firewall

```bash
# Разрешить HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Закрыть прямой доступ к Flask (только через NGINX)
sudo ufw deny 5000/tcp
sudo ufw enable
```

## Шаг 8: Мониторинг

### Просмотр логов

```bash
# Backend логи
tail -f /path/to/FelixPartsBot/felix_hub/backend/felix_hub.log

# Systemd логи
sudo journalctl -u felix-backend -f
sudo journalctl -u felix-bot -f
```

### Проверка статуса сервисов

```bash
sudo systemctl status felix-backend
sudo systemctl status felix-bot
```

## Резервное копирование

### База данных SQLite
```bash
# Создать резервную копию
cp felix_hub/backend/felix_hub.db felix_hub/backend/felix_hub.db.backup

# Автоматическое резервное копирование (cron)
# Добавьте в crontab (crontab -e):
0 2 * * * cp /path/to/felix_hub.db /path/to/backups/felix_hub_$(date +\%Y\%m\%d).db
```

### База данных PostgreSQL
```bash
# Создать резервную копию
pg_dump -U felix_user felix_hub > felix_hub_backup.sql

# Восстановление
psql -U felix_user felix_hub < felix_hub_backup.sql
```

## Обновление системы

```bash
# Остановите сервисы
sudo systemctl stop felix-backend felix-bot

# Получите обновления
cd /path/to/FelixPartsBot
git pull

# Обновите зависимости
cd felix_hub/backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

cd ../bot
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запустите сервисы
sudo systemctl start felix-backend felix-bot
```

## Безопасность

1. **Измените FLASK_SECRET_KEY** - используйте длинную случайную строку:
```python
import secrets
print(secrets.token_hex(32))
```

2. **Защитите .env файлы**:
```bash
chmod 600 backend/.env bot/.env
```

3. **Ограничьте доступ к админ-панели** через NGINX basic auth или встроенную авторизацию

4. **Регулярно обновляйте зависимости**:
```bash
pip list --outdated
pip install --upgrade <package>
```

5. **Настройте регулярные резервные копии базы данных**

## Поддержка

Если возникают проблемы, смотрите [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

Для дополнительной информации о функциях системы:
- Backend API: `felix_hub/backend/API_DOCUMENTATION.md`
- Admin Panel: `felix_hub/backend/ADMIN_PANEL_GUIDE.md`
- Printer Setup: `felix_hub/backend/PRINTER_README.md`
- Notifications: `felix_hub/backend/NOTIFICATION_SYSTEM.md`
