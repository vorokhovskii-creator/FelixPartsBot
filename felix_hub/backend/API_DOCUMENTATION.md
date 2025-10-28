# Felix Hub Backend - API Documentation

## Overview
Flask REST API для управления заказами запчастей с поддержкой CRUD операций, фильтрации и валидации.

## Технологический стек
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-CORS 4.0.0
- SQLite база данных

## Установка и запуск

### 1. Установка зависимостей
```bash
cd felix_hub/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Настройка окружения
Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
FLASK_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///database.db
```

### 3. Запуск сервера
```bash
python app.py
```

Сервер запустится на `http://0.0.0.0:5000`

### 4. Запуск тестов
```bash
python test_api.py
python test_filters.py
python test_comprehensive.py
```

## API Endpoints

### 1. Создание заказа
**POST /api/orders**

Создает новый заказ от Telegram-бота.

**Request Body:**
```json
{
  "mechanic_name": "David",
  "telegram_id": "12345678",
  "category": "Тормоза",
  "vin": "4T1BE32K",
  "selected_parts": ["Передние колодки", "Диски передние"],
  "is_original": false,
  "photo_url": "https://api.telegram.org/file/..."
}
```

**Валидация:**
- `mechanic_name`, `telegram_id`, `category`, `vin`, `selected_parts` - обязательные поля
- `selected_parts` - должен быть непустым массивом
- `vin` - минимум 4 символа
- `is_original` - опциональное, по умолчанию `false`
- `photo_url` - опциональное

**Response:** `201 Created`
```json
{
  "id": 1,
  "mechanic_name": "David",
  "telegram_id": "12345678",
  "category": "Тормоза",
  "vin": "4T1BE32K",
  "selected_parts": ["Передние колодки", "Диски передние"],
  "is_original": false,
  "photo_url": "https://api.telegram.org/file/...",
  "status": "новый",
  "printed": false,
  "created_at": "2025-01-01T12:00:00.000000"
}
```

### 2. Получение списка заказов
**GET /api/orders**

Получает список заказов с поддержкой фильтрации и пагинации.

**Query параметры:**
- `status` - фильтр по статусу (новый, в работе, готов, выдан)
- `mechanic` - фильтр по имени механика
- `telegram_id` - фильтр по telegram_id
- `limit` - количество записей (по умолчанию 50)
- `offset` - смещение для пагинации (по умолчанию 0)

**Примеры:**
```
GET /api/orders
GET /api/orders?status=новый
GET /api/orders?mechanic=David
GET /api/orders?telegram_id=12345678
GET /api/orders?limit=10&offset=20
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "mechanic_name": "David",
    "telegram_id": "12345678",
    "category": "Тормоза",
    "vin": "4T1BE32K",
    "selected_parts": ["Передние колодки", "Диски передние"],
    "is_original": false,
    "photo_url": "https://api.telegram.org/file/...",
    "status": "новый",
    "printed": false,
    "created_at": "2025-01-01T12:00:00.000000"
  }
]
```

### 3. Получение заказа по ID
**GET /api/orders/<id>**

Получает конкретный заказ по его ID.

**Response:** 
- `200 OK` - заказ найден
- `404 Not Found` - заказ не найден

### 4. Обновление заказа
**PATCH /api/orders/<id>**

Обновляет поля заказа (чаще всего статус).

**Request Body (все поля опциональны):**
```json
{
  "status": "готов",
  "printed": true,
  "mechanic_name": "John",
  "category": "Двигатель",
  "vin": "NEW_VIN",
  "selected_parts": ["Новые запчасти"],
  "is_original": true,
  "photo_url": "new_url"
}
```

**Response:** 
- `200 OK` - обновленный заказ
- `404 Not Found` - заказ не найден

### 5. Удаление заказа
**DELETE /api/orders/<id>**

Удаляет заказ из базы данных.

**Response:** 
- `204 No Content` - успешно удален
- `404 Not Found` - заказ не найден

### 6. Печать чека
**POST /api/orders/<id>/print**

Инициирует печать чека для заказа (на данном этапе - заглушка).

**Response:** `200 OK`
```json
{
  "message": "Печать инициирована",
  "order_id": 1
}
```

## Модель данных

### Order
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ (автоинкремент) |
| mechanic_name | String(120) | Имя механика |
| telegram_id | String(50) | Telegram ID пользователя |
| category | String(120) | Категория запчастей |
| vin | String(50) | VIN номер автомобиля |
| selected_parts | JSON | Массив выбранных запчастей |
| is_original | Boolean | Оригинальные/аналоговые запчасти |
| photo_url | String(250) | URL фотографии (опционально) |
| status | String(50) | Статус заказа (по умолчанию "новый") |
| printed | Boolean | Флаг печати чека (по умолчанию false) |
| created_at | DateTime | Время создания заказа |

### Возможные статусы
- `новый` - заказ только создан
- `в работе` - заказ в процессе обработки
- `готов` - запчасти готовы к выдаче
- `выдан` - заказ выдан клиенту

## Обработка ошибок

Все ошибки возвращаются в формате JSON:
```json
{
  "error": "Описание ошибки"
}
```

### HTTP статус коды
- `200 OK` - успешный запрос
- `201 Created` - ресурс создан
- `204 No Content` - успешное удаление
- `400 Bad Request` - невалидные данные
- `404 Not Found` - ресурс не найден
- `500 Internal Server Error` - внутренняя ошибка сервера

## Логирование

Приложение логирует важные операции:
- Создание заказа: `Order created: ID={id}, mechanic={name}`
- Обновление заказа: `Order updated: ID={id}, status={status}`
- Удаление заказа: `Order deleted: ID={id}`
- Инициация печати: `Print triggered for order: ID={id}`
- Ошибки: детальная информация об ошибках

## CORS

CORS настроен для всех origins (для разработки). В продакшене следует ограничить доступ к конкретным доменам.

## База данных

- По умолчанию используется SQLite
- База создается автоматически при первом запуске
- Путь к базе настраивается через `DATABASE_URL` в `.env`
- Поддерживается любая база данных, совместимая с SQLAlchemy

## Разработка

### Структура проекта
```
backend/
├── app.py                    # Основное приложение Flask
├── models.py                 # SQLAlchemy модели
├── requirements.txt          # Зависимости Python
├── .env.example             # Пример файла окружения
├── test_api.py              # Основные тесты API
├── test_filters.py          # Тесты фильтрации
├── test_comprehensive.py    # Комплексные тесты
└── API_DOCUMENTATION.md     # Документация API
```

### Тестирование
Все тесты используют изолированную тестовую базу данных и автоматически очищают данные после выполнения.

### Соглашения о коде
- Используются русские сообщения об ошибках для пользователей
- Snake_case для переменных и функций Python
- Логирование всех важных операций
- Обработка всех исключений с возвратом понятных ошибок
