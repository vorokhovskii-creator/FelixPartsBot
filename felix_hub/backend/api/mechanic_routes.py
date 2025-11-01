from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func
from models import db, Mechanic, Order, OrderComment, TimeLog, CustomWorkItem, CustomPartItem, WorkOrderAssignment, Category, Part
from auth import generate_jwt_token, require_auth, get_jwt_identity
import jwt
import os
import json
import logging

logger = logging.getLogger(__name__)

mechanic_bp = Blueprint('mechanic', __name__, url_prefix='/api/mechanic')


@mechanic_bp.route('/login', methods=['POST'])
def mechanic_login():
    """Вход механика"""
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email и пароль обязательны'}), 400
    
    mechanic = db.session.query(Mechanic).filter_by(
        email=data['email'],
        active=True
    ).first()
    
    if mechanic and check_password_hash(mechanic.password_hash, data['password']):
        token = generate_jwt_token(mechanic.id)
        return jsonify({
            'token': token,
            'mechanic': mechanic.to_dict()
        })
    return jsonify({'error': 'Неверный email или пароль'}), 401


@mechanic_bp.route('/token-login', methods=['POST'])
def mechanic_token_login():
    """Вход механика по временному токену (для deeplink из Telegram)"""
    data = request.json
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Токен обязателен'}), 400
    
    try:
        secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
        payload = jwt.decode(data['token'], secret_key, algorithms=['HS256'])
        
        mechanic_id = payload.get('mechanic_id')
        telegram_id = payload.get('telegram_id')
        
        if not mechanic_id or not telegram_id:
            return jsonify({'error': 'Невалидный токен'}), 401
        
        # Проверить существование механика
        mechanic = db.session.query(Mechanic).filter_by(
            id=mechanic_id,
            telegram_id=telegram_id,
            active=True
        ).first()
        
        if not mechanic:
            return jsonify({'error': 'Механик не найден или неактивен'}), 404
        
        # Сгенерировать полноценный JWT токен
        auth_token = generate_jwt_token(mechanic.id)
        
        logger.info(f"Mechanic {mechanic_id} logged in via token from Telegram")
        
        return jsonify({
            'token': auth_token,
            'mechanic': mechanic.to_dict()
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Токен истёк'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Невалидный токен'}), 401
    except Exception as e:
        logger.error(f"Token login error: {e}")
        return jsonify({'error': 'Ошибка авторизации'}), 500


@mechanic_bp.route('/me', methods=['GET'])
@require_auth
def get_current_mechanic():
    """Получить текущего механика"""
    mechanic_id = get_jwt_identity()
    mechanic = db.session.query(Mechanic).get(mechanic_id)
    
    if not mechanic:
        return jsonify({'error': 'Механик не найден'}), 404
    
    return jsonify(mechanic.to_dict())


@mechanic_bp.route('/orders', methods=['GET'])
@require_auth
def get_mechanic_orders():
    """Список заказов текущего механика"""
    mechanic_id = get_jwt_identity()
    status = request.args.get('status')
    
    query = db.session.query(Order).filter(
        Order.assigned_mechanic_id == mechanic_id
    )
    
    if status:
        query = query.filter(Order.work_status == status)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])


@mechanic_bp.route('/orders/<int:order_id>', methods=['GET'])
@require_auth
def get_mechanic_order_details(order_id):
    """Детали заказа"""
    mechanic_id = get_jwt_identity()
    
    order = db.session.query(Order).filter(
        Order.id == order_id,
        Order.assigned_mechanic_id == mechanic_id
    ).first()
    
    if not order:
        return jsonify({'error': 'Заказ не найден'}), 404
    
    return jsonify({
        **order.to_dict(),
        'comments': [c.to_dict() for c in order.comments],
        'time_logs': [t.to_dict() for t in order.time_logs],
        'custom_works': [w.to_dict() for w in order.custom_works],
        'custom_parts': [p.to_dict() for p in order.custom_parts],
    })


