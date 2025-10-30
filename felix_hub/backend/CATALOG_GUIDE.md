# Catalog Management System - Руководство

## Обзор

Система управления каталогом запчастей позволяет администраторам управлять категориями и деталями через веб-интерфейс вместо редактирования `config.py`.

## Возможности

### ✅ Реализовано

1. **База данных**
   - Модель `Category` с мультиязычными полями (RU/HE/EN)
   - Модель `Part` с мультиязычными полями (RU/HE/EN)
   - Связь один-ко-многим между категориями и деталями
   - Cascade удаление деталей при удалении категории

2. **REST API**
   - `GET /api/categories` - список всех категорий
   - `GET /api/categories/<id>` - получить категорию
   - `POST /api/categories` - создать категорию
   - `PATCH /api/categories/<id>` - обновить категорию
   - `DELETE /api/categories/<id>` - удалить категорию
   - `GET /api/parts?category_id=<id>` - список деталей
   - `GET /api/parts/<id>` - получить деталь
   - `POST /api/parts` - создать деталь
   - `PATCH /api/parts/<id>` - обновить деталь
   - `DELETE /api/parts/<id>` - удалить деталь

3. **Веб-интерфейс**
   - Страница `/catalog` для управления каталогом
   - Две колонки: категории слева, детали справа
   - Модальные окна для создания/редактирования
   - AJAX операции без перезагрузки страницы
   - Ссылка из админ-панели (`/admin` → `/catalog`)

4. **Интеграция с ботом**
   - Функции загрузки категорий из API
   - Функции загрузки деталей из API
   - Fallback на `config.py` если API недоступен
   - Поддержка мультиязычности

5. **Миграция данных**
   - Скрипт `migrate_catalog.py` для переноса данных из `config.py`
   - Включает переводы на иврит и английский

## Использование

### Первоначальная настройка

1. **Создать таблицы в БД:**
```bash
cd felix_hub/backend
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

2. **Запустить миграцию данных:**
```bash
python3 migrate_catalog.py
```

### Работа с веб-интерфейсом

1. Запустить Flask приложение:
```bash
python3 app.py
```

2. Открыть админ-панель: `http://localhost:5000/admin`
3. Нажать кнопку "📦 Каталог"
4. Управлять категориями и деталями через интерфейс

### API Примеры

**Создать категорию:**
```bash
curl -X POST http://localhost:5000/api/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name_ru": "Кузовные детали",
    "name_he": "חלקי מרכב",
    "name_en": "Body parts",
    "icon": "🚗",
    "sort_order": 10
  }'
```

**Создать деталь:**
```bash
curl -X POST http://localhost:5000/api/parts \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "name_ru": "Бампер передний",
    "name_he": "פגוש קדמי",
    "name_en": "Front bumper",
    "is_common": true,
    "sort_order": 0
  }'
```

**Получить детали категории:**
```bash
curl http://localhost:5000/api/parts?category_id=1
```

## Структура моделей

### Category
```python
{
    "id": 1,
    "name_ru": "Тормоза",
    "name_he": "בלמים",
    "name_en": "Brakes",
    "icon": "🔧",
    "sort_order": 0,
    "created_at": "2024-01-01T12:00:00"
}
```

### Part
```python
{
    "id": 1,
    "category_id": 1,
    "name_ru": "Передние колодки",
    "name_he": "רפידות קדמיות",
    "name_en": "Front pads",
    "is_common": true,
    "sort_order": 0,
    "created_at": "2024-01-01T12:00:00"
}
```

## Интеграция с ботом

Бот автоматически использует API для загрузки категорий и деталей:

```python
# В bot.py
categories = get_categories_dict()  # Загрузит из API или fallback на config.py
parts = get_parts_list(category_key, category_data, lang='ru')
```

Если backend недоступен, бот использует данные из `config.py`.

## Безопасность

- Валидация обязательных полей (`name_ru`)
- Проверка существования связанных сущностей
- Защита от удаления категорий со связанными заказами
- Логирование всех операций

## Тестирование

Запустить тесты:
```bash
cd felix_hub/backend
python3 test_catalog.py
```

Результат:
- ✅ CRUD операции для категорий
- ✅ CRUD операции для деталей
- ✅ Роуты `/admin` и `/catalog`
- ✅ Связи моделей в БД

## Troubleshooting

**Проблема:** Категории не загружаются в боте  
**Решение:** Убедитесь, что backend запущен и доступен по BACKEND_URL

**Проблема:** Ошибка при удалении категории  
**Решение:** Проверьте, нет ли связанных заказов с этой категорией

**Проблема:** Детали не отображаются  
**Решение:** Убедитесь, что `is_common=true` для деталей, которые должны быть в чек-листе

## Файлы

- `backend/models.py` - модели Category и Part
- `backend/app.py` - API endpoints
- `backend/templates/catalog.html` - UI
- `backend/static/catalog.js` - Frontend логика
- `backend/migrate_catalog.py` - миграция данных
- `bot/bot.py` - интеграция с API

## Дальнейшее развитие

Возможные улучшения:
- Массовое редактирование деталей
- Импорт/экспорт каталога в Excel
- История изменений
- Права доступа для разных пользователей
- Поиск по каталогу
