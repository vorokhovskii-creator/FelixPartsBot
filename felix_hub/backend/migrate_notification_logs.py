#!/usr/bin/env python3
"""
Migration script to add notification_logs table
"""

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import NotificationLog

def migrate():
    """Run migration"""
    with app.app_context():
        print("Creating notification_logs table...")
        
        try:
            # Create table
            db.create_all()
            print("✅ notification_logs table created successfully")
            
            # Check table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'notification_logs' in tables:
                print("✅ Verified: notification_logs table exists")
                
                # Check columns
                columns = [col['name'] for col in inspector.get_columns('notification_logs')]
                print(f"📋 Columns: {', '.join(columns)}")
                
                # Check indexes
                indexes = inspector.get_indexes('notification_logs')
                print(f"📊 Indexes: {len(indexes)} indexes created")
            else:
                print("❌ Error: notification_logs table not found")
                
        except Exception as e:
            print(f"❌ Migration error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    print("Starting notification_logs migration...")
    success = migrate()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