@mechanic_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
@require_auth
def update_order_status(order_id):
    """Обновить статус заказа"""
    mechanic_id = get_jwt_identity()
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Статус обязателен'}), 400
    
    order = db.session.query(Order).filter(
        Order.id == order_id,
        Order.assigned_mechanic_id == mechanic_id
    ).first()
    
    if not order:
        return jsonify({'error': 'Заказ не найден'}), 404
    
    valid_statuses = ['новый', 'в работе', 'на паузе', 'завершен']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Недопустимый статус'}), 400
    
    order.work_status = data['status']
    order.updated_at = datetime.utcnow()
    
    assignment = db.session.query(WorkOrderAssignment).filter_by(
        order_id=order_id,
        mechanic_id=mechanic_id
    ).first()
    if assignment:
        status_map = {
            'новый': 'assigned',
            'в работе': 'in_progress',
            'на паузе': 'paused',
            'завершен': 'completed'
        }
        assignment.status = status_map[data['status']]
    
    db.session.commit()
    return jsonify(order.to_dict())


@mechanic_bp.route('/orders/<int:order_id>/comments', methods=['POST'])
@require_auth
def add_comment(order_id):
    """Добавить комментарий к заказу"""
    mechanic_id = get_jwt_identity()
    data = request.json
    
    if not data or 'comment' not in data:
        return jsonify({'error': 'Комментарий обязателен'}), 400
    
    comment = OrderComment(
        order_id=order_id,
        mechanic_id=mechanic_id,
        comment=data['comment']
    )
    
    db.session.add(comment)
    
    order = db.session.query(Order).get(order_id)
    if order:
        order.comments_count += 1
    
    db.session.commit()
    return jsonify(comment.to_dict()), 201


@mechanic_bp.route('/orders/<int:order_id>/comments', methods=['GET'])
@require_auth
def get_comments(order_id):
    """Получить комментарии к заказу"""
    comments = db.session.query(OrderComment).filter_by(
        order_id=order_id
    ).order_by(OrderComment.created_at.desc()).all()
    
    return jsonify([c.to_dict() for c in comments])


@mechanic_bp.route('/orders/<int:order_id>/time/start', methods=['POST'])
@require_auth
def start_timer(order_id):
    """Запустить таймер работы"""
    mechanic_id = get_jwt_identity()
    
    active_timer = db.session.query(TimeLog).filter_by(
        mechanic_id=mechanic_id,
        is_active=True
    ).first()
    
    if active_timer:
        return jsonify({'error': 'У вас уже запущен таймер'}), 400
    
    time_log = TimeLog(
        order_id=order_id,
        mechanic_id=mechanic_id,
        started_at=datetime.utcnow(),
        is_active=True
    )
    
    db.session.add(time_log)
    db.session.commit()
    return jsonify(time_log.to_dict()), 201


@mechanic_bp.route('/orders/<int:order_id>/time/stop', methods=['POST'])
@require_auth
def stop_timer(order_id):
    """Остановить таймер"""
    mechanic_id = get_jwt_identity()
    
    time_log = db.session.query(TimeLog).filter_by(
        order_id=order_id,
        mechanic_id=mechanic_id,
        is_active=True
    ).first()
    
    if not time_log:
        return jsonify({'error': 'Активный таймер не найден'}), 404
    
    time_log.ended_at = datetime.utcnow()
    time_log.is_active = False
    time_log.duration_minutes = int(
        (time_log.ended_at - time_log.started_at).total_seconds() / 60
    )
    
    order = db.session.query(Order).get(order_id)
    if order:
        order.total_time_minutes += time_log.duration_minutes
    
    db.session.commit()
    return jsonify(time_log.to_dict())


@mechanic_bp.route('/orders/<int:order_id>/time/manual', methods=['POST'])
@require_auth
def add_manual_time(order_id):
    """Добавить время вручную"""
    mechanic_id = get_jwt_identity()
    data = request.json
    
    if not data or 'started_at' not in data or 'ended_at' not in data or 'duration_minutes' not in data:
        return jsonify({'error': 'started_at, ended_at и duration_minutes обязательны'}), 400
    
    time_log = TimeLog(
        order_id=order_id,
        mechanic_id=mechanic_id,
        started_at=datetime.fromisoformat(data['started_at'].replace('Z', '+00:00')),
        ended_at=datetime.fromisoformat(data['ended_at'].replace('Z', '+00:00')),
        duration_minutes=data['duration_minutes'],
        notes=data.get('notes'),
        is_active=False
    )
    
    db.session.add(time_log)
    
    order = db.session.query(Order).get(order_id)
    if order:
        order.total_time_minutes += time_log.duration_minutes
    
    db.session.commit()
    return jsonify(time_log.to_dict()), 201


