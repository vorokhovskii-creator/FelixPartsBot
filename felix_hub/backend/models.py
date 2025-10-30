from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
            'created_at': self.created_at.isoformat()
        }
