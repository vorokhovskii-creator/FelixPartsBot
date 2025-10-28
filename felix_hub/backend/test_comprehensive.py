import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

def test_comprehensive():
    from app import app, db
    from models import Order
    import json
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        
        client = app.test_client()
        
        print("=" * 60)
        print("COMPREHENSIVE API TEST - Felix Hub Backend")
        print("=" * 60)
        
        print("\n1. Testing Order Creation (POST /api/orders)")
        print("-" * 60)
        order_data = {
            "mechanic_name": "David",
            "telegram_id": "12345678",
            "category": "Тормоза",
            "vin": "4T1BE32K",
            "selected_parts": ["Передние колодки", "Диски передние"],
            "is_original": False,
            "photo_url": "https://api.telegram.org/file/test.jpg"
        }
        response = client.post('/api/orders', 
            data=json.dumps(order_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        order = json.loads(response.data)
        print(f"✅ Order created successfully with ID: {order['id']}")
        print(f"   - Mechanic: {order['mechanic_name']}")
        print(f"   - Status: {order['status']}")
        print(f"   - Parts: {', '.join(order['selected_parts'])}")
        
        print("\n2. Testing Input Validation")
        print("-" * 60)
        
        print("   a. Testing missing required field...")
        response = client.post('/api/orders',
            data=json.dumps({'mechanic_name': 'Test'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        error = json.loads(response.data)
        print(f"   ✅ Validation working: {error['error']}")
        
        print("   b. Testing empty selected_parts...")
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Test',
                'telegram_id': '123',
                'category': 'Test',
                'vin': 'ABCD1234',
                'selected_parts': []
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        print("   ✅ Empty parts validation working")
        
        print("   c. Testing short VIN...")
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Test',
                'telegram_id': '123',
                'category': 'Test',
                'vin': 'ABC',
                'selected_parts': ['Part1']
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        print("   ✅ VIN length validation working")
        
        print("\n3. Testing Order Retrieval (GET /api/orders)")
        print("-" * 60)
        response = client.get('/api/orders')
        assert response.status_code == 200
        orders = json.loads(response.data)
        print(f"✅ Retrieved {len(orders)} order(s)")
        
        print("\n4. Testing Single Order Retrieval (GET /api/orders/<id>)")
        print("-" * 60)
        response = client.get(f'/api/orders/{order["id"]}')
        assert response.status_code == 200
        retrieved_order = json.loads(response.data)
        assert retrieved_order['id'] == order['id']
        print(f"✅ Retrieved order {order['id']} successfully")
        
        print("\n5. Testing Order Update (PATCH /api/orders/<id>)")
        print("-" * 60)
        response = client.patch(f'/api/orders/{order["id"]}',
            data=json.dumps({'status': 'в работе'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        updated_order = json.loads(response.data)
        assert updated_order['status'] == 'в работе'
        print(f"✅ Order status updated to: {updated_order['status']}")
        
        response = client.patch(f'/api/orders/{order["id"]}',
            data=json.dumps({'status': 'готов', 'printed': True}),
            content_type='application/json'
        )
        assert response.status_code == 200
        updated_order = json.loads(response.data)
        assert updated_order['status'] == 'готов'
        assert updated_order['printed'] == True
        print(f"✅ Order status updated to: {updated_order['status']}, printed: {updated_order['printed']}")
        
        print("\n6. Testing Print Endpoint (POST /api/orders/<id>/print)")
        print("-" * 60)
        response = client.post(f'/api/orders/{order["id"]}/print')
        assert response.status_code == 200
        result = json.loads(response.data)
        print(f"✅ Print endpoint triggered: {result['message']}")
        
        print("\n7. Testing Filtering and Pagination")
        print("-" * 60)
        
        for i in range(3):
            client.post('/api/orders',
                data=json.dumps({
                    'mechanic_name': 'John' if i % 2 == 0 else 'David',
                    'telegram_id': str(1000 + i),
                    'category': 'Двигатель',
                    'vin': f'VIN{i:04d}',
                    'selected_parts': ['Part1', 'Part2']
                }),
                content_type='application/json'
            )
        
        print("   a. Testing status filter...")
        response = client.get('/api/orders?status=новый')
        orders = json.loads(response.data)
        assert all(o['status'] == 'новый' for o in orders)
        print(f"   ✅ Status filter working: found {len(orders)} order(s) with status 'новый'")
        
        print("   b. Testing mechanic filter...")
        response = client.get('/api/orders?mechanic=David')
        orders = json.loads(response.data)
        assert all(o['mechanic_name'] == 'David' for o in orders)
        print(f"   ✅ Mechanic filter working: found {len(orders)} order(s) for David")
        
        print("   c. Testing limit parameter...")
        response = client.get('/api/orders?limit=2')
        orders = json.loads(response.data)
        assert len(orders) == 2
        print(f"   ✅ Limit parameter working: returned {len(orders)} order(s)")
        
        print("\n8. Testing Error Handling")
        print("-" * 60)
        
        print("   a. Testing 404 for non-existent order...")
        response = client.get('/api/orders/999999')
        assert response.status_code == 404
        error = json.loads(response.data)
        assert 'error' in error
        print(f"   ✅ 404 handler working: {error['error']}")
        
        print("   b. Testing invalid JSON...")
        response = client.post('/api/orders',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
        error = json.loads(response.data)
        assert 'error' in error
        print("   ✅ Invalid JSON handler working")
        
        print("\n9. Testing Order Deletion (DELETE /api/orders/<id>)")
        print("-" * 60)
        response = client.delete(f'/api/orders/{order["id"]}')
        assert response.status_code == 204
        print(f"✅ Order {order['id']} deleted successfully")
        
        response = client.get(f'/api/orders/{order["id"]}')
        assert response.status_code == 404
        print("✅ Verified order was deleted (404 returned)")
        
        print("\n" + "=" * 60)
        print("✅ ALL COMPREHENSIVE TESTS PASSED!")
        print("=" * 60)
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

if __name__ == '__main__':
    test_comprehensive()