@mechanic_bp.route('/time/active', methods=['GET'])
@require_auth
def get_active_timer():
    """Получить активный таймер механика"""
    mechanic_id = get_jwt_identity()
    
    timer = db.session.query(TimeLog).filter_by(
        mechanic_id=mechanic_id,
        is_active=True
    ).first()
    
    return jsonify(timer.to_dict() if timer else None)


@mechanic_bp.route('/orders/<int:order_id>/custom-works', methods=['POST'])
@require_auth
def add_custom_work(order_id):
    """Добавить кастомную работу"""
    mechanic_id = get_jwt_identity()
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Название работы обязательно'}), 400
    
    work = CustomWorkItem(
        order_id=order_id,
        name=data['name'],
        description=data.get('description'),
        price=data.get('price'),
        estimated_time_minutes=data.get('estimated_time_minutes'),
        added_by_id=mechanic_id
    )
    
    db.session.add(work)
    db.session.commit()
    return jsonify(work.to_dict()), 201


@mechanic_bp.route('/orders/<int:order_id>/custom-parts', methods=['POST'])
@require_auth
def add_custom_part(order_id):
    """Добавить кастомную запчасть"""
    mechanic_id = get_jwt_identity()
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Название запчасти обязательно'}), 400
    
    part = CustomPartItem(
        order_id=order_id,
        name=data['name'],
        part_number=data.get('part_number'),
        price=data.get('price'),
        quantity=data.get('quantity', 1),
        added_by_id=mechanic_id
    )
    
    db.session.add(part)
    db.session.commit()
    return jsonify(part.to_dict()), 201


@mechanic_bp.route('/stats', methods=['GET'])
@require_auth
def get_mechanic_stats():
    """Статистика работы механика"""
    mechanic_id = get_jwt_identity()
    all_time = request.args.get('all_time', 'false') == 'true'
    
    if all_time:
        # Общая статистика за всё время
        total_completed = db.session.query(Order).filter(
            Order.assigned_mechanic_id == mechanic_id,
            Order.work_status == 'завершен'
        ).count()
        
        active_orders = db.session.query(Order).filter(
            Order.assigned_mechanic_id == mechanic_id,
            Order.work_status.in_(['в работе', 'на паузе'])
        ).count()
        
        total_minutes = db.session.query(func.sum(TimeLog.duration_minutes)).filter(
            TimeLog.mechanic_id == mechanic_id,
            TimeLog.is_active == False
        ).scalar() or 0
        
        avg_order_time = db.session.query(func.avg(Order.total_time_minutes)).filter(
            Order.assigned_mechanic_id == mechanic_id,
            Order.work_status == 'завершен',
            Order.total_time_minutes > 0
        ).scalar() or 0
        
        return jsonify({
            'total_completed': total_completed,
            'active_orders': active_orders,
            'total_minutes': int(total_minutes),
            'avg_order_time': round(float(avg_order_time), 1)
        })
    else:
        # Статистика за сегодня
        today = datetime.utcnow().date()
        
        stats = {
            'active_orders': db.session.query(Order).filter(
                Order.assigned_mechanic_id == mechanic_id,
                Order.work_status.in_(['в работе', 'на паузе'])
            ).count(),
            
            'completed_today': db.session.query(Order).filter(
                Order.assigned_mechanic_id == mechanic_id,
                Order.work_status == 'завершен',
                func.date(Order.updated_at) == today
            ).count(),
            
            'time_today_minutes': db.session.query(func.sum(TimeLog.duration_minutes)).filter(
                TimeLog.mechanic_id == mechanic_id,
                func.date(TimeLog.started_at) == today
            ).scalar() or 0,
        }
        
        return jsonify(stats)


@mechanic_bp.route('/time/history', methods=['GET'])
@require_auth
def get_mechanic_time_history():
    """История времени механика с фильтрами"""
    mechanic_id = get_jwt_identity()
    start_date = request.args.get('start_date')  # YYYY-MM-DD
    end_date = request.args.get('end_date')
    
    query = db.session.query(TimeLog).filter(
        TimeLog.mechanic_id == mechanic_id,
        TimeLog.is_active == False
    )
    
    if start_date:
        query = query.filter(func.date(TimeLog.started_at) >= start_date)
    if end_date:
        query = query.filter(func.date(TimeLog.started_at) <= end_date)
    
    time_logs = query.order_by(TimeLog.started_at.desc()).all()
    
    # Статистика
    total_minutes = sum(log.duration_minutes for log in time_logs if log.duration_minutes)
    sessions_count = len(time_logs)
    orders_count = len(set(log.order_id for log in time_logs))
    avg_session = total_minutes / sessions_count if sessions_count > 0 else 0
    
    return jsonify({
        'stats': {
            'total_minutes': total_minutes,
            'sessions_count': sessions_count,
            'orders_count': orders_count,
            'avg_session': avg_session
        },
        'sessions': [log.to_dict() for log in time_logs]
    })


