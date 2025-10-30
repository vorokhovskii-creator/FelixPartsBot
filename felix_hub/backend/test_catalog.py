import unittest
import json
from app import app, db
from models import Category, Part, Order

class TestCatalogAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            cat1 = Category(name_ru='Тормоза', icon='🔧', sort_order=0)
            db.session.add(cat1)
            db.session.flush()
            
            part1 = Part(category_id=cat1.id, name_ru='Передние колодки', is_common=True, sort_order=0)
            part2 = Part(category_id=cat1.id, name_ru='Задние колодки', is_common=True, sort_order=1)
            db.session.add(part1)
            db.session.add(part2)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_categories(self):
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name_ru'], 'Тормоза')
        self.assertEqual(data[0]['icon'], '🔧')
        self.assertEqual(data[0]['parts_count'], 2)
    
    def test_create_category(self):
        response = self.client.post('/api/categories',
            data=json.dumps({'name_ru': 'Двигатель', 'icon': '⚙️'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name_ru'], 'Двигатель')
    
    def test_update_category(self):
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id
        
        response = self.client.patch(f'/api/categories/{cat_id}',
            data=json.dumps({'name_ru': 'Тормоза обновлены'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['name_ru'], 'Тормоза обновлены')
    
    def test_get_parts(self):
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id
        
        response = self.client.get(f'/api/parts?category_id={cat_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name_ru'], 'Передние колодки')
    
    def test_create_part(self):
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id
        
        response = self.client.post('/api/parts',
            data=json.dumps({
                'category_id': cat_id,
                'name_ru': 'Диски передние',
                'is_common': True
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['name_ru'], 'Диски передние')
    
    def test_update_part(self):
        with app.app_context():
            part = Part.query.first()
            part_id = part.id
        
        response = self.client.patch(f'/api/parts/{part_id}',
            data=json.dumps({'name_ru': 'Колодки передние обновлены'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['name_ru'], 'Колодки передние обновлены')
    
    def test_delete_part(self):
        with app.app_context():
            part = Part.query.first()
            part_id = part.id
        
        response = self.client.delete(f'/api/parts/{part_id}')
        self.assertEqual(response.status_code, 204)
    
    def test_delete_category_with_orders(self):
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id
            cat_name = cat.name_ru
            
            order = Order(
                mechanic_name='Test',
                telegram_id='123',
                category=cat_name,
                vin='TEST123',
                selected_parts=['Передние колодки']
            )
            db.session.add(order)
            db.session.commit()
        
        response = self.client.delete(f'/api/categories/{cat_id}')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('Невозможно удалить', data['error'])
    
    def test_delete_category_cascades_parts(self):
        with app.app_context():
            cat = Category.query.first()
            cat_id = cat.id
        
        response = self.client.delete(f'/api/categories/{cat_id}')
        self.assertEqual(response.status_code, 204)
        
        with app.app_context():
            parts_count = Part.query.filter_by(category_id=cat_id).count()
            self.assertEqual(parts_count, 0)

if __name__ == '__main__':
    unittest.main()
