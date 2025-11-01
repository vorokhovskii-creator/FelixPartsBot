import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('ENABLE_CAR_NUMBER', 'true')
os.environ.setdefault('ALLOW_ANY_CAR_NUMBER', 'false')

def test_api():
    from app import app, db
    from models import Order
    import json
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        client = app.test_client()
        
        print("Testing POST /api/orders...")
        response = client.post('/api/orders', 
            data=json.dumps({
                'mechanic_name': 'David',
                'telegram_id': '12345678',
                'category': 'Тормоза',
                'carNumber': 'AB1234CD',
                'selected_parts': ['Передние колодки', 'Диски передние'],
                'is_original': False,
                'photo_url': 'https://api.telegram.org/file/test.jpg'
            }),
            content_type='application/json'
        )
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        data = json.loads(response.data)
        order_id = data['id']
        assert data['carNumber'] == 'AB1234CD', f"Expected carNumber AB1234CD, got {data['carNumber']}"
        assert data['vin'] == 'AB1234CD', f"Expected vin AB1234CD, got {data['vin']}"
        print(f"✓ Order created with ID: {order_id}")
        
        print("\nTesting GET /api/orders...")
        response = client.get('/api/orders')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert len(data) == 1, f"Expected 1 order, got {len(data)}"
        assert data[0]['carNumber'] == 'AB1234CD', f"Expected list carNumber AB1234CD, got {data[0].get('carNumber')}"
        print(f"✓ Retrieved {len(data)} order(s)")
        
        print(f"\nTesting GET /api/orders/{order_id}...")
        response = client.get(f'/api/orders/{order_id}')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = json.loads(response.data)
        assert data['mechanic_name'] == 'David'
        assert data['carNumber'] == 'AB1234CD'
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
        
        print("\nTesting backward compatibility with vin field...")
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Legacy',
                'telegram_id': '987',
                'category': 'Test',
                'vin': 'ZZ9900',
                'selected_parts': ['LegacyPart']
            }),
            content_type='application/json'
        )
        assert response.status_code == 201, f"Expected 201 for legacy vin, got {response.status_code}"
        legacy_data = json.loads(response.data)
        assert legacy_data['carNumber'] == 'ZZ9900', f"Expected carNumber ZZ9900, got {legacy_data['carNumber']}"
        assert legacy_data['vin'] == 'ZZ9900', f"Expected vin ZZ9900, got {legacy_data['vin']}"
        print("✓ Legacy vin payload accepted")
        legacy_order_id = legacy_data['id']

        print(f"\nCleaning up legacy order {legacy_order_id}...")
        response = client.delete(f'/api/orders/{legacy_order_id}')
        assert response.status_code == 204, f"Expected 204 when cleaning legacy order, got {response.status_code}"
        print("✓ Legacy order removed")

        print("\nTesting validation...")
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Test',
                'telegram_id': '123',
                'category': 'Test',
                'carNumber': 'ABC',
                'selected_parts': ['Part1']
            }),
            content_type='application/json'
        )
        assert response.status_code == 400, f"Expected 400 for short car number, got {response.status_code}"
        print("✓ carNumber length validation working")
        
        response = client.post('/api/orders',
            data=json.dumps({
                'mechanic_name': 'Test',
                'telegram_id': '123',
                'category': 'Test',
                'carNumber': 'ABCD1234',
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
