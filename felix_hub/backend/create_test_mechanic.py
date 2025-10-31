#!/usr/bin/env python3
"""
Script to create a test mechanic for testing the API
"""
import sys
import os
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Mechanic

def create_test_mechanic():
    with app.app_context():
        # Check if test mechanic already exists
        existing = Mechanic.query.filter_by(email='test@example.com').first()
        if existing:
            print(f"✅ Test mechanic already exists: {existing.email}")
            print(f"   ID: {existing.id}")
            print(f"   Name: {existing.name}")
            return existing
        
        # Create new test mechanic
        mechanic = Mechanic(
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            name='Тестовый Механик',
            active=True
        )
        
        db.session.add(mechanic)
        db.session.commit()
        
        print(f"✅ Test mechanic created successfully!")
        print(f"   Email: {mechanic.email}")
        print(f"   Password: password123")
        print(f"   ID: {mechanic.id}")
        print(f"   Name: {mechanic.name}")
        
        return mechanic

if __name__ == '__main__':
    create_test_mechanic()
