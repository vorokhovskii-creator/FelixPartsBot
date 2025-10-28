# Felix Hub System

Автономная система управления заказами запчастей для СТО Felix.

## Компоненты
- **Telegram Bot** - интерфейс механика для создания заказов
- **Flask Backend** - API, база данных, админ-панель
- **Notification System** - уведомления механикам через Telegram
- **Print System** - автоматическая печать чеков на термопринтере

## Технологии
- Python 3.10+
- Flask + SQLAlchemy
- python-telegram-bot v21.x
- python-escpos
- SQLite (позже PostgreSQL)

## Структура
- `/bot` - Telegram-бот механика
- `/backend` - Flask-сервер с API и админ-панелью

## Установка
См. README.md в каждой папке для инструкций.
