from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ru = db.Column(db.String(120), nullable=False)
    name_he = db.Column(db.String(120), nullable=True)
    name_en = db.Column(db.String(120), nullable=True)
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
            'parts_count': len(self.parts)
        }

class Part(db.Model):
    __tablename__ = 'parts'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name_ru = db.Column(db.String(200), nullable=False)
    name_he = db.Column(db.String(200), nullable=True)
    name_en = db.Column(db.String(200), nullable=True)
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
            'sort_order': self.sort_order
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
            'created_at': self.created_at.isoformat()
        }
