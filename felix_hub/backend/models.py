from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(120), nullable=False)
    name_he = db.Column(db.String(120))
    name_en = db.Column(db.String(120))
    icon = db.Column(db.String(10), default='🔧')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parts = db.relationship('Part', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name_ru': self.name_ru,
            'name_he': self.name_he,
            'name_en': self.name_en,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat()
        }


class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name_ru = db.Column(db.String(200), nullable=False)
    name_he = db.Column(db.String(200))
    name_en = db.Column(db.String(200))
    is_common = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name_ru': self.name_ru,
            'name_he': self.name_he,
            'name_en': self.name_en,
            'is_common': self.is_common,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat()
        }


class Mechanic(db.Model):
    __tablename__ = 'mechanics'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    telegram_id = db.Column(db.String(50), nullable=True)
    telegram_username = db.Column(db.String(120), nullable=True)
    specialty = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assigned_orders = db.relationship('Order', back_populates='assigned_mechanic')
    assignments = db.relationship('WorkOrderAssignment', foreign_keys='WorkOrderAssignment.mechanic_id', back_populates='mechanic')
    comments = db.relationship('OrderComment', back_populates='mechanic')
    time_logs = db.relationship('TimeLog', back_populates='mechanic')
    custom_works = db.relationship('CustomWorkItem', back_populates='added_by')
    custom_parts = db.relationship('CustomPartItem', back_populates='added_by')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'telegram_id': self.telegram_id,
            'telegram_username': self.telegram_username,
            'specialty': self.specialty,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    mechanic_name = db.Column(db.String(120), nullable=False)
    telegram_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    car_number = db.Column(db.String(20), nullable=True, index=True)
    vin = db.Column(db.String(50), nullable=True)
    selected_parts = db.Column(db.JSON, nullable=False)
    is_original = db.Column(db.Boolean, default=False)
    photo_url = db.Column(db.String(250), nullable=True)
    status = db.Column(db.String(50), default="новый")
    printed = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(5), default='ru')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assigned_mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=True)
    work_status = db.Column(db.String(50), default='новый')
    comments_count = db.Column(db.Integer, default=0)
    total_time_minutes = db.Column(db.Integer, default=0)
    
    assigned_mechanic = db.relationship('Mechanic', back_populates='assigned_orders')
    assignments = db.relationship('WorkOrderAssignment', back_populates='order', cascade='all, delete-orphan')
    comments = db.relationship('OrderComment', back_populates='order', order_by='OrderComment.created_at.desc()', cascade='all, delete-orphan')
    time_logs = db.relationship('TimeLog', back_populates='order', order_by='TimeLog.started_at.desc()', cascade='all, delete-orphan')
    custom_works = db.relationship('CustomWorkItem', back_populates='order', cascade='all, delete-orphan')
    custom_parts = db.relationship('CustomPartItem', back_populates='order', cascade='all, delete-orphan')
    
    @property
    def preferred_car_number(self):
        return self.car_number or self.vin
    
    def _normalized_selected_parts(self):
        items = []
        raw_parts = self.selected_parts or []
        if isinstance(raw_parts, list):
            for raw in raw_parts:
                if isinstance(raw, dict):
                    part_id = raw.get('partId', raw.get('part_id'))
                    if part_id is not None:
                        try:
                            part_id = int(part_id)
                        except (TypeError, ValueError):
                            part_id = None
                    name = raw.get('name')
                    if isinstance(name, str):
                        name = name.strip()
                    quantity_raw = raw.get('quantity', 1)
                    try:
                        quantity = int(quantity_raw)
                    except (TypeError, ValueError):
                        quantity = 1
                    if quantity <= 0:
                        quantity = 1
                    price_raw = raw.get('price')
                    if price_raw is not None:
                        try:
                            price = float(price_raw)
                        except (TypeError, ValueError):
                            price = None
                    else:
                        price = None
                    is_custom = raw.get('isCustom', raw.get('is_custom', False))
                    note_present = 'note' in raw
                    note_value = raw.get('note')
                    if note_value in (None, ''):
                        alt_note = raw.get('description') or raw.get('part_number')
                    else:
                        alt_note = note_value
                    item = {
                        'partId': part_id,
                        'name': name,
                        'quantity': quantity,
                        'price': price,
                        'isCustom': bool(is_custom)
                    }
                    if alt_note not in (None, ''):
                        item['note'] = str(alt_note)
                    elif note_present:
                        item['note'] = None
                    custom_part_id = raw.get('customPartId', raw.get('custom_part_id'))
                    if custom_part_id:
                        try:
                            item['customPartId'] = int(custom_part_id)
                        except (TypeError, ValueError):
                            pass
                    items.append(item)
                else:
                    items.append({
                        'partId': None,
                        'name': str(raw),
                        'quantity': 1,
                        'price': None,
                        'isCustom': False
                    })
        elif raw_parts:
            items.append({
                'partId': None,
                'name': str(raw_parts),
                'quantity': 1,
                'price': None,
                'isCustom': False
            })
        return items
    
    def get_part_names(self):
        return [item['name'] for item in self._normalized_selected_parts() if item.get('name')]
    
    def get_parts_payload(self, include_custom_parts=True):
        parts = self._normalized_selected_parts()
        if include_custom_parts:
            for custom_part in getattr(self, 'custom_parts', []):
                quantity = custom_part.quantity or 1
                try:
                    quantity = int(quantity)
                except (TypeError, ValueError):
                    quantity = 1
                price = custom_part.price
                if price is not None:
                    try:
                        price = float(price)
                    except (TypeError, ValueError):
                        price = None
                parts.append({
                    'partId': None,
                    'customPartId': custom_part.id,
                    'name': custom_part.name,
                    'quantity': quantity,
                    'price': price,
                    'isCustom': True,
                    'note': custom_part.part_number
                })
        return parts
    
    def to_dict(self):
        parts_payload = self.get_parts_payload()
        part_names = [p['name'] for p in parts_payload if p.get('name')]
        part_name = ', '.join(part_names)
        part_type = 'Оригинал' if self.is_original else 'Аналог'
        preferred_car_number = self.preferred_car_number
        
        return {
            'id': self.id,
            'mechanic_name': self.mechanic_name,
            'telegram_id': self.telegram_id,
            'category': self.category,
            'vin': self.vin or preferred_car_number,
            'car_number': preferred_car_number,
            'carNumber': preferred_car_number,
            'parts': parts_payload,
            'selected_parts': part_names,
            'part_name': part_name,
            'part_type': part_type,
            'is_original': self.is_original,
            'photo_url': self.photo_url,
            'status': self.status,
            'printed': self.printed,
            'language': self.language,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'assigned_mechanic_id': self.assigned_mechanic_id,
            'work_status': self.work_status,
            'comments_count': self.comments_count,
            'total_time_minutes': self.total_time_minutes
        }


