#!/usr/bin/env python
"""
Validation script for mechanics models implementation
Run this to verify all mechanics functionality is working correctly
"""
import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///validation_test.db'
os.environ['TELEGRAM_TOKEN'] = 'test_validation'
os.environ['ADMIN_CHAT_ID'] = '12345'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def cleanup():
    """Clean up test database"""
    if os.path.exists('validation_test.db'):
        os.remove('validation_test.db')

def main():
    print("=" * 70)
    print("MECHANICS MODELS VALIDATION")
    print("=" * 70)
    
    try:
        print("\n1️⃣  Importing Flask app and models...")
        from app import app, db
        from models import (
            Mechanic, Order, WorkOrderAssignment, OrderComment,
            TimeLog, CustomWorkItem, CustomPartItem
        )
        print("   ✅ All imports successful")
        
        print("\n2️⃣  Checking database initialization...")
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected = [
                'mechanics', 'work_order_assignments', 'order_comments',
                'time_logs', 'custom_work_items', 'custom_part_items'
            ]
            
            missing = [t for t in expected if t not in tables]
            if missing:
                print(f"   ❌ Missing tables: {missing}")
                return False
            
            print(f"   ✅ All {len(expected)} mechanics tables created")
        
        print("\n3️⃣  Testing model creation...")
        with app.app_context():
            # Create mechanic
            mechanic = Mechanic(
                name="Validation Test Mechanic",
                email="validation@test.com",
                specialty="Testing"
            )
            db.session.add(mechanic)
            db.session.commit()
            print(f"   ✅ Created mechanic: {mechanic.name}")
            
            # Create order
            order = Order(
                mechanic_name="Test",
                telegram_id="123",
                category="Test",
                vin="TEST123",
                selected_parts=["test"]
            )
            db.session.add(order)
            db.session.commit()
            print(f"   ✅ Created order: {order.id}")
            
            # Create assignment
            assignment = WorkOrderAssignment(
                order_id=order.id,
                mechanic_id=mechanic.id
            )
            db.session.add(assignment)
            db.session.commit()
            print(f"   ✅ Created assignment")
            
            # Create comment
            comment = OrderComment(
                order_id=order.id,
                mechanic_id=mechanic.id,
                comment="Test comment"
            )
            db.session.add(comment)
            db.session.commit()
            print(f"   ✅ Created comment")
            
            # Create time log
            from datetime import datetime
            time_log = TimeLog(
                order_id=order.id,
                mechanic_id=mechanic.id,
                started_at=datetime.utcnow(),
                is_active=True
            )
            db.session.add(time_log)
            db.session.commit()
            print(f"   ✅ Created time log")
            
            # Create custom work
            work = CustomWorkItem(
                order_id=order.id,
                name="Test Work",
                price=100.0,
                added_by_mechanic_id=mechanic.id
            )
            db.session.add(work)
            db.session.commit()
            print(f"   ✅ Created custom work item")
            
            # Create custom part
            part = CustomPartItem(
                order_id=order.id,
                name="Test Part",
                part_number="TP-123",
                price=50.0,
                added_by_mechanic_id=mechanic.id
            )
            db.session.add(part)
            db.session.commit()
            print(f"   ✅ Created custom part item")
        
        print("\n4️⃣  Testing relationships...")
        with app.app_context():
            mechanic = Mechanic.query.first()
            order = Order.query.first()
            
            checks = [
                (len(mechanic.assignments) == 1, "Mechanic assignments"),
                (len(mechanic.comments) == 1, "Mechanic comments"),
                (len(mechanic.time_logs) == 1, "Mechanic time logs"),
                (len(mechanic.custom_works) == 1, "Mechanic custom works"),
                (len(mechanic.custom_parts) == 1, "Mechanic custom parts"),
                (len(order.assignments) == 1, "Order assignments"),
                (len(order.comments) == 1, "Order comments"),
                (len(order.time_logs) == 1, "Order time logs"),
                (len(order.custom_works) == 1, "Order custom works"),
                (len(order.custom_parts) == 1, "Order custom parts"),
            ]
            
            for check, name in checks:
                if check:
                    print(f"   ✅ {name}")
                else:
                    print(f"   ❌ {name}")
                    return False
        
        print("\n5️⃣  Testing to_dict() methods...")
        with app.app_context():
            models = [
                (Mechanic.query.first(), "Mechanic"),
                (Order.query.first(), "Order"),
                (WorkOrderAssignment.query.first(), "WorkOrderAssignment"),
                (OrderComment.query.first(), "OrderComment"),
                (TimeLog.query.first(), "TimeLog"),
                (CustomWorkItem.query.first(), "CustomWorkItem"),
                (CustomPartItem.query.first(), "CustomPartItem"),
            ]
            
            for model, name in models:
                try:
                    data = model.to_dict()
                    assert isinstance(data, dict)
                    assert 'id' in data
                    print(f"   ✅ {name}.to_dict()")
                except Exception as e:
                    print(f"   ❌ {name}.to_dict(): {e}")
                    return False
        
        print("\n6️⃣  Testing indexes...")
        with app.app_context():
            inspector = inspect(db.engine)
            
            index_checks = [
                ('work_order_assignments', 2),
                ('order_comments', 1),
                ('time_logs', 2),
            ]
            
            for table, expected_count in index_checks:
                indexes = inspector.get_indexes(table)
                if len(indexes) >= expected_count:
                    print(f"   ✅ {table}: {len(indexes)} indexes")
                else:
                    print(f"   ❌ {table}: expected {expected_count}, got {len(indexes)}")
                    return False
        
        print("\n7️⃣  Testing new Order fields...")
        with app.app_context():
            order = Order.query.first()
            
            field_checks = [
                ('assigned_mechanic_id', None),
                ('work_status', 'новый'),
                ('total_time_minutes', 0),
                ('comments_count', 0),
            ]
            
            for field, default_value in field_checks:
                actual_value = getattr(order, field)
                if actual_value == default_value:
                    print(f"   ✅ {field}: {actual_value}")
                else:
                    print(f"   ❌ {field}: expected {default_value}, got {actual_value}")
                    return False
        
        print("\n" + "=" * 70)
        print("✅ ALL VALIDATION CHECKS PASSED")
        print("=" * 70)
        print("\nMechanics models are ready for production! 🎉")
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        cleanup()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
