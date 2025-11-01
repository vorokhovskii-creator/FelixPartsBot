"""
API Contract Tests for Custom Parts
Tests the custom parts functionality for orders.
"""

import sys
import os
import tempfile
import json

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'felix_hub', 'backend'))

os.environ.setdefault('ENABLE_CAR_NUMBER', 'true')


def test_create_order_with_custom_parts():
    """Test creating an order with custom parts"""
    from app import app, db
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        client = app.test_client()
        
        # Create order with custom parts
        response = client.post('/api/orders', 
            data=json.dumps({
                'mechanic_name': 'Test Mechanic',
                'telegram_id': '123456789',
                'category': 'Тормоза',
                'carNumber': 'AB1234CD',
                'parts': [
                    {
                        'name': 'Standard Part',
                        'quantity': 1,
                        'isCustom': False
                    },
                    {
                        'name': 'Custom Part',
                        'quantity': 2,
                        'price': 150.50,
                        'note': 'Part Number: ABC123',
                        'isCustom': True
                    }
                ],
                'is_original': False
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = json.loads(response.data)
        
        assert 'id' in data, "Response should include order ID"
        assert 'parts' in data or 'selected_parts' in data, "Response should include parts"
        
        # Verify the order
        order_id = data['id']
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200
        
        order_data = json.loads(response.data)
        parts = order_data.get('parts', [])
        
        # Check that custom parts are included
        custom_parts = [p for p in parts if p.get('isCustom')]
        assert len(custom_parts) >= 1, "Should have at least one custom part"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_create_order_with_custom_parts passed")


def test_add_custom_part_to_order():
    """Test adding a custom part to an existing order - direct DB"""
    # Note: The mechanic API requires proper authentication which is tested separately
    # This test verifies the CustomPartItem model and its relationship with Order
    from app import app, db
    from models import Order, CustomPartItem, Mechanic
    from werkzeug.security import generate_password_hash
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create a mechanic
        mechanic = Mechanic(
            email='mechanic@test.com',
            password_hash=generate_password_hash('password123'),
            name='Test Mechanic'
        )
        db.session.add(mechanic)
        db.session.commit()
        
        client = app.test_client()
        
        # Create an order
        response = client.post('/api/orders', 
            data=json.dumps({
                'mechanic_name': 'Test Mechanic',
                'telegram_id': '123456789',
                'category': 'Тормоза',
                'carNumber': 'AB1234CD',
                'selected_parts': ['Standard Part']
            }),
            content_type='application/json'
        )
        
        order_id = json.loads(response.data)['id']
        
        # Add custom part directly to database (simulating what the API would do)
        order = Order.query.get(order_id)
        custom_part = CustomPartItem(
            order_id=order.id,
            name='Custom Brake Pad',
            part_number='BP-2024-001',
            price=200.00,
            quantity=2,
            added_by_id=mechanic.id
        )
        db.session.add(custom_part)
        db.session.commit()
        
        # Verify the custom part was added
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        order_data = json.loads(response.data)
        parts = order_data.get('parts', [])
        
        # Should have standard part + custom part
        assert len(parts) >= 2, f"Expected at least 2 parts, got {len(parts)}"
        
        custom_parts = [p for p in parts if p.get('isCustom') or p.get('customPartId')]
        assert len(custom_parts) >= 1, "Should have at least one custom part"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_add_custom_part_to_order passed")


def test_custom_parts_in_order_list():
    """Test that custom parts are included in order list"""
    from app import app, db
    from models import Order, CustomPartItem, Mechanic
    from werkzeug.security import generate_password_hash
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create a mechanic
        mechanic = Mechanic(
            email='mechanic@test.com',
            password_hash=generate_password_hash('password123'),
            name='Test Mechanic'
        )
        db.session.add(mechanic)
        db.session.commit()
        
        # Create an order
        order = Order(
            mechanic_name='Test Mechanic',
            telegram_id='123456789',
            category='Тормоза',
            car_number='AB1234CD',
            selected_parts=[{'name': 'Standard Part', 'quantity': 1}],
            is_original=False
        )
        db.session.add(order)
        db.session.flush()
        
        # Add custom part
        custom_part = CustomPartItem(
            order_id=order.id,
            name='Custom Part',
            part_number='CP-001',
            price=100.0,
            quantity=1,
            added_by_id=mechanic.id
        )
        db.session.add(custom_part)
        db.session.commit()
        
        client = app.test_client()
        
        # Get order details
        response = client.get(f'/api/orders/{order.id}')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        
        # Check that parts include custom parts
        parts = data.get('parts', [])
        assert len(parts) >= 2, f"Expected at least 2 parts (standard + custom), got {len(parts)}"
        
        custom_parts = [p for p in parts if p.get('isCustom') or p.get('customPartId')]
        assert len(custom_parts) >= 1, "Should include custom parts"
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)
    print("✅ test_custom_parts_in_order_list passed")


def run_all_tests():
    """Run all custom parts API tests"""
    print("\n" + "=" * 60)
    print("Running Custom Parts API Contract Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_create_order_with_custom_parts,
        test_add_custom_part_to_order,
        test_custom_parts_in_order_list
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
