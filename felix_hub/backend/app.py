import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import text
import asyncio
import time
from collections import OrderedDict
from threading import Event, Lock, Thread

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import (db, Order, Category, Part, Mechanic, OrderComment, 
                    TimeLog, CustomWorkItem, CustomPartItem, WorkOrderAssignment)
from utils.notifier import notify_order_ready, notify_order_status_changed
from utils.printer import print_order_with_fallback, print_test_receipt

load_dotenv()

# Import telegram modules для webhook режима
try:
    from telegram import Update
    from telegram.ext import Application
    # Import bot setup_handlers
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bot'))
    from bot import setup_handlers
    TELEGRAM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Telegram bot modules not available: {e}")
    TELEGRAM_AVAILABLE = False

app = Flask(__name__)

# Secret key configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Database configuration with PostgreSQL support
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
# Railway provides DATABASE_URL with postgres://
# But SQLAlchemy 1.4+ requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# CORS configuration for production
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, origins=ALLOWED_ORIGINS, 
     resources={r"/api/*": {
         "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type", "Authorization"]
     }})

# Setup logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('felix_hub.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ВАЖНО: Создать таблицы сразу при импорте модуля
def init_database():
    """Инициализировать базу данных"""
    try:
        with app.app_context():
            # Проверить подключение
            db.engine.connect()
            logger.info(f"✅ Database connected: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Создать все таблицы
            db.create_all()
            logger.info("✅ Database tables created/verified")
            
            # Проверить что таблицы существуют
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"📋 Available tables: {tables}")
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        import traceback
        traceback.print_exc()


# Инициализировать БД при загрузке модуля
init_database()


# Регистрация mechanic API routes
from api.mechanic_routes import mechanic_bp
app.register_blueprint(mechanic_bp)


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


@app.route('/health')
def health_check():
    """Health check для Railway"""
    try:
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        db_status = 'connected'
    except:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/admin')
def admin_panel():
    """Отображение админ-панели"""
    return render_template('admin.html')


@app.route('/catalog')
def catalog_page():
    """Страница управления каталогом запчастей"""
    return render_template('catalog.html')


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
        # Если таблицы нет - попробовать создать
        if "no such table" in str(e).lower():
            try:
                db.create_all()
                logger.info("✅ Tables created on demand")
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
            except Exception as e2:
                logger.error(f"❌ Error creating tables: {e2}")
                return jsonify({"error": "Database not initialized", "details": str(e2)}), 500
        else:
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
            photo_url=data.get('photo_url'),
            language=data.get('language', 'ru')
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
        # Если таблицы нет - попробовать создать
        if "no such table" in str(e).lower():
            try:
                db.create_all()
                logger.info("✅ Tables created on demand")
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
            except Exception as e2:
                logger.error(f"❌ Error creating tables: {e2}")
                return jsonify({"error": "Database not initialized", "details": str(e2)}), 500
        else:
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
                # Печать чека
                print_success = print_order_with_fallback(order)
                
                # Уведомление
                notify_order_ready(order)
                
                # Отметить как напечатанный если печать была успешной
                if print_success:
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
def print_order_manually(order_id):
    """Принудительная печать чека"""
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({'error': 'Заказ не найден'}), 404
        
        success = print_order_with_fallback(order)
        
        if success:
            order.printed = True
            db.session.commit()
            return jsonify({'message': 'Чек отправлен на печать'}), 200
        else:
            return jsonify({'error': 'Ошибка печати'}), 500
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error printing order {order_id}: {e}")
        return jsonify({'error': 'Ошибка печати заказа'}), 500


@app.route('/api/printer/test', methods=['POST'])
def test_printer():
    """Тестовая печать для проверки принтера"""
    try:
        success = print_test_receipt()
        
        if success:
            return jsonify({'message': 'Тестовый чек напечатан'}), 200
        else:
            return jsonify({'error': 'Ошибка печати'}), 500
        
    except Exception as e:
        logger.error(f"Error testing printer: {e}")
        return jsonify({'error': 'Ошибка печати'}), 500


