#!/usr/bin/env python3
"""
Test to verify that category deletion properly checks for orders
with categories stored as "🔧 Двигатель" (with emoji).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Category, Part, Order

def test_category_deletion_with_emoji():
    """Test that deletion check works for both category formats"""
    with app.app_context():
        # Clean up
        db.drop_all()
        db.create_all()
        
        # Create a category
        category = Category(
            name_ru='Двигатель',
            icon='🔧',
            sort_order=0
        )
        db.session.add(category)
        db.session.commit()
        
        print(f"✅ Created category: ID={category.id}, name_ru='{category.name_ru}', icon='{category.icon}'")
        
        # Test 1: Delete without orders should succeed
        response = app.test_client().delete(f'/api/categories/{category.id}')
        if response.status_code == 204:
            print("✅ Test 1 passed: Can delete category without orders")
        else:
            print(f"❌ Test 1 failed: Expected 204, got {response.status_code}")
            return False
        
        # Recreate category
        category = Category(
            name_ru='Двигатель',
            icon='🔧',
            sort_order=0
        )
        db.session.add(category)
        db.session.commit()
        
        # Test 2: Create order with category name WITHOUT emoji
        order1 = Order(
            mechanic_name='Test Mechanic',
            telegram_id='12345',
            category='Двигатель',  # Without emoji
            vin='TEST123',
            selected_parts=['Часть 1']
        )
        db.session.add(order1)
        db.session.commit()
        
        print(f"✅ Created order with category='Двигатель' (no emoji)")
        
        # Try to delete - should be blocked
        response = app.test_client().delete(f'/api/categories/{category.id}')
        if response.status_code == 400:
            print("✅ Test 2 passed: Cannot delete category with orders (no emoji)")
        else:
            print(f"❌ Test 2 failed: Expected 400, got {response.status_code}")
            return False
        
        # Clean up order
        db.session.delete(order1)
        db.session.commit()
        
        # Test 3: Create order with category name WITH emoji (as bot stores it)
        order2 = Order(
            mechanic_name='Test Mechanic',
            telegram_id='12345',
            category='🔧 Двигатель',  # With emoji - as bot stores it
            vin='TEST456',
            selected_parts=['Часть 2']
        )
        db.session.add(order2)
        db.session.commit()
        
        print(f"✅ Created order with category='🔧 Двигатель' (with emoji)")
        
        # Try to delete - should be blocked
        response = app.test_client().delete(f'/api/categories/{category.id}')
        if response.status_code == 400:
            data = response.get_json()
            print(f"✅ Test 3 passed: Cannot delete category with orders (with emoji)")
            print(f"   Error message: {data.get('error')}")
        else:
            print(f"❌ Test 3 failed: Expected 400, got {response.status_code}")
            return False
        
        # Clean up
        db.session.delete(order2)
        db.session.delete(category)
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        return True

if __name__ == '__main__':
    success = test_category_deletion_with_emoji()
    sys.exit(0 if success else 1)
