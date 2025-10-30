import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or os.getenv('BOT_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

# Admin IDs configuration
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Validate required configuration
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN not found in environment variables")

# Keep backward compatibility
BOT_TOKEN = TELEGRAM_TOKEN

CATEGORIES = {
    "🔧 Тормоза": [
        "Передние колодки",
        "Задние колодки",
        "Диски передние",
        "Диски задние",
        "Тормозная жидкость",
        "Суппорт передний",
        "Суппорт задний"
    ],
    "⚙️ Двигатель": [
        "Масло моторное",
        "Масляный фильтр",
        "Воздушный фильтр",
        "Свечи зажигания",
        "Ремень ГРМ",
        "Помпа",
        "Термостат"
    ],
    "🔩 Подвеска": [
        "Амортизаторы передние",
        "Амортизаторы задние",
        "Стойки",
        "Рычаги передние",
        "Сайлентблоки",
        "Шаровые опоры",
        "Стойки стабилизатора"
    ],
    "⚡ Электрика": [
        "Аккумулятор",
        "Генератор",
        "Стартер",
        "Проводка",
        "Предохранители",
        "Датчики",
        "Лампы"
    ],
    "💧 Расходники": [
        "Фильтр салона",
        "Щетки стеклоочистителя",
        "Антифриз",
        "Омывающая жидкость",
        "Тормозная жидкость",
        "Масло трансмиссионное"
    ]
}

CATEGORY, PARTS_SELECTION, VIN_INPUT, ORIGINAL_CHOICE, PHOTO_UPLOAD, CONFIRMATION = range(6)
