"""
Тесты для админ-панели
"""
import pytest
from app import app, db
from models import Order
from datetime import datetime, timedelta
import json


@pytest.fixture
def client():
    """Создание тестового клиента Flask"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            
            # Создаем тестовые заказы
            for i in range(5):
                order = Order(
                    mechanic_name=f'Механик {i+1}',
                    telegram_id=f'12345678{i}',
                    category='Подвеска',
                    vin=f'TEST123456789{i}',
                    selected_parts=['Деталь 1', 'Деталь 2'],
                    is_original=i % 2 == 0,
                    status='новый' if i < 2 else 'в работе' if i < 4 else 'готов'
                )
                db.session.add(order)
            
            # Заказ за сегодня
            today_order = Order(
                mechanic_name='Механик Сегодня',
                telegram_id='999999999',
                category='Двигатель',
                vin='TODAY12345',
                selected_parts=['Свеча'],
                is_original=True,
                status='готов',
                created_at=datetime.now()
            )
            db.session.add(today_order)
            
            db.session.commit()
            
        yield client


def test_admin_panel_route(client):
    """Тест GET /admin - админ-панель должна открываться"""
    response = client.get('/admin')
    assert response.status_code == 200
    assert b'Felix Hub' in response.data
    assert b'admin.html' in response.data or b'admin.js' in response.data or b'\xd0\x90\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd-\xd0\xbf\xd0\xb0\xd0\xbd\xd0\xb5\xd0\xbb\xd1\x8c' in response.data


def test_get_orders_stats(client):
    """Тест GET /api/orders/stats - статистика заказов"""
    response = client.get('/api/orders/stats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'total' in data
    assert 'by_status' in data
    assert 'today' in data
    
    assert data['total'] == 6
    assert data['by_status']['новый'] == 2
    assert data['by_status']['в работе'] == 2
    assert data['by_status']['готов'] == 2
    # All test orders are created today
    assert data['today'] >= 1


def test_export_orders_default(client):
    """Тест GET /export - экспорт заказов в Excel (последние 30 дней)"""
    response = client.get('/export')
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert 'felix_orders_' in response.headers.get('Content-Disposition', '')


def test_export_orders_with_filter(client):
    """Тест GET /export?days=7&status=готов - экспорт с фильтрами"""
    response = client.get('/export?days=7&status=готов')
    assert response.status_code == 200
    assert response.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def test_status_change_to_ready_marks_printed(client):
    """Тест: при статусе 'готов' заказ автоматически помечается как напечатанный"""
    # Создаем новый заказ
    response = client.post('/api/orders', 
                          json={
                              'mechanic_name': 'Иван',
                              'telegram_id': '123456',
                              'category': 'Тормоза',
                              'vin': 'AUTOTEST123',
                              'selected_parts': ['Тормозные колодки']
                          })
    assert response.status_code == 201
    order_id = json.loads(response.data)['id']
    
    # Изменяем статус на "готов"
    response = client.patch(f'/api/orders/{order_id}',
                           json={'status': 'готов'})
    assert response.status_code == 200
    
    # Проверяем, что printed установлен в True
    updated_order = json.loads(response.data)
    assert updated_order['status'] == 'готов'
    assert updated_order['printed'] == True


def test_admin_panel_filters(client):
    """Тест фильтрации заказов через API"""
    # Фильтр по статусу
    response = client.get('/api/orders?status=готов')
    assert response.status_code == 200
    orders = json.loads(response.data)
    assert len(orders) >= 2
    assert all(order['status'] == 'готов' for order in orders)
    
    # Фильтр по механику
    response = client.get('/api/orders?mechanic=Механик 1')
    assert response.status_code == 200
    orders = json.loads(response.data)
    assert len(orders) >= 1
    assert all(order['mechanic_name'] == 'Механик 1' for order in orders)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
