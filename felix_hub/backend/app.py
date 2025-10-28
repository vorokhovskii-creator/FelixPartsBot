import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, Order

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

logging.basicConfig(level=logging.INFO)
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
        
        if 'status' in data:
            order.status = data['status']
        
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
