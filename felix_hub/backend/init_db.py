import os
import sys

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Order, Category, Part

def init_database():
    """Создать таблицы и заполнить начальными данными"""
    with app.app_context():
        # Создать все таблицы
        db.create_all()
        print("✅ Таблицы созданы")
        
        # Проверить, есть ли уже данные
        if Category.query.count() == 0:
            # Добавить базовые категории
            categories = [
                Category(name_ru="Тормоза", name_he="בלמים", name_en="Brakes", icon="🔧", sort_order=1),
                Category(name_ru="Двигатель", name_he="מנוע", name_en="Engine", icon="⚙️", sort_order=2),
                Category(name_ru="Подвеска", name_he="מתלים", name_en="Suspension", icon="🔩", sort_order=3),
                Category(name_ru="Электрика", name_he="חשמל", name_en="Electrical", icon="⚡", sort_order=4),
                Category(name_ru="Расходники", name_he="חומרים מתכלים", name_en="Consumables", icon="💧", sort_order=5),
            ]
            for cat in categories:
                db.session.add(cat)
            db.session.commit()
            print("✅ Добавлены базовые категории")
        
        print("✅ База данных готова!")

if __name__ == '__main__':
    init_database()
