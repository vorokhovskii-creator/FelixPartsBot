import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
from models import db, Order
from utils.notifier import notify_order_ready, notify_order_status_changed

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('felix_hub.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ресурс не найден'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500


@app.route('/admin')
def admin_panel():
    """Отображение админ-панели"""
    return render_template('admin.html')


@app.route('/api/orders/stats')
def get_orders_stats():
    """Статистика по заказам"""
    try:
        total = Order.query.count()
        by_status = db.session.query(
            Order.status, 
            db.func.count(Order.id)
        ).group_by(Order.status).all()
        
        today = datetime.now().date()
        today_count = Order.query.filter(
            db.func.date(Order.created_at) == today
        ).count()
        
        return jsonify({
            'total': total,
            'by_status': dict(by_status),
            'today': today_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Ошибка получения статистики'}), 500


@app.route('/export')
def export_orders():
    """Экспорт заказов в Excel"""
    try:
        # Параметры фильтрации
        days = request.args.get('days', 30, type=int)
        status = request.args.get('status', None)
        
        # Запрос заказов
        query = Order.query.filter(
            Order.created_at >= datetime.now() - timedelta(days=days)
        )
        
        if status:
            query = query.filter(Order.status == status)
        
        orders = query.all()
        
        # Формирование DataFrame
        data = []
        for order in orders:
            data.append({
                'ID': order.id,
                'Дата': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'Механик': order.mechanic_name,
                'Категория': order.category,
                'VIN': order.vin,
                'Детали': ', '.join(order.selected_parts),
                'Оригинал': 'Да' if order.is_original else 'Нет',
                'Статус': order.status,
                'Напечатан': 'Да' if order.printed else 'Нет'
            })
        
        df = pd.DataFrame(data)
        
        # Сохранение в Excel
        output_path = f'/tmp/felix_orders_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        return send_file(
            output_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'felix_orders_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
        
    except Exception as e:
        logger.error(f"Error exporting orders: {e}")
        return jsonify({'error': 'Ошибка экспорта заказов'}), 500


@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Невалидный JSON'}), 400
        
        required_fields = ['mechanic_name', 'telegram_id', 'category', 'vin', 'selected_parts']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Отсутствует обязательное поле: {field}'}), 400
        
        if not isinstance(data['selected_parts'], list) or len(data['selected_parts']) == 0:
            return jsonify({'error': 'selected_parts должен быть непустым массивом'}), 400
        
        if len(data['vin']) < 4:
            return jsonify({'error': 'VIN должен содержать минимум 4 символа'}), 400
        
        order = Order(
            mechanic_name=data['mechanic_name'],
            telegram_id=data['telegram_id'],
            category=data['category'],
            vin=data['vin'],
            selected_parts=data['selected_parts'],
            is_original=data.get('is_original', False),
            photo_url=data.get('photo_url')
        )
        
        db.session.add(order)
        db.session.commit()
        
        logger.info(f"Order created: ID={order.id}, mechanic={order.mechanic_name}")
        
        return jsonify(order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating order: {e}")
        return jsonify({'error': 'Ошибка создания заказа'}), 500


@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        query = Order.query
        
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        mechanic = request.args.get('mechanic')
        if mechanic:
            query = query.filter_by(mechanic_name=mechanic)
        
        telegram_id = request.args.get('telegram_id')
        if telegram_id:
            query = query.filter_by(telegram_id=telegram_id)
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        orders = query.order_by(Order.created_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({'error': 'Ошибка получения заказов'}), 500


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        return jsonify({'error': 'Ошибка получения заказа'}), 500


@app.route('/api/orders/<int:order_id>', methods=['PATCH'])
def update_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Невалидный JSON'}), 400
        
        old_status = order.status
        
        if 'status' in data:
            new_status = data['status']
            order.status = new_status
            
            if new_status == 'готов':
                notify_order_ready(order)
                order.printed = True
                logger.info(f"Order {order_id} marked as printed automatically")
            elif new_status in ['в работе', 'выдан']:
                notify_order_status_changed(order, old_status, new_status)
        
        if 'printed' in data:
            order.printed = data['printed']
        
        if 'mechanic_name' in data:
            order.mechanic_name = data['mechanic_name']
        
        if 'category' in data:
            order.category = data['category']
        
        if 'vin' in data:
            order.vin = data['vin']
        
        if 'selected_parts' in data:
            order.selected_parts = data['selected_parts']
        
        if 'is_original' in data:
            order.is_original = data['is_original']
        
        if 'photo_url' in data:
            order.photo_url = data['photo_url']
        
        db.session.commit()
        
        logger.info(f"Order updated: ID={order_id}, status={order.status}")
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating order {order_id}: {e}")
        return jsonify({'error': 'Ошибка обновления заказа'}), 500


@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404
        
        db.session.delete(order)
        db.session.commit()
        
        logger.info(f"Order deleted: ID={order_id}")
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting order {order_id}: {e}")
        return jsonify({'error': 'Ошибка удаления заказа'}), 500


@app.route('/api/orders/<int:order_id>/print', methods=['POST'])
def print_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404
        
        logger.info(f"Print triggered for order: ID={order_id}")
        
        return jsonify({'message': 'Печать инициирована', 'order_id': order_id}), 200
        
    except Exception as e:
        logger.error(f"Error printing order {order_id}: {e}")
        return jsonify({'error': 'Ошибка печати заказа'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
    app.run(host='0.0.0.0', port=5000, debug=True)
