from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='assigned_mechanic', lazy=True)
    comments = db.relationship('OrderComment', backref='mechanic', lazy=True)
    time_logs = db.relationship('TimeLog', backref='mechanic', lazy=True)
    assignments = db.relationship('WorkOrderAssignment', backref='mechanic', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }


class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    mechanic_name = db.Column(db.String(120), nullable=False)
    telegram_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    vin = db.Column(db.String(50), nullable=False)
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
    
    comments = db.relationship('OrderComment', backref='order', lazy=True, cascade='all, delete-orphan')
    time_logs = db.relationship('TimeLog', backref='order', lazy=True, cascade='all, delete-orphan')
    custom_works = db.relationship('CustomWorkItem', backref='order', lazy=True, cascade='all, delete-orphan')
    custom_parts = db.relationship('CustomPartItem', backref='order', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('WorkOrderAssignment', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'mechanic_name': self.mechanic_name,
            'telegram_id': self.telegram_id,
            'category': self.category,
            'vin': self.vin,
            'selected_parts': self.selected_parts,
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


class OrderComment(db.Model):
    __tablename__ = 'order_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
            'mechanic_name': self.mechanic.name if self.mechanic else None
        }


class TimeLog(db.Model):
    __tablename__ = 'time_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
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
    added_by_mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    added_by_mechanic = db.relationship('Mechanic', foreign_keys=[added_by_mechanic_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'estimated_time_minutes': self.estimated_time_minutes,
            'added_by_mechanic_id': self.added_by_mechanic_id,
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
    added_by_mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    added_by_mechanic = db.relationship('Mechanic', foreign_keys=[added_by_mechanic_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'name': self.name,
            'part_number': self.part_number,
            'price': self.price,
            'quantity': self.quantity,
            'added_by_mechanic_id': self.added_by_mechanic_id,
            'created_at': self.created_at.isoformat()
        }


class WorkOrderAssignment(db.Model):
    __tablename__ = 'work_order_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=False)
    status = db.Column(db.String(50), default='assigned')
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'mechanic_id': self.mechanic_id,
            'status': self.status,
            'assigned_at': self.assigned_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
