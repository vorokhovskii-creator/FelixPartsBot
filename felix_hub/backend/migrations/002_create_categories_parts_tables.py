#!/usr/bin/env python3
"""
Migration 002: Create categories and parts tables
This migration creates the categories and parts tables with proper relationships.
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text, inspect


def apply():
    """Apply the migration - create categories and parts tables"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("Creating categories and parts tables...")
        
        # Create categories table
        if 'categories' not in existing_tables:
            print("Creating categories table...")
            with db.engine.connect() as conn:
                conn.execute(text('''
                    CREATE TABLE categories (
                        id SERIAL PRIMARY KEY,
                        name_ru VARCHAR(120) NOT NULL,
                        name_he VARCHAR(120),
                        name_en VARCHAR(120),
                        icon VARCHAR(10) DEFAULT '🔧',
                        sort_order INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                '''))
                conn.commit()
            print("   - Created categories table")
        else:
            print("⚠️  categories table already exists. Skipping.")
        
        # Create parts table
        if 'parts' not in existing_tables:
            print("Creating parts table...")
            with db.engine.connect() as conn:
                conn.execute(text('''
                    CREATE TABLE parts (
                        id SERIAL PRIMARY KEY,
                        category_id INTEGER NOT NULL,
                        name_ru VARCHAR(200) NOT NULL,
                        name_he VARCHAR(200),
                        name_en VARCHAR(200),
                        is_common BOOLEAN DEFAULT TRUE,
                        sort_order INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                    )
                '''))
                conn.commit()
                
                # Create index on category_id
                conn.execute(text('CREATE INDEX idx_parts_category_id ON parts(category_id)'))
                conn.commit()
            print("   - Created parts table")
            print("   - Created index idx_parts_category_id")
        else:
            print("⚠️  parts table already exists. Skipping.")
        
        print("✅ Migration 002 applied successfully!")
        return True


def rollback():
    """Rollback the migration - drop categories and parts tables"""
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("Rolling back migration 002...")
        
        # Drop parts table first (has foreign key to categories)
        if 'parts' in existing_tables:
            print("Dropping parts table...")
            with db.engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS parts CASCADE'))
                conn.commit()
            print("   - Dropped parts table")
        else:
            print("⚠️  parts table does not exist. Skipping.")
        
        # Drop categories table
        if 'categories' in existing_tables:
            print("Dropping categories table...")
            with db.engine.connect() as conn:
                conn.execute(text('DROP TABLE IF EXISTS categories CASCADE'))
                conn.commit()
            print("   - Dropped categories table")
        else:
            print("⚠️  categories table does not exist. Skipping.")
        
        print("✅ Migration 002 rolled back successfully!")
        return True


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback()
    else:
        apply()