class WorkOrderAssignment(db.Model):
    __tablename__ = 'work_order_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'))
    status = db.Column(db.String(20), default='assigned')
    notes = db.Column(db.Text)
    
    order = db.relationship('Order', back_populates='assignments')
    mechanic = db.relationship('Mechanic', foreign_keys=[mechanic_id], back_populates='assignments')
    assigned_by = db.relationship('Mechanic', foreign_keys=[assigned_by_id])
    
    __table_args__ = (
        Index('idx_assignments_mechanic', 'mechanic_id'),
        Index('idx_assignments_order', 'order_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
            'assigned_at': self.assigned_at.isoformat(),
            'assigned_by_id': self.assigned_by_id,
            'status': self.status,
            'notes': self.notes
        }


class OrderComment(db.Model):
    __tablename__ = 'order_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', back_populates='comments')
    mechanic = db.relationship('Mechanic', back_populates='comments')
    
    __table_args__ = (
        Index('idx_comments_order', 'order_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
            'mechanic_name': self.mechanic.name if self.mechanic else None,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }


class TimeLog(db.Model):
    __tablename__ = 'time_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', back_populates='time_logs')
    mechanic = db.relationship('Mechanic', back_populates='time_logs')
    
    __table_args__ = (
        Index('idx_time_logs_mechanic', 'mechanic_id'),
        Index('idx_time_logs_active', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
            'mechanic_name': self.mechanic.name if self.mechanic else None,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_minutes': self.duration_minutes,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class CustomWorkItem(db.Model):
    __tablename__ = 'custom_work_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    estimated_time_minutes = db.Column(db.Integer, nullable=True)
    added_by_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', back_populates='custom_works')
    added_by = db.relationship('Mechanic', back_populates='custom_works')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'estimated_time_minutes': self.estimated_time_minutes,
            'added_by_id': self.added_by_id,
            'added_by_name': self.added_by.name if self.added_by else None,
            'created_at': self.created_at.isoformat()
        }


class CustomPartItem(db.Model):
    __tablename__ = 'custom_part_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    part_number = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, default=1)
    added_by_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order = db.relationship('Order', back_populates='custom_parts')
    added_by = db.relationship('Mechanic', back_populates='custom_parts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'name': self.name,
            'part_number': self.part_number,
            'price': self.price,
            'quantity': self.quantity,
            'added_by_id': self.added_by_id,
            'added_by_name': self.added_by.name if self.added_by else None,
            'created_at': self.created_at.isoformat()
        }


class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(50), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=True)
    telegram_id = db.Column(db.String(50), nullable=False)
    message_hash = db.Column(db.String(64), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    __table_args__ = (
        Index('idx_notification_hash', 'message_hash'),
        Index('idx_notification_telegram', 'telegram_id', 'notification_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'notification_type': self.notification_type,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
            'telegram_id': self.telegram_id,
            'sent_at': self.sent_at.isoformat(),
            'success': self.success,
            'error_message': self.error_message
        }
