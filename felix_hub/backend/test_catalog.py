#!/usr/bin/env python3
"""
Test script for catalog CRUD functionality
"""

import sys
import json
from app import app, db
from models import Category, Part

def test_categories_api():
    """Test categories API endpoints"""
    print("Testing Categories API...")
    with app.app_context():
        client = app.test_client()
        
        # GET all categories
        response = client.get('/api/categories')
        assert response.status_code == 200
        categories = json.loads(response.data)
        assert len(categories) > 0
        print(f"✅ GET /api/categories - {len(categories)} categories")
        
        # GET single category
        cat_id = categories[0]['id']
        response = client.get(f'/api/categories/{cat_id}')
        assert response.status_code == 200
        print(f"✅ GET /api/categories/{cat_id}")
        
        # POST new category
        new_cat = {
            'name_ru': 'Тест категория',
            'name_he': 'קטגוריית מבחן',
            'name_en': 'Test category',
            'icon': '🧪',
            'sort_order': 100
        }
        response = client.post('/api/categories', 
                              json=new_cat,
                              content_type='application/json')
        assert response.status_code == 201
        created_cat = json.loads(response.data)
        print(f"✅ POST /api/categories - Created ID {created_cat['id']}")
        
        # PATCH category
        update_data = {'name_ru': 'Обновленная категория'}
        response = client.patch(f'/api/categories/{created_cat["id"]}',
                               json=update_data,
                               content_type='application/json')
        assert response.status_code == 200
        print(f"✅ PATCH /api/categories/{created_cat['id']}")
        
        # DELETE category
        response = client.delete(f'/api/categories/{created_cat["id"]}')
        assert response.status_code == 204
        print(f"✅ DELETE /api/categories/{created_cat['id']}")


def test_parts_api():
    """Test parts API endpoints"""
    print("\nTesting Parts API...")
    with app.app_context():
        client = app.test_client()
        
        # Get a category to work with
        response = client.get('/api/categories')
        categories = json.loads(response.data)
        cat_id = categories[0]['id']
        
        # GET all parts for category
        response = client.get(f'/api/parts?category_id={cat_id}')
        assert response.status_code == 200
        parts = json.loads(response.data)
        print(f"✅ GET /api/parts?category_id={cat_id} - {len(parts)} parts")
        
        # GET single part
        if parts:
            part_id = parts[0]['id']
            response = client.get(f'/api/parts/{part_id}')
            assert response.status_code == 200
            print(f"✅ GET /api/parts/{part_id}")
        
        # POST new part
        new_part = {
            'category_id': cat_id,
            'name_ru': 'Тестовая деталь',
            'name_he': 'חלק מבחן',
            'name_en': 'Test part',
            'is_common': True,
            'sort_order': 100
        }
        response = client.post('/api/parts',
                              json=new_part,
                              content_type='application/json')
        assert response.status_code == 201
        created_part = json.loads(response.data)
        print(f"✅ POST /api/parts - Created ID {created_part['id']}")
        
        # PATCH part
        update_data = {'name_ru': 'Обновленная деталь', 'is_common': False}
        response = client.patch(f'/api/parts/{created_part["id"]}',
                               json=update_data,
                               content_type='application/json')
        assert response.status_code == 200
        print(f"✅ PATCH /api/parts/{created_part['id']}")
        
        # DELETE part
        response = client.delete(f'/api/parts/{created_part["id"]}')
        assert response.status_code == 204
        print(f"✅ DELETE /api/parts/{created_part['id']}")


def test_routes():
    """Test page routes"""
    print("\nTesting Routes...")
    with app.app_context():
        client = app.test_client()
        
        # Test admin page
        response = client.get('/admin')
        assert response.status_code == 200
        print("✅ GET /admin")
        
        # Test catalog page
        response = client.get('/catalog')
        assert response.status_code == 200
        print("✅ GET /catalog")


def test_database_models():
    """Test database models"""
    print("\nTesting Database Models...")
    with app.app_context():
        # Count categories
        cat_count = Category.query.count()
        print(f"✅ Database has {cat_count} categories")
        
        # Count parts
        part_count = Part.query.count()
        print(f"✅ Database has {part_count} parts")
        
        # Test relationship
        first_cat = Category.query.first()
        if first_cat:
            parts_in_cat = len(first_cat.parts)
            print(f"✅ First category '{first_cat.name_ru}' has {parts_in_cat} parts")


if __name__ == '__main__':
    try:
        test_database_models()
        test_categories_api()
        test_parts_api()
        test_routes()
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
