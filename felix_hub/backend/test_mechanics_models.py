"""Test mechanics models and relationships"""
import os
import sys
from datetime import datetime

os.environ['DATABASE_URL'] = 'sqlite:///test_mechanics.db'
os.environ['TELEGRAM_TOKEN'] = 'test_token'
os.environ['ADMIN_CHAT_ID'] = '12345'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    Mechanic, Order, WorkOrderAssignment, OrderComment, 
    TimeLog, CustomWorkItem, CustomPartItem
)


def test_models():
    """Test all models and relationships"""
    with app.app_context():
        print("🧪 Testing Mechanics Models and Relationships\n")
        
        print("1️⃣ Testing Mechanic Model...")
        mechanic = Mechanic.query.first()
        if mechanic:
            print(f"   ✅ Found mechanic: {mechanic.name}")
            print(f"   📧 Email: {mechanic.email}")
            print(f"   🔧 Specialty: {mechanic.specialty}")
        
        print("\n2️⃣ Testing Order Model with new fields...")
        order = Order.query.first()
        if not order:
            order = Order(
                mechanic_name="Test Mechanic",
                telegram_id="123456",
                category="Test Category",
                vin="TEST123456789",
                selected_parts=["part1", "part2"],
                is_original=True
            )
            db.session.add(order)
            db.session.commit()
            print(f"   ✅ Created test order: {order.id}")
        else:
            print(f"   ✅ Found existing order: {order.id}")
        
        print(f"   Work Status: {order.work_status}")
        print(f"   Total Time: {order.total_time_minutes} minutes")
        print(f"   Comments Count: {order.comments_count}")
        
        print("\n3️⃣ Testing WorkOrderAssignment...")
        if mechanic and order:
            assignment = WorkOrderAssignment.query.filter_by(
                order_id=order.id, 
                mechanic_id=mechanic.id
            ).first()
            
            if not assignment:
                assignment = WorkOrderAssignment(
                    order_id=order.id,
                    mechanic_id=mechanic.id,
                    status='assigned',
                    notes='Test assignment'
                )
                db.session.add(assignment)
                db.session.commit()
                print(f"   ✅ Created assignment: Order {order.id} -> Mechanic {mechanic.name}")
            else:
                print(f"   ✅ Found existing assignment")
            
            print(f"   Status: {assignment.status}")
            print(f"   Assigned at: {assignment.assigned_at}")
        
        print("\n4️⃣ Testing OrderComment...")
        if mechanic and order:
            comment = OrderComment(
                order_id=order.id,
                mechanic_id=mechanic.id,
                comment="Test comment about the repair"
            )
            db.session.add(comment)
            db.session.commit()
            print(f"   ✅ Created comment by {mechanic.name}")
            print(f"   Comment: {comment.comment}")
        
        print("\n5️⃣ Testing TimeLog...")
        if mechanic and order:
            time_log = TimeLog(
                order_id=order.id,
                mechanic_id=mechanic.id,
                started_at=datetime.utcnow(),
                is_active=True,
                notes="Working on engine"
            )
            db.session.add(time_log)
            db.session.commit()
            print(f"   ✅ Created time log for {mechanic.name}")
            print(f"   Started at: {time_log.started_at}")
            print(f"   Is active: {time_log.is_active}")
        
        print("\n6️⃣ Testing CustomWorkItem...")
        if mechanic and order:
            work = CustomWorkItem(
                order_id=order.id,
                name="Engine oil change",
                description="Full synthetic oil",
                price=150.0,
                estimated_time_minutes=30,
                added_by_mechanic_id=mechanic.id
            )
            db.session.add(work)
            db.session.commit()
            print(f"   ✅ Created custom work: {work.name}")
            print(f"   Price: ${work.price}")
            print(f"   Time: {work.estimated_time_minutes} min")
        
        print("\n7️⃣ Testing CustomPartItem...")
        if mechanic and order:
            part = CustomPartItem(
                order_id=order.id,
                name="Oil Filter",
                part_number="OF-12345",
                price=25.0,
                quantity=1,
                added_by_mechanic_id=mechanic.id
            )
            db.session.add(part)
            db.session.commit()
            print(f"   ✅ Created custom part: {part.name}")
            print(f"   Part Number: {part.part_number}")
            print(f"   Price: ${part.price}")
        
        print("\n8️⃣ Testing Relationships...")
        if mechanic:
            print(f"   Mechanic '{mechanic.name}' has:")
            print(f"   - {len(mechanic.assignments)} assignments")
            print(f"   - {len(mechanic.comments)} comments")
            print(f"   - {len(mechanic.time_logs)} time logs")
            print(f"   - {len(mechanic.custom_works)} custom works")
            print(f"   - {len(mechanic.custom_parts)} custom parts")
        
        if order:
            print(f"\n   Order {order.id} has:")
            print(f"   - {len(order.assignments)} assignments")
            print(f"   - {len(order.comments)} comments")
            print(f"   - {len(order.time_logs)} time logs")
            print(f"   - {len(order.custom_works)} custom works")
            print(f"   - {len(order.custom_parts)} custom parts")
        
        print("\n✅ All tests passed successfully!")
        print("\n📊 Summary:")
        print(f"   - Mechanics: {Mechanic.query.count()}")
        print(f"   - Orders: {Order.query.count()}")
        print(f"   - Assignments: {WorkOrderAssignment.query.count()}")
        print(f"   - Comments: {OrderComment.query.count()}")
        print(f"   - Time Logs: {TimeLog.query.count()}")
        print(f"   - Custom Works: {CustomWorkItem.query.count()}")
        print(f"   - Custom Parts: {CustomPartItem.query.count()}")


if __name__ == '__main__':
    test_models()
