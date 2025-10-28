import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

def test_api():
    from app import app, db
    from models import Order
    import json
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        
        client = app.test_client()
        
        print("Testing POST /api/orders...")
        response = client.post('/api/orders', 
            data=json.dumps({
                'mechanic_name': 'David',
                'telegram_id': '12345678',
                'category': 'Тормоза',
                'vin': '4T1BE32K',
                'selected_parts': ['Передние колодки', 'Диски передние'],
                'is_original': False,
                'photo_url': 'https://api.telegram.org/file/test.jpg'
            }),
            content_type='application/json'
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = json.loads(response.data)
        order_id = data['id']
        print(f"✓ Order created with ID: {order_id}")
        
        print("\nTesting GET /api/orders...")
        response = client.get('/api/orders')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert len(data) == 1, f"Expected 1 order, got {len(data)}"
        print(f"✓ Retrieved {len(data)} order(s)")
        
        print(f"\nTesting GET /api/orders/{order_id}...")
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['mechanic_name'] == 'David'
        print(f"✓ Retrieved order {order_id}")
        
        print(f"\nTesting PATCH /api/orders/{order_id}...")
        response = client.patch(f'/api/orders/{order_id}',
            data=json.dumps({'status': 'готов'}),
            content_type='application/json'
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['status'] == 'готов'
        print(f"✓ Updated order {order_id} status to 'готов'")
        
        print(f"\nTesting POST /api/orders/{order_id}/print...")
        response = client.post(f'/api/orders/{order_id}/print')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Print endpoint triggered for order {order_id}")
        
        print(f"\nTesting DELETE /api/orders/{order_id}...")
        response = client.delete(f'/api/orders/{order_id}')
        assert response.status_code == 204, f"Expected 204, got {response.status_code}"
        print(f"✓ Deleted order {order_id}")
        
        print("\nTesting validation...")
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
        assert response.status_code == 400, f"Expected 400 for short VIN, got {response.status_code}"
        print("✓ VIN validation working")
        
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
        assert response.status_code == 400, f"Expected 400 for empty parts, got {response.status_code}"
        print("✓ Empty parts validation working")
        
        print("\n✅ All tests passed!")
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

if __name__ == '__main__':
    test_api()
