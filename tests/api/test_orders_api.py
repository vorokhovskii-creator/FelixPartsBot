"""
API Contract Tests for Orders
Tests the create, list, and status update endpoints for orders.
"""

import sys
import os
import tempfile
import json

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'felix_hub', 'backend'))

# Set environment variables before importing app
os.environ.setdefault('ENABLE_CAR_NUMBER', 'true')
os.environ.setdefault('ALLOW_ANY_CAR_NUMBER', 'false')


def test_create_order():
    """Test POST /api/orders - Create a new order"""
    from app import app, db
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        client = app.test_client()
        
        # Test creating order with car number
        response = client.post('/api/orders', 
            data=json.dumps({
                'mechanic_name': 'Test Mechanic',
                'telegram_id': '123456789',
                'category': 'Тормоза',
                'carNumber': 'AB1234CD',
                'selected_parts': ['Передние колодки', 'Диски передние'],
                'is_original': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.data}"
        data = json.loads(response.data)
        
        assert 'id' in data, "Response should include order ID"
        assert data['carNumber'] == 'AB1234CD', f"Expected carNumber AB1234CD, got {data.get('carNumber')}"
        assert data['mechanic_name'] == 'Test Mechanic'
        assert data['status'] == 'новый'
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_create_order passed")


def test_list_orders():
    """Test GET /api/orders - List all orders"""
    from app import app, db
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        client = app.test_client()
        
        # Create multiple orders
        for i in range(3):
            client.post('/api/orders', 
                data=json.dumps({
                    'mechanic_name': f'Mechanic {i}',
                    'telegram_id': f'12345678{i}',
                    'category': 'Тормоза',
                    'carNumber': f'AB{i}234CD',
                    'selected_parts': ['Test Part']
                }),
                content_type='application/json'
            )
        
        # List all orders
        response = client.get('/api/orders')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        
        assert len(data) == 3, f"Expected 3 orders, got {len(data)}"
        assert all('id' in order for order in data), "All orders should have an ID"
        assert all('carNumber' in order for order in data), "All orders should have carNumber"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_list_orders passed")


def test_update_order_status():
    """Test PATCH /api/orders/:id - Update order status"""
    from app import app, db
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        client = app.test_client()
        
        # Create an order
        response = client.post('/api/orders', 
            data=json.dumps({
                'mechanic_name': 'Test Mechanic',
                'telegram_id': '123456789',
                'category': 'Тормоза',
                'carNumber': 'AB1234CD',
                'selected_parts': ['Test Part']
            }),
            content_type='application/json'
        )
        
        order_id = json.loads(response.data)['id']
        
        # Update status
        response = client.patch(f'/api/orders/{order_id}',
            data=json.dumps({'status': 'готов'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        
        assert data['status'] == 'готов', f"Expected status 'готов', got {data['status']}"
        assert data['id'] == order_id
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_update_order_status passed")


def test_order_validation():
    """Test order validation rules"""
    from app import app, db
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        client = app.test_client()
        
        # Test invalid car number (too short)
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Test',
                'telegram_id': '123',
                'category': 'Test',
                'carNumber': 'AB1',
                'selected_parts': ['Part1']
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid car number, got {response.status_code}"
        
        # Test empty parts
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Test',
                'telegram_id': '123',
                'category': 'Test',
                'carNumber': 'AB1234CD',
                'selected_parts': []
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400, f"Expected 400 for empty parts, got {response.status_code}"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_order_validation passed")


def run_all_tests():
    """Run all order API tests"""
    print("\n" + "=" * 60)
    print("Running Order API Contract Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_create_order,
        test_list_orders,
        test_update_order_status,
        test_order_validation
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
