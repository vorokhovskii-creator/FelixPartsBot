"""
API Contract Tests for Categories
Tests the categories and parts catalog endpoints.
"""

import sys
import os
import tempfile
import json

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'felix_hub', 'backend'))


def test_list_categories():
    """Test GET /api/categories - List all categories"""
    from app import app, db
    from models import Category
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create test categories
        cat1 = Category(name_ru='Тормоза', name_en='Brakes', icon='🔧', sort_order=1)
        cat2 = Category(name_ru='Двигатель', name_en='Engine', icon='⚙️', sort_order=2)
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.commit()
        
        client = app.test_client()
        
        response = client.get('/api/categories')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        
        assert len(data) >= 2, f"Expected at least 2 categories, got {len(data)}"
        assert all('id' in cat for cat in data), "All categories should have an ID"
        assert all('name_ru' in cat for cat in data), "All categories should have name_ru"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_list_categories passed")


def test_list_parts_by_category():
    """Test GET /api/parts?category_id=:id - List parts for a category"""
    from app import app, db
    from models import Category, Part
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create a category with parts
        category = Category(name_ru='Тормоза', icon='🔧')
        db.session.add(category)
        db.session.flush()
        
        part1 = Part(category_id=category.id, name_ru='Передние колодки', name_en='Front pads')
        part2 = Part(category_id=category.id, name_ru='Задние колодки', name_en='Rear pads')
        db.session.add(part1)
        db.session.add(part2)
        db.session.commit()
        
        client = app.test_client()
        
        # Get all parts and filter by category
        response = client.get('/api/parts')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        
        # Filter parts by category_id
        category_parts = [p for p in data if p.get('category_id') == category.id]
        
        assert len(category_parts) == 2, f"Expected 2 parts for category, got {len(category_parts)}"
        assert all('id' in part for part in category_parts), "All parts should have an ID"
        assert all('name_ru' in part for part in category_parts), "All parts should have name_ru"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_list_parts_by_category passed")


def test_get_all_parts():
    """Test GET /api/parts - List all parts"""
    from app import app, db
    from models import Category, Part
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create categories with parts
        cat1 = Category(name_ru='Тормоза', icon='🔧')
        db.session.add(cat1)
        db.session.flush()
        
        part1 = Part(category_id=cat1.id, name_ru='Передние колодки')
        part2 = Part(category_id=cat1.id, name_ru='Задние колодки')
        db.session.add(part1)
        db.session.add(part2)
        db.session.commit()
        
        client = app.test_client()
        
        response = client.get('/api/parts')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        
        assert len(data) >= 2, f"Expected at least 2 parts, got {len(data)}"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_get_all_parts passed")


def run_all_tests():
    """Run all category API tests"""
    print("\n" + "=" * 60)
    print("Running Category API Contract Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_list_categories,
        test_list_parts_by_category,
        test_get_all_parts
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ {test.__name__} failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
