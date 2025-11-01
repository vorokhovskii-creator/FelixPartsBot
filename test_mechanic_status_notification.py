#!/usr/bin/env python3
"""
Test script for mechanic status change notifications.
Verifies that mechanics receive Telegram notifications when order status changes.
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'felix_hub', 'backend'))

load_dotenv()

def test_mechanic_notification():
    """Test mechanic status change notification"""
    from app import app, db
    from models import Order, Mechanic
    from services.telegram import notify_mechanic_status_change
    
    with app.app_context():
        print("=" * 60)
        print("Testing Mechanic Status Change Notification")
        print("=" * 60)
        
        # Check feature flag
        is_enabled = os.getenv('ENABLE_TG_MECH_NOTIFS', 'false').lower() in ('true', '1', 'yes')
        print(f"\n✓ Feature flag ENABLE_TG_MECH_NOTIFS: {is_enabled}")
        
        if not is_enabled:
            print("⚠️  Warning: Feature flag is disabled. Enable it to test notifications.")
        
        # Find a mechanic with telegram_id
        mechanic = Mechanic.query.filter(Mechanic.telegram_id.isnot(None)).first()
        
        if not mechanic:
            print("\n❌ No mechanic with telegram_id found.")
            print("   Create a mechanic with telegram_id to test notifications:")
            print("   - Go to admin panel -> Mechanics -> Add/Edit mechanic")
            print("   - Set telegram_id field to your Telegram user ID")
            return False
        
        print(f"\n✓ Found mechanic: {mechanic.name} (ID: {mechanic.id})")
        print(f"  Telegram ID: {mechanic.telegram_id}")
        
        # Find an order assigned to this mechanic
        order = Order.query.filter_by(assigned_mechanic_id=mechanic.id).first()
        
        if not order:
            print(f"\n⚠️  No orders assigned to mechanic {mechanic.name}")
            print("   Assign an order to this mechanic in the admin panel to test.")
            
            # Try any order
            order = Order.query.first()
            if not order:
                print("\n❌ No orders found in database.")
                return False
            
            print(f"\n✓ Using order #{order.id} for testing (not assigned to mechanic)")
        else:
            print(f"\n✓ Found order #{order.id} assigned to mechanic")
        
        print(f"  Current status: {order.status}")
        print(f"  Car number: {order.car_number or order.vin or '—'}")
        print(f"  Category: {order.category}")
        
        # Test notification
        print("\n📤 Testing notification...")
        old_status = order.status
        new_status = 'в работе' if old_status != 'в работе' else 'готов'
        
        print(f"  Status change: {old_status} → {new_status}")
        
        try:
            success = notify_mechanic_status_change(
                order=order,
                old_status=old_status,
                new_status=new_status,
                mechanic=mechanic,
                db_session=db.session
            )
            
            if success:
                print("\n✅ Notification sent successfully!")
                print(f"   Check Telegram for mechanic {mechanic.name}")
                print(f"   Telegram ID: {mechanic.telegram_id}")
            else:
                print("\n⚠️  Notification failed (check logs for details)")
                print("   Common issues:")
                print("   - BOT_TOKEN not configured")
                print("   - Invalid telegram_id")
                print("   - Bot blocked by user")
                print("   - Feature flag disabled")
            
            return success
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_notification_logging():
    """Test that notifications are logged correctly"""
    from app import app, db
    from models import NotificationLog
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("Checking Notification Logs")
        print("=" * 60)
        
        # Get recent mechanic status change notifications
        logs = NotificationLog.query.filter_by(
            notification_type='mechanic_status_change'
        ).order_by(NotificationLog.sent_at.desc()).limit(5).all()
        
        if not logs:
            print("\nℹ️  No mechanic status change notifications logged yet.")
            return
        
        print(f"\n✓ Found {len(logs)} recent notification(s):\n")
        
        for log in logs:
            status = "✅ Success" if log.success else "❌ Failed"
            print(f"  {status} - Order #{log.order_id}")
            print(f"    Mechanic ID: {log.mechanic_id}")
            print(f"    Telegram ID: {log.telegram_id}")
            print(f"    Sent at: {log.sent_at}")
            if log.error_message:
                print(f"    Error: {log.error_message}")
            print()


if __name__ == '__main__':
    print("\n🔧 Mechanic Status Notification Test\n")
    
    # Check environment
    if not os.getenv('TELEGRAM_BOT_TOKEN') and not os.getenv('BOT_TOKEN'):
        print("❌ Error: TELEGRAM_BOT_TOKEN or BOT_TOKEN not set in environment")
        print("   Set it in .env file or environment variables")
        sys.exit(1)
    
    # Run tests
    success = test_mechanic_notification()
    test_notification_logging()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Test completed successfully")
    else:
        print("⚠️  Test completed with warnings (check output above)")
    print("=" * 60 + "\n")
