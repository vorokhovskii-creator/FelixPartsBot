import logging
from flask import request, jsonify
from models import db, Order

logger = logging.getLogger(__name__)


def sanitize_legacy_parts_payload(parts_list):
    """Sanitize legacy parts payload format."""
    if not isinstance(parts_list, list) or not parts_list:
        raise ValueError('selected_parts должен быть непустым массивом')
    sanitized = []
    for part in parts_list:
        if not isinstance(part, str) or not part.strip():
            raise ValueError('selected_parts должен содержать строковые значения')
        sanitized.append({
            'partId': None,
            'name': part.strip(),
            'quantity': 1,
            'price': None,
            'isCustom': False,
            'note': None
        })
    return sanitized


def sanitize_parts_payload(parts_payload):
    """Sanitize modern parts payload format."""
    from models import Part
    
    if not isinstance(parts_payload, list) or not parts_payload:
        raise ValueError('parts должен быть непустым массивом')
    sanitized = []
    for index, raw in enumerate(parts_payload, start=1):
        if not isinstance(raw, dict):
            raise ValueError('Каждая запись в parts должна быть объектом')
        part_id = raw.get('partId')
        if part_id is not None:
            try:
                part_id = int(part_id)
            except (TypeError, ValueError):
                raise ValueError('partId должен быть числом')
        is_custom = bool(raw.get('isCustom', False))
        name_value = raw.get('name')
        if isinstance(name_value, str):
            name_value = name_value.strip()
        note_value = raw.get('note')
        if isinstance(note_value, str):
            note_value = note_value.strip()
        elif note_value is not None:
            note_value = str(note_value)
        if note_value == '':
            note_value = None
        quantity_raw = raw.get('quantity', 1)
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            raise ValueError('quantity должен быть целым числом')
        if quantity <= 0:
            raise ValueError('quantity должен быть положительным числом')
        price_raw = raw.get('price')
        if price_raw is not None:
            try:
                price = float(price_raw)
            except (TypeError, ValueError):
                raise ValueError('price должен быть числом')
        else:
            price = None
        resolved_name = name_value if name_value else None
        if is_custom:
            if not resolved_name:
                raise ValueError('name обязателен для кастомной детали')
        else:
            if part_id:
                part = Part.query.get(part_id)
                if not part:
                    from app import ensure_part_catalog_seeded
                    ensure_part_catalog_seeded()
                    part = Part.query.get(part_id)
                if not part:
                    raise ValueError(f'Деталь с id {part_id} не найдена')
                if not resolved_name:
                    resolved_name = part.name_ru
            elif not resolved_name:
                raise ValueError('Для детали необходимо указать name или partId')
        sanitized.append({
            'partId': part_id,
            'name': resolved_name,
            'quantity': quantity,
            'price': price,
            'isCustom': is_custom,
            'note': note_value
        })
    return sanitized


def create_order(enable_car_number, allow_any_car_number, normalize_car_number, is_valid_car_number):
    """
    Create a new order.
    
    This function handles order creation and triggers admin notifications.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Невалидный JSON'}), 400

        required_fields = ['mechanic_name', 'telegram_id', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Отсутствует обязательное поле: {field}'}), 400

        parts_payload = data.get('parts')
        legacy_parts_payload = data.get('selected_parts')

        try:
            if parts_payload is not None:
                sanitized_parts = sanitize_parts_payload(parts_payload)
            elif legacy_parts_payload is not None:
                sanitized_parts = sanitize_legacy_parts_payload(legacy_parts_payload)
            else:
                return jsonify({'error': 'Необходимо указать parts или selected_parts'}), 400
        except ValueError as exc:
            return jsonify({'error': str(exc)}), 400

        car_number = None
        vin_value = None

        if enable_car_number:
            car_number_input = data.get('carNumber') or data.get('car_number')
            vin_input = data.get('vin')

            if vin_input is not None and not isinstance(vin_input, str):
                return jsonify({'error': 'vin должен быть строкой'}), 400

            car_number = normalize_car_number(car_number_input)
            if not car_number and vin_input:
                car_number = normalize_car_number(vin_input)

            if not car_number:
                return jsonify({'error': 'carNumber обязателен при создании заказа'}), 400

            if not is_valid_car_number(car_number):
                return jsonify({'error': 'carNumber должен содержать 4-10 символов и состоять из букв и цифр'}), 400

            vin_value = normalize_car_number(vin_input) if vin_input else car_number
        else:
            vin_input = data.get('vin')

            if vin_input is None:
                return jsonify({'error': 'Отсутствует обязательное поле: vin'}), 400

            if not isinstance(vin_input, str):
                return jsonify({'error': 'VIN должен быть строкой'}), 400

            vin_value = vin_input.strip()
            if len(vin_value) < 4:
                return jsonify({'error': 'VIN должен содержать минимум 4 символа'}), 400

            car_number = normalize_car_number(data.get('carNumber') or data.get('car_number') or vin_value)

        order = Order(
            mechanic_name=data['mechanic_name'],
            telegram_id=data['telegram_id'],
            category=data['category'],
            vin=vin_value,
            car_number=car_number,
            selected_parts=sanitized_parts,
            is_original=data.get('is_original', False),
            photo_url=data.get('photo_url'),
            language=data.get('language', 'ru')
        )

        if enable_car_number and order.car_number and not order.vin:
            order.vin = order.car_number

        db.session.add(order)
        db.session.commit()

        logger.info(f"Order created: ID={order.id}, mechanic={order.mechanic_name}")
        
        # Notify admin about new order
        try:
            from services.telegram import notify_admin_new_order
            notify_admin_new_order(order, db_session=db.session)
        except Exception as e:
            # Don't fail order creation if notification fails
            logger.error(f"Failed to send admin notification for order {order.id}: {e}")
        
        return jsonify(order.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating order: {e}")
        return jsonify({'error': 'Ошибка создания заказа'}), 500