@mechanic_bp.route('/profile', methods=['PATCH'])
@require_auth
def update_mechanic_profile():
    """Обновление профиля механика"""
    mechanic_id = get_jwt_identity()
    mechanic = db.session.query(Mechanic).get(mechanic_id)
    
    if not mechanic:
        return jsonify({'error': 'Механик не найден'}), 404
    
    data = request.json
    
    # Разрешено редактировать только телефон
    if 'phone' in data:
        mechanic.phone = data['phone']
    
    mechanic.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(mechanic.to_dict())


@mechanic_bp.route('/change-password', methods=['POST'])
@require_auth
def change_mechanic_password():
    """Смена пароля механика"""
    mechanic_id = get_jwt_identity()
    mechanic = db.session.query(Mechanic).get(mechanic_id)
    
    if not mechanic:
        return jsonify({'error': 'Механик не найден'}), 404
    
    data = request.json
    
    if not data or 'current_password' not in data or 'new_password' not in data or 'confirm_password' not in data:
        return jsonify({'error': 'Все поля обязательны'}), 400
    
    # Проверить текущий пароль
    if not check_password_hash(mechanic.password_hash, data['current_password']):
        return jsonify({'error': 'Неверный текущий пароль'}), 400
    
    # Проверить совпадение нового пароля
    if data['new_password'] != data['confirm_password']:
        return jsonify({'error': 'Пароли не совпадают'}), 400
    
    # Проверить минимальную длину пароля
    if len(data['new_password']) < 6:
        return jsonify({'error': 'Пароль должен содержать минимум 6 символов'}), 400
    
    # Обновить пароль
    mechanic.password_hash = generate_password_hash(data['new_password'])
    mechanic.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Пароль успешно изменён'})


@mechanic_bp.route('/orders', methods=['POST'])
@require_auth
def create_order():
    """Механик создаёт заказ на запчасти"""
    mechanic_id = get_jwt_identity()
    mechanic = db.session.query(Mechanic).get(mechanic_id)
    
    if not mechanic:
        return jsonify({'error': 'Механик не найден'}), 404
    
    try:
        category_id = request.form.get('category_id')
        part_ids_json = request.form.get('part_ids')
        car_number = request.form.get('car_number')
        vin = request.form.get('vin')
        part_type = request.form.get('part_type')
        
        # Accept either car_number or vin (for backward compatibility)
        vehicle_identifier = car_number or vin
        
        if not all([category_id, part_ids_json, vehicle_identifier, part_type]):
            return jsonify({'error': 'Все поля обязательны'}), 400
        
        part_ids = json.loads(part_ids_json)
        
        if not isinstance(part_ids, list) or len(part_ids) == 0:
            return jsonify({'error': 'Выберите хотя бы одну запчасть'}), 400
        
        category = db.session.query(Category).get(category_id)
        if not category:
            return jsonify({'error': 'Категория не найдена'}), 404
        
        parts = db.session.query(Part).filter(Part.id.in_(part_ids)).all()
        if len(parts) != len(part_ids):
            return jsonify({'error': 'Некоторые запчасти не найдены'}), 404
        
        part_names = ', '.join([p.name_ru for p in parts])
        
        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                filename = secure_filename(f"order_{datetime.utcnow().timestamp()}_{file.filename}")
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                photo_url = f"/static/uploads/{filename}"
        
        is_original = part_type == 'original'
        
        order = Order(
            mechanic_name=mechanic.name,
            telegram_id=mechanic.telegram_id or '',
            category=category.name_ru,
            car_number=car_number,
            vin=vin,
            selected_parts=[p.name_ru for p in parts],
            is_original=is_original,
            photo_url=photo_url,
            status='новый',
            work_status='новый',
            assigned_mechanic_id=mechanic_id
        )
        
        db.session.add(order)
        db.session.commit()
        
        logger.info(f"Order created by mechanic {mechanic.name}: ID={order.id}")
        
        return jsonify(order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating order: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Ошибка создания заказа'}), 500
