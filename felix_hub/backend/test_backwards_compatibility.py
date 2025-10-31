"""Test that existing code still works after adding mechanic features"""
import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///test_backwards.db'
os.environ['TELEGRAM_TOKEN'] = 'test_token'
os.environ['ADMIN_CHAT_ID'] = '12345'

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Order, Category, Part


def test_backwards_compatibility():
    """Ensure existing Order model still works as before"""
    with app.app_context():
        print("🔍 Testing Backwards Compatibility\n")
        
        print("1️⃣ Creating Order the old way (without new fields)...")
        order = Order(
            mechanic_name="Test Mechanic",
            telegram_id="123456789",
            category="Engine",
            vin="1HGBH41JXMN109186",
            selected_parts=["Oil Filter", "Air Filter"],
            is_original=True,
            status="новый"
        )
        
        db.session.add(order)
        db.session.commit()
        print(f"   ✅ Order created: ID={order.id}")
        
        print("\n2️⃣ Checking that new fields have default values...")
        print(f"   assigned_mechanic_id: {order.assigned_mechanic_id} (should be None)")
        print(f"   work_status: {order.work_status} (should be 'новый')")
        print(f"   total_time_minutes: {order.total_time_minutes} (should be 0)")
        print(f"   comments_count: {order.comments_count} (should be 0)")
        
        assert order.assigned_mechanic_id is None, "assigned_mechanic_id should default to None"
        assert order.work_status == 'новый', "work_status should default to 'новый'"
        assert order.total_time_minutes == 0, "total_time_minutes should default to 0"
        assert order.comments_count == 0, "comments_count should default to 0"
        print("   ✅ All default values are correct")
        
        print("\n3️⃣ Testing to_dict() includes new fields...")
        order_dict = order.to_dict()
        required_fields = [
            'id', 'mechanic_name', 'telegram_id', 'category', 'vin',
            'selected_parts', 'is_original', 'status', 'created_at',
            'assigned_mechanic_id', 'work_status', 'total_time_minutes', 'comments_count'
        ]
        
        for field in required_fields:
            assert field in order_dict, f"Field '{field}' missing from to_dict()"
            print(f"   ✅ {field}: {order_dict[field]}")
        
        print("\n4️⃣ Testing that old queries still work...")
        orders = Order.query.filter_by(status='новый').all()
        print(f"   ✅ Found {len(orders)} orders with status='новый'")
        
        order_by_id = Order.query.get(order.id)
        assert order_by_id is not None, "Should be able to get order by ID"
        print(f"   ✅ Retrieved order by ID: {order_by_id.id}")
        
        print("\n5️⃣ Testing update operations...")
        order.status = "в работе"
        order.work_status = "в работе"
        order.total_time_minutes = 30
        db.session.commit()
        print(f"   ✅ Updated order status and work_status")
        
        refreshed_order = Order.query.get(order.id)
        assert refreshed_order.status == "в работе"
        assert refreshed_order.work_status == "в работе"
        assert refreshed_order.total_time_minutes == 30
        print(f"   ✅ Changes persisted correctly")
        
        print("\n6️⃣ Testing delete operation...")
        db.session.delete(order)
        db.session.commit()
        deleted_order = Order.query.get(order.id)
        assert deleted_order is None, "Order should be deleted"
        print(f"   ✅ Order deleted successfully")
        
        print("\n✅ All backwards compatibility tests passed!")
        print("\n🎉 Existing code will continue to work without changes!")


if __name__ == '__main__':
    test_backwards_compatibility()
