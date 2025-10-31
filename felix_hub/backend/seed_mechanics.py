"""Seed mechanics data for testing"""
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Mechanic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_mechanics():
    """Create test mechanics in the database"""
    with app.app_context():
        try:
            existing_mechanics = Mechanic.query.all()
            if existing_mechanics:
                logger.info(f"Database already has {len(existing_mechanics)} mechanics")
                for m in existing_mechanics:
                    logger.info(f"  - {m.name} ({m.email})")
                return
            
            logger.info("Creating test mechanics...")
            
            mechanics = [
                Mechanic(
                    name="Иван Петров",
                    phone="+972501234567",
                    email="ivan@felix.com",
                    specialty="Двигатель",
                    active=True,
                    telegram_username="ivan_petrov"
                ),
                Mechanic(
                    name="Алексей Сидоров",
                    phone="+972507654321",
                    email="alex@felix.com",
                    specialty="Ходовая",
                    active=True,
                    telegram_username="alex_sidorov"
                ),
                Mechanic(
                    name="Михаил Иванов",
                    phone="+972509876543",
                    email="mikhail@felix.com",
                    specialty="Электрика",
                    active=True,
                    telegram_username="mikhail_ivanov"
                ),
                Mechanic(
                    name="Дмитрий Козлов",
                    phone="+972505551234",
                    email="dmitry@felix.com",
                    specialty="Диагностика",
                    active=True,
                    telegram_username="dmitry_kozlov"
                ),
            ]
            
            db.session.add_all(mechanics)
            db.session.commit()
            
            logger.info("✅ Successfully created test mechanics:")
            for mechanic in mechanics:
                logger.info(f"  - {mechanic.name} ({mechanic.specialty})")
            
            logger.info(f"\nTotal mechanics in database: {Mechanic.query.count()}")
            
        except Exception as e:
            logger.error(f"❌ Error seeding mechanics: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == '__main__':
    seed_mechanics()
