#!/usr/bin/env python3
"""
Migration 001: Add car_number column to orders table
This migration adds the car_number column with index support.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text, inspect


def apply():
    """Apply the migration - add car_number column"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if orders table exists
        if 'orders' not in inspector.get_table_names():
            print("❌ Orders table does not exist. Run init_db.py first.")
            return False
        
        # Check if car_number column already exists
        columns = [col['name'] for col in inspector.get_columns('orders')]
        if 'car_number' in columns:
            print("⚠️  car_number column already exists. Skipping.")
            return True
        
        print("Adding car_number column to orders table...")
        
        # Add the column
        with db.engine.connect() as conn:
            # Add column without index first
            conn.execute(text('ALTER TABLE orders ADD COLUMN car_number VARCHAR(20)'))
            conn.commit()
            
            # Create index on car_number
            conn.execute(text('CREATE INDEX idx_orders_car_number ON orders(car_number)'))
            conn.commit()
        
        print("✅ Migration 001 applied successfully!")
        print("   - Added car_number column (VARCHAR(20))")
        print("   - Created index idx_orders_car_number")
        return True


def rollback():
    """Rollback the migration - remove car_number column"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if orders table exists
        if 'orders' not in inspector.get_table_names():
            print("⚠️  Orders table does not exist. Nothing to rollback.")
            return True
        
        # Check if car_number column exists
        columns = [col['name'] for col in inspector.get_columns('orders')]
        if 'car_number' not in columns:
            print("⚠️  car_number column does not exist. Nothing to rollback.")
            return True
        
        print("Rolling back migration 001...")
        
        # Drop the column and its index
        with db.engine.connect() as conn:
            # Drop index first (if it exists)
            try:
                conn.execute(text('DROP INDEX IF EXISTS idx_orders_car_number'))
                conn.commit()
            except Exception as e:
                print(f"⚠️  Could not drop index: {e}")
            
            # Drop column
            conn.execute(text('ALTER TABLE orders DROP COLUMN car_number'))
            conn.commit()
        
        print("✅ Migration 001 rolled back successfully!")
        print("   - Removed car_number column")
        print("   - Removed index idx_orders_car_number")
        return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback()
    else:
        apply()
