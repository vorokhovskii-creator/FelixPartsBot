import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Category, Part

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bot'))
from config import CATEGORIES

def migrate_catalog():
    """Перенести категории и детали из config.py в БД"""
    with app.app_context():
        if Category.query.count() > 0:
            print("⚠️  Данные уже существуют в базе данных")
            response = input("Продолжить и добавить новые данные? (y/n): ")
            if response.lower() != 'y':
                print("Миграция отменена")
                return
        
        print("🔄 Начинаем миграцию категорий и деталей...")
        
        for i, (cat_name, parts_list) in enumerate(CATEGORIES.items()):
            icon = '🔧'
            name_ru = cat_name
            
            if ' ' in cat_name:
                parts = cat_name.split(maxsplit=1)
                if len(parts[0]) <= 2:
                    icon = parts[0]
                    name_ru = parts[1]
            
            existing_cat = Category.query.filter_by(name_ru=name_ru).first()
            if existing_cat:
                print(f"⏭️  Категория '{name_ru}' уже существует, пропускаем...")
                category = existing_cat
            else:
                category = Category(
                    name_ru=name_ru,
                    icon=icon,
                    sort_order=i
                )
                db.session.add(category)
                db.session.flush()
                print(f"✅ Создана категория: {icon} {name_ru}")
            
            for j, part_name in enumerate(parts_list):
                existing_part = Part.query.filter_by(
                    category_id=category.id,
                    name_ru=part_name
                ).first()
                
                if existing_part:
                    print(f"   ⏭️  Деталь '{part_name}' уже существует, пропускаем...")
                    continue
                
                part = Part(
                    category_id=category.id,
                    name_ru=part_name,
                    is_common=True,
                    sort_order=j
                )
                db.session.add(part)
                print(f"   ✅ Добавлена деталь: {part_name}")
        
        db.session.commit()
        
        total_categories = Category.query.count()
        total_parts = Part.query.count()
        
        print("\n" + "="*50)
        print("🎉 Миграция завершена успешно!")
        print(f"📊 Всего категорий: {total_categories}")
        print(f"📊 Всего деталей: {total_parts}")
        print("="*50)

if __name__ == '__main__':
    migrate_catalog()
