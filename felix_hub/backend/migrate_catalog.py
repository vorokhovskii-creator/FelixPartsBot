#!/usr/bin/env python3
"""
Migration script to transfer catalog data from config.py to database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Category, Part

# Import categories from bot config
bot_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bot')
sys.path.insert(0, bot_path)

try:
    from config import CATEGORIES
except ImportError:
    print("Could not import CATEGORIES from bot/config.py")
    CATEGORIES = {}

TRANSLATIONS = {
    "🔧 Тормоза": {
        "he": "בלמים",
        "en": "Brakes",
        "parts": {
            "Передние колодки": {"he": "רפידות קדמיות", "en": "Front pads"},
            "Задние колодки": {"he": "רפידות אחוריות", "en": "Rear pads"},
            "Диски передние": {"he": "דיסקים קדמיים", "en": "Front discs"},
            "Диски задние": {"he": "דיסקים אחוריים", "en": "Rear discs"},
            "Тормозная жидкость": {"he": "נוזל בלמים", "en": "Brake fluid"},
            "Суппорт передний": {"he": "קליפר קדמי", "en": "Front caliper"},
            "Суппорт задний": {"he": "קליפר אחורי", "en": "Rear caliper"}
        }
    },
    "⚙️ Двигатель": {
        "he": "מנוע",
        "en": "Engine",
        "parts": {
            "Масло моторное": {"he": "שמן מנוע", "en": "Engine oil"},
            "Масляный фильтр": {"he": "מסנן שמן", "en": "Oil filter"},
            "Воздушный фильтр": {"he": "מסנן אוויר", "en": "Air filter"},
            "Свечи зажигания": {"he": "מצתים", "en": "Spark plugs"},
            "Ремень ГРМ": {"he": "רצועת תזמון", "en": "Timing belt"},
            "Помпа": {"he": "משאבת מים", "en": "Water pump"},
            "Термостат": {"he": "תרמוסטט", "en": "Thermostat"}
        }
    },
    "🔩 Подвеска": {
        "he": "מתלים",
        "en": "Suspension",
        "parts": {
            "Амортизаторы передние": {"he": "בולמי זעזועים קדמיים", "en": "Front shock absorbers"},
            "Амортизаторы задние": {"he": "בולמי זעזועים אחוריים", "en": "Rear shock absorbers"},
            "Стойки": {"he": "עמודי תמיכה", "en": "Struts"},
            "Рычаги передние": {"he": "זרועות קדמיות", "en": "Front arms"},
            "Сайлентблоки": {"he": "סיילנטבלוקים", "en": "Silent blocks"},
            "Шаровые опоры": {"he": "פיקות כדוריות", "en": "Ball joints"},
            "Стойки стабилизатора": {"he": "מוטות יציבות", "en": "Stabilizer bars"}
        }
    },
    "⚡ Электрика": {
        "he": "חשמל",
        "en": "Electrics",
        "parts": {
            "Аккумулятор": {"he": "מצבר", "en": "Battery"},
            "Генератор": {"he": "גנרטור", "en": "Alternator"},
            "Стартер": {"he": "מתנע", "en": "Starter"},
            "Проводка": {"he": "חיווט", "en": "Wiring"},
            "Предохранители": {"he": "נתיכים", "en": "Fuses"},
            "Датчики": {"he": "חיישנים", "en": "Sensors"},
            "Лампы": {"he": "נורות", "en": "Bulbs"}
        }
    },
    "💧 Расходники": {
        "he": "מתכלים",
        "en": "Consumables",
        "parts": {
            "Фильтр салона": {"he": "מסנן תא נוסעים", "en": "Cabin filter"},
            "Щетки стеклоочистителя": {"he": "מגבי שמשה", "en": "Wiper blades"},
            "Антифриз": {"he": "נוזל קירור", "en": "Antifreeze"},
            "Омывающая жидкость": {"he": "מי שמשה", "en": "Washer fluid"},
            "Тормозная жидкость": {"he": "נוזל בלמים", "en": "Brake fluid"},
            "Масло трансмиссионное": {"he": "שמן תיבת הילוכים", "en": "Transmission oil"}
        }
    }
}


def migrate_catalog():
    """Migrate catalog data from config.py to database"""
    
    with app.app_context():
        print("Starting catalog migration...")
        
        # Check if data already exists
        existing_categories = Category.query.count()
        if existing_categories > 0:
            response = input(f"Database already has {existing_categories} categories. Continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Migration cancelled.")
                return
        
        # Create categories and parts
        category_count = 0
        part_count = 0
        
        for category_name, parts_list in CATEGORIES.items():
            # Extract icon from category name
            icon = category_name.split()[0] if category_name.split() else '🔧'
            name_ru = category_name.replace(icon, '').strip()
            
            # Get translations
            translations = TRANSLATIONS.get(category_name, {})
            name_he = translations.get('he')
            name_en = translations.get('en')
            
            # Create category
            category = Category(
                name_ru=name_ru,
                name_he=name_he,
                name_en=name_en,
                icon=icon,
                sort_order=category_count
            )
            db.session.add(category)
            db.session.flush()  # Get category ID
            
            print(f"Created category: {icon} {name_ru}")
            category_count += 1
            
            # Create parts
            part_translations = translations.get('parts', {})
            for i, part_name in enumerate(parts_list):
                part_trans = part_translations.get(part_name, {})
                
                part = Part(
                    category_id=category.id,
                    name_ru=part_name,
                    name_he=part_trans.get('he'),
                    name_en=part_trans.get('en'),
                    is_common=True,
                    sort_order=i
                )
                db.session.add(part)
                part_count += 1
                print(f"  - Created part: {part_name}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Migration completed successfully!")
        print(f"Created {category_count} categories and {part_count} parts")


if __name__ == '__main__':
    migrate_catalog()
