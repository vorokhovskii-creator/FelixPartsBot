"""
Migration script to add language field to existing orders
Run this script once to update the database schema
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')

def migrate():
    """Add language column to orders table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if column already exists
        try:
            result = conn.execute(text("SELECT language FROM orders LIMIT 1"))
            print("✅ Language column already exists")
            return
        except Exception:
            print("⚙️  Adding language column...")
        
        # Add the column with default value 'ru' for existing orders
        try:
            conn.execute(text("ALTER TABLE orders ADD COLUMN language VARCHAR(5) DEFAULT 'ru'"))
            conn.commit()
            print("✅ Language column added successfully")
            print("✅ All existing orders set to 'ru' (Russian)")
        except Exception as e:
            print(f"❌ Error adding column: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("🔧 Felix Hub - Database Migration")
    print("=" * 40)
    print("Adding 'language' field to orders table...")
    print()
    migrate()
    print()
    print("=" * 40)
    print("Migration complete!")
