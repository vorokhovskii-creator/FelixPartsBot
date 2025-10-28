# Felix Hub Backend

Flask-сервер для управления заказами запчастей.

## Установка
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env файл
```

## Запуск
```bash
python app.py
```

## API Endpoints
- `POST /api/orders` - создать заказ
- `GET /api/orders` - список заказов
- `PATCH /api/orders/<id>` - изменить статус
- `DELETE /api/orders/<id>` - удалить заказ
- `POST /api/orders/<id>/print` - печать чека
- `GET /export` - экспорт в Excel
- `GET /admin` - админ-панель
