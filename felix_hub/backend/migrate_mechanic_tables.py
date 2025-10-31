#!/usr/bin/env python3
"""
Migration script to add mechanic-related tables and columns
Run this script to update an existing database with new tables and columns
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text, inspect

def migrate_database():
    """Add new tables and columns for mechanic functionality"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("🔄 Starting database migration for mechanic tables...")
        print(f"📋 Existing tables: {existing_tables}")
        
        # Create all new tables
        db.create_all()
        
        # Get updated table list
        inspector = inspect(db.engine)
        new_tables = inspector.get_table_names()
        
        print(f"✅ Tables after migration: {new_tables}")
        
        # Add new columns to existing orders table if they don't exist
        existing_columns = [col['name'] for col in inspector.get_columns('orders')]
        print(f"📋 Existing columns in orders table: {existing_columns}")
        
        new_columns = {
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'assigned_mechanic_id': 'INTEGER',
            'work_status': "VARCHAR(50) DEFAULT 'новый'",
            'comments_count': 'INTEGER DEFAULT 0',
            'total_time_minutes': 'INTEGER DEFAULT 0'
        }
        
        for column_name, column_def in new_columns.items():
            if column_name not in existing_columns:
                try:
                    # SQLite syntax
                    if 'sqlite' in str(db.engine.url):
                        db.engine.execute(text(f'ALTER TABLE orders ADD COLUMN {column_name} {column_def}'))
                    # PostgreSQL syntax
                    else:
                        db.engine.execute(text(f'ALTER TABLE orders ADD COLUMN IF NOT EXISTS {column_name} {column_def}'))
                    print(f"✅ Added column: orders.{column_name}")
                except Exception as e:
                    print(f"⚠️  Column {column_name} may already exist or error: {e}")
        
        # Verify new tables were created
        new_mechanic_tables = ['mechanics', 'order_comments', 'time_logs', 
                                'custom_work_items', 'custom_part_items', 
                                'work_order_assignments']
        
        print("\n📊 Checking new tables:")
        for table in new_mechanic_tables:
            if table in new_tables:
                count = db.session.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
                print(f"✅ {table}: {count} rows")
            else:
                print(f"❌ {table}: NOT FOUND")
        
        print("\n✅ Migration completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Create a test mechanic: python create_test_mechanic.py")
        print("   2. Test the API: python test_mechanic_api.py")

if __name__ == '__main__':
    migrate_database()
