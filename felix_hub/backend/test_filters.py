import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

def test_filters():
    from app import app, db
    from models import Order
    import json
    
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        
        client = app.test_client()
        
        print("Creating test orders...")
        orders_data = [
            {
                'mechanic_name': 'David',
                'telegram_id': '111',
                'category': 'Тормоза',
                'vin': '4T1BE32K',
                'selected_parts': ['Передние колодки'],
                'is_original': False
            },
            {
                'mechanic_name': 'John',
                'telegram_id': '222',
                'category': 'Двигатель',
                'vin': 'WBAAA',
                'selected_parts': ['Масло'],
                'is_original': True
            },
            {
                'mechanic_name': 'David',
                'telegram_id': '111',
                'category': 'Подвеска',
                'vin': 'JN1CA',
                'selected_parts': ['Амортизатор'],
                'is_original': False
            }
        ]
        
        order_ids = []
        for order_data in orders_data:
            response = client.post('/api/orders', 
                data=json.dumps(order_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            order_ids.append(json.loads(response.data)['id'])
        print("✓ Created 3 test orders")
        
        client.patch(f'/api/orders/{order_ids[1]}',
            data=json.dumps({'status': 'в работе'}),
            content_type='application/json'
        )
        client.patch(f'/api/orders/{order_ids[2]}',
            data=json.dumps({'status': 'готов'}),
            content_type='application/json'
        )
        print("✓ Updated order statuses")
        
        print("\nTesting filter by status...")
        response = client.get('/api/orders?status=новый')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['status'] == 'новый'
        print(f"✓ Filter by status working: found {len(data)} order(s)")
        
        print("\nTesting filter by mechanic...")
        response = client.get('/api/orders?mechanic=David')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert all(order['mechanic_name'] == 'David' for order in data)
        print(f"✓ Filter by mechanic working: found {len(data)} order(s)")
        
        print("\nTesting filter by telegram_id...")
        response = client.get('/api/orders?telegram_id=222')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['telegram_id'] == '222'
        print(f"✓ Filter by telegram_id working: found {len(data)} order(s)")
        
        print("\nTesting limit parameter...")
        response = client.get('/api/orders?limit=2')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        print(f"✓ Limit parameter working: returned {len(data)} order(s)")
        
        print("\nTesting offset parameter...")
        response = client.get('/api/orders?offset=2')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        print(f"✓ Offset parameter working: returned {len(data)} order(s)")
        
        print("\nTesting 404 for non-existent order...")
        response = client.get('/api/orders/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        print("✓ 404 error handling working")
        
        print("\n✅ All filter tests passed!")
        
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

if __name__ == '__main__':
    test_filters()
