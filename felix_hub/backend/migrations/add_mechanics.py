"""Add mechanics tables and extend orders"""
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


def upgrade(db, app):
    """
    Create mechanics tables and add new columns to orders table
    This migration is designed to work with both SQLite and PostgreSQL
    """
    logger.info("Running mechanics migration...")
    
    with app.app_context():
        try:
            from models import (
                Mechanic, WorkOrderAssignment, OrderComment, 
                TimeLog, CustomWorkItem, CustomPartItem
            )
            
            logger.info("Creating new mechanics tables...")
            db.create_all()
            
            logger.info("Checking if new columns need to be added to orders table...")
            
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('orders')]
            
            new_columns = {
                'assigned_mechanic_id': 'INTEGER',
                'work_status': "VARCHAR(20) DEFAULT 'новый'",
                'total_time_minutes': 'INTEGER DEFAULT 0',
                'comments_count': 'INTEGER DEFAULT 0'
            }
            
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    logger.info(f"Adding column {column_name} to orders table...")
                    try:
                        if 'sqlite' in str(db.engine.url):
                            db.session.execute(text(f'ALTER TABLE orders ADD COLUMN {column_name} {column_type}'))
                        else:
                            if column_name == 'assigned_mechanic_id':
                                db.session.execute(text(f'ALTER TABLE orders ADD COLUMN {column_name} INTEGER REFERENCES mechanics(id)'))
                            else:
                                db.session.execute(text(f'ALTER TABLE orders ADD COLUMN {column_name} {column_type}'))
                        db.session.commit()
                        logger.info(f"✅ Column {column_name} added successfully")
                    except Exception as e:
                        logger.warning(f"Could not add column {column_name}: {e}")
                        db.session.rollback()
                else:
                    logger.info(f"Column {column_name} already exists")
            
            logger.info("✅ Mechanics migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def run_migration():
    """Standalone function to run migration from command line"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from app import app, db
    
    return upgrade(db, app)


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