# === Категории ===

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Получение всех категорий"""
    try:
        categories = Category.query.order_by(Category.sort_order, Category.id).all()
        return jsonify([cat.to_dict() for cat in categories]), 200
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return jsonify({'error': 'Ошибка получения категорий'}), 500


@app.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Получение одной категории"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        return jsonify(category.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching category {category_id}: {e}")
        return jsonify({'error': 'Ошибка получения категории'}), 500


@app.route('/api/categories', methods=['POST'])
def create_category():
    """Создание новой категории"""
    try:
        data = request.get_json()
        
        if not data or 'name_ru' not in data:
            return jsonify({'error': 'Поле name_ru обязательно'}), 400
        
        category = Category(
            name_ru=data['name_ru'],
            name_he=data.get('name_he'),
            name_en=data.get('name_en'),
            icon=data.get('icon', '🔧'),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        logger.info(f"Category created: ID={category.id}, name={category.name_ru}")
        return jsonify(category.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating category: {e}")
        return jsonify({'error': 'Ошибка создания категории'}), 500


@app.route('/api/categories/<int:category_id>', methods=['PATCH'])
def update_category(category_id):
    """Обновление категории"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Невалидный JSON'}), 400
        
        if 'name_ru' in data:
            category.name_ru = data['name_ru']
        if 'name_he' in data:
            category.name_he = data['name_he']
        if 'name_en' in data:
            category.name_en = data['name_en']
        if 'icon' in data:
            category.icon = data['icon']
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        
        db.session.commit()
        
        logger.info(f"Category updated: ID={category_id}")
        return jsonify(category.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating category {category_id}: {e}")
        return jsonify({'error': 'Ошибка обновления категории'}), 500


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Удаление категории"""
    try:
        category = Category.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        # Проверка на связанные заказы
        orders_count = Order.query.filter_by(category=category.name_ru).count()
        if orders_count > 0:
            return jsonify({
                'error': f'Невозможно удалить категорию. Существует {orders_count} связанных заказов'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        logger.info(f"Category deleted: ID={category_id}")
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting category {category_id}: {e}")
        return jsonify({'error': 'Ошибка удаления категории'}), 500


# === Детали ===

@app.route('/api/parts', methods=['GET'])
def get_parts():
    """Получение деталей с опциональным фильтром по категории"""
    try:
        query = Part.query
        
        category_id = request.args.get('category_id', type=int)
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        parts = query.order_by(Part.sort_order, Part.id).all()
        return jsonify([part.to_dict() for part in parts]), 200
        
    except Exception as e:
        logger.error(f"Error fetching parts: {e}")
        return jsonify({'error': 'Ошибка получения деталей'}), 500


@app.route('/api/parts/<int:part_id>', methods=['GET'])
def get_part(part_id):
    """Получение одной детали"""
    try:
        part = Part.query.get(part_id)
        if not part:
            return jsonify({'error': 'Деталь не найдена'}), 404
        return jsonify(part.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching part {part_id}: {e}")
        return jsonify({'error': 'Ошибка получения детали'}), 500


@app.route('/api/parts', methods=['POST'])
def create_part():
    """Создание новой детали"""
    try:
        data = request.get_json()
        
        if not data or 'category_id' not in data or 'name_ru' not in data:
            return jsonify({'error': 'Поля category_id и name_ru обязательны'}), 400
        
        # Проверка существования категории
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        part = Part(
            category_id=data['category_id'],
            name_ru=data['name_ru'],
            name_he=data.get('name_he'),
            name_en=data.get('name_en'),
            is_common=data.get('is_common', True),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(part)
        db.session.commit()
        
        logger.info(f"Part created: ID={part.id}, name={part.name_ru}")
        return jsonify(part.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating part: {e}")
        return jsonify({'error': 'Ошибка создания детали'}), 500


@app.route('/api/parts/<int:part_id>', methods=['PATCH'])
def update_part(part_id):
    """Обновление детали"""
    try:
        part = Part.query.get(part_id)
        
        if not part:
            return jsonify({'error': 'Деталь не найдена'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Невалидный JSON'}), 400
        
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Категория не найдена'}), 404
            part.category_id = data['category_id']
        
        if 'name_ru' in data:
            part.name_ru = data['name_ru']
        if 'name_he' in data:
            part.name_he = data['name_he']
        if 'name_en' in data:
            part.name_en = data['name_en']
        if 'is_common' in data:
            part.is_common = data['is_common']
        if 'sort_order' in data:
            part.sort_order = data['sort_order']
        
        db.session.commit()
        
        logger.info(f"Part updated: ID={part_id}")
        return jsonify(part.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating part {part_id}: {e}")
        return jsonify({'error': 'Ошибка обновления детали'}), 500


@app.route('/api/parts/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    """Удаление детали"""
    try:
        part = Part.query.get(part_id)
        
        if not part:
            return jsonify({'error': 'Деталь не найдена'}), 404
        
        db.session.delete(part)
        db.session.commit()
        
        logger.info(f"Part deleted: ID={part_id}")
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting part {part_id}: {e}")
        return jsonify({'error': 'Ошибка удаления детали'}), 500


# === Telegram Webhook ===

# Глобальные объекты для управления Telegram webhook
telegram_app = None
telegram_loop = None
telegram_thread = None
_processed_updates = OrderedDict()
_processed_updates_lock = Lock()
PROCESSED_UPDATES_TTL = 60 * 15  # 15 минут
PROCESSED_UPDATES_MAX_SIZE = 2048


def _cleanup_processed_updates(now=None):
    if now is None:
        now = time.time()
    while _processed_updates:
        first_key, first_timestamp = next(iter(_processed_updates.items()))
        if now - first_timestamp > PROCESSED_UPDATES_TTL:
            _processed_updates.popitem(last=False)
        else:
            break


def _register_update(update_id):
    if update_id is None:
        return True
    update_key = str(update_id)
    now = time.time()
    with _processed_updates_lock:
        _cleanup_processed_updates(now)
        if update_key in _processed_updates:
            return False
        _processed_updates[update_key] = now
        while len(_processed_updates) > PROCESSED_UPDATES_MAX_SIZE:
            _processed_updates.popitem(last=False)
    return True


def _release_update(update_id):
    if update_id is None:
        return
    update_key = str(update_id)
    with _processed_updates_lock:
        _processed_updates.pop(update_key, None)


def _log_update_result(future, update_identifier):
    try:
        future.result()
        logger.info(f"✅ Update {update_identifier} processed successfully")
    except Exception as exc:
        logger.error(f"❌ Update {update_identifier} processing error: {exc}", exc_info=True)


def setup_telegram_webhook():
    """Настроить Telegram webhook"""
    global telegram_app, telegram_loop, telegram_thread
    
    if not TELEGRAM_AVAILABLE:
        logger.warning("⚠️  Telegram modules not available, webhook disabled")
        return
    
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
    
    if not TELEGRAM_TOKEN:
        logger.warning("⚠️  TELEGRAM_TOKEN not set, bot webhook disabled")
        return
    
    if not WEBHOOK_URL:
        logger.warning("⚠️  WEBHOOK_URL not set, bot webhook disabled")
        return
    
    try:
        from telegram.request import HTTPXRequest
        
        request_config = HTTPXRequest(
            connection_pool_size=8,
            connect_timeout=10.0,
            read_timeout=10.0,
            write_timeout=10.0,
        )
        
        telegram_app = Application.builder()\
            .token(TELEGRAM_TOKEN)\
            .request(request_config)\
            .build()
        
        setup_handlers(telegram_app)
        
        telegram_loop = asyncio.new_event_loop()
        loop_ready = Event()
        
        def run_loop():
            asyncio.set_event_loop(telegram_loop)
            loop_ready.set()
            telegram_loop.run_forever()
        
        telegram_thread = Thread(
            target=run_loop,
            name="TelegramWebhookLoop",
            daemon=True
        )
        telegram_thread.start()
        
        if not loop_ready.wait(timeout=5.0):
            raise RuntimeError("Telegram event loop thread failed to start")
        
        async def init_and_set_webhook():
            await telegram_app.initialize()
            await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
            logger.info(f"✅ Telegram webhook set to: {WEBHOOK_URL}/webhook")
        
        future = asyncio.run_coroutine_threadsafe(init_and_set_webhook(), telegram_loop)
        future.result(timeout=30.0)
        
        with _processed_updates_lock:
            _processed_updates.clear()
        
        logger.info("✅ Telegram application initialized for webhook mode")
    
    except Exception as e:
        logger.error(f"❌ Failed to setup webhook: {e}", exc_info=True)
        cleanup_telegram_app()


@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Endpoint для приёма обновлений от Telegram"""
    if not telegram_app or not telegram_loop:
        logger.error("❌ Webhook called but telegram_app is not configured")
        return jsonify({'error': 'Bot not configured'}), 500
    
    if not telegram_loop.is_running():
        logger.error("❌ Telegram event loop is not running")
        return jsonify({'error': 'Bot not ready'}), 503
    
    try:
        update_data = request.get_json()
        
        if not update_data:
            logger.warning("⚠️  Webhook called with no data")
            return jsonify({'error': 'No data'}), 400
        
        update_id_value = update_data.get('update_id')
        update_identifier = str(update_id_value) if update_id_value is not None else 'unknown'
        
        if update_id_value is not None and not _register_update(update_id_value):
            logger.info(f"🔁 Duplicate update {update_identifier} ignored")
            return jsonify({'ok': True, 'duplicate': True}), 200
        
        logger.info(f"📨 Received webhook update: {update_identifier}")
        
        update = Update.de_json(update_data, telegram_app.bot)
        
        try:
            future = asyncio.run_coroutine_threadsafe(
                telegram_app.process_update(update),
                telegram_loop
            )
        except Exception:
            _release_update(update_id_value)
            raise
        
        future.add_done_callback(
            lambda fut, uid=update_identifier: _log_update_result(fut, uid)
        )
        
        return jsonify({'ok': True}), 200
    
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def cleanup_telegram_app():
    """Gracefully shutdown telegram application"""
    global telegram_app, telegram_loop, telegram_thread
    try:
        if telegram_app and telegram_loop and telegram_loop.is_running():
            logger.info("🔄 Shutting down telegram application...")
            future = asyncio.run_coroutine_threadsafe(telegram_app.shutdown(), telegram_loop)
            future.result(timeout=15.0)
            logger.info("✅ Telegram application shut down successfully")
    except Exception as e:
        logger.error(f"❌ Error shutting down telegram app: {e}", exc_info=True)
    finally:
        if telegram_loop:
            try:
                if telegram_loop.is_running():
                    telegram_loop.call_soon_threadsafe(telegram_loop.stop)
            except RuntimeError:
                pass
        if telegram_thread and telegram_thread.is_alive():
            telegram_thread.join(timeout=5.0)
        if telegram_loop:
            try:
                telegram_loop.close()
            except Exception:
                pass
        telegram_app = None
        telegram_loop = None
        telegram_thread = None
        with _processed_updates_lock:
            _processed_updates.clear()


# Инициализировать webhook при старте приложения
with app.app_context():
    setup_telegram_webhook()

# Зарегистрировать cleanup при завершении
import atexit
atexit.register(cleanup_telegram_app)


if __name__ == '__main__':
    # Создать таблицы если их нет
    with app.app_context():
        db.create_all()
        logger.info("Database initialized")
    
    # Production: gunicorn управляет запуском
    # Development: запускается напрямую
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
