# Mechanics Models - Quick Start Guide

## Quick Setup

### 1. Database Initialization
The database tables are automatically created when the app starts:

```python
from app import app, db

with app.app_context():
    db.create_all()  # Creates all tables including mechanics tables
```

### 2. Seed Test Data
```bash
cd felix_hub/backend
TELEGRAM_TOKEN=test ADMIN_CHAT_ID=123 python seed_mechanics.py
```

### 3. Test Models
```bash
cd felix_hub/backend
python test_mechanics_models.py
python test_backwards_compatibility.py
```

## Quick Examples

### Create a Mechanic
```python
from models import db, Mechanic

mechanic = Mechanic(
    name="John Doe",
    email="john@example.com",
    phone="+972501234567",
    specialty="Engine",
    active=True
)
db.session.add(mechanic)
db.session.commit()
```

### Assign Mechanic to Order
```python
from models import db, Order, WorkOrderAssignment

order = Order.query.get(1)
order.assigned_mechanic_id = mechanic.id
order.work_status = 'в работе'

assignment = WorkOrderAssignment(
    order_id=order.id,
    mechanic_id=mechanic.id,
    status='in_progress'
)
db.session.add(assignment)
db.session.commit()
```

### Add Comment
```python
from models import db, OrderComment

comment = OrderComment(
    order_id=order.id,
    mechanic_id=mechanic.id,
    comment='Started working on the engine'
)
db.session.add(comment)
db.session.commit()
```

### Track Time
```python
from models import db, TimeLog
from datetime import datetime

# Start timer
time_log = TimeLog(
    order_id=order.id,
    mechanic_id=mechanic.id,
    started_at=datetime.utcnow(),
    is_active=True
)
db.session.add(time_log)
db.session.commit()

# Stop timer
time_log.ended_at = datetime.utcnow()
time_log.is_active = False
time_log.duration_minutes = int((time_log.ended_at - time_log.started_at).total_seconds() / 60)
db.session.commit()
```

### Add Custom Work
```python
from models import db, CustomWorkItem

work = CustomWorkItem(
    order_id=order.id,
    name="Oil change",
    price=100.0,
    estimated_time_minutes=30,
    added_by_mechanic_id=mechanic.id
)
db.session.add(work)
db.session.commit()
```

### Add Custom Part
```python
from models import db, CustomPartItem

part = CustomPartItem(
    order_id=order.id,
    name="Oil filter",
    part_number="OF-123",
    price=20.0,
    quantity=1,
    added_by_mechanic_id=mechanic.id
)
db.session.add(part)
db.session.commit()
```

## Query Examples

### Get Mechanic's Orders
```python
mechanic = Mechanic.query.get(1)
orders = mechanic.assigned_orders
print(f"{mechanic.name} has {len(orders)} orders")
```

### Get Order Details with All Relations
```python
order = Order.query.get(1)
print(f"Order: {order.id}")
print(f"Assigned to: {order.assigned_mechanic.name if order.assigned_mechanic else 'Unassigned'}")
print(f"Comments: {len(order.comments)}")
print(f"Time logs: {len(order.time_logs)}")
print(f"Custom works: {len(order.custom_works)}")
print(f"Custom parts: {len(order.custom_parts)}")
```

### Get Active Time Logs
```python
active_logs = TimeLog.query.filter_by(is_active=True).all()
for log in active_logs:
    print(f"{log.mechanic.name} working on order {log.order_id}")
```

### Get Mechanic's Work History
```python
mechanic = Mechanic.query.get(1)
print(f"Total assignments: {len(mechanic.assignments)}")
print(f"Total comments: {len(mechanic.comments)}")
print(f"Total time logs: {len(mechanic.time_logs)}")
```

## JSON Serialization

All models have `to_dict()` method:

```python
mechanic = Mechanic.query.get(1)
data = mechanic.to_dict()
# Returns: {'id': 1, 'name': '...', 'email': '...', ...}

order = Order.query.get(1)
data = order.to_dict()
# Includes both old and new fields

comment = OrderComment.query.get(1)
data = comment.to_dict()
# Includes mechanic_name for convenience
```

## Database Support

Works with both SQLite and PostgreSQL:

```bash
# SQLite (development)
export DATABASE_URL="sqlite:///database.db"

# PostgreSQL (production)
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

## File Locations

- **Models**: `felix_hub/backend/models.py`
- **Migration**: `felix_hub/backend/migrations/add_mechanics.py`
- **Seed Data**: `felix_hub/backend/seed_mechanics.py`
- **Tests**: 
  - `felix_hub/backend/test_mechanics_models.py`
  - `felix_hub/backend/test_backwards_compatibility.py`
- **Documentation**: 
  - `felix_hub/backend/MECHANICS_IMPLEMENTATION.md`
  - `felix_hub/backend/MECHANICS_ACCEPTANCE_CRITERIA.md`

## New Tables Summary

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `mechanics` | Mechanic profiles | name, email, specialty, active |
| `work_order_assignments` | Order assignments | order_id, mechanic_id, status |
| `order_comments` | Comments on orders | order_id, mechanic_id, comment |
| `time_logs` | Time tracking | started_at, ended_at, duration_minutes |
| `custom_work_items` | Custom work | name, price, estimated_time_minutes |
| `custom_part_items` | Custom parts | name, part_number, price, quantity |

## New Order Fields

- `assigned_mechanic_id` - FK to mechanics table
- `work_status` - новый, в работе, на паузе, завершен
- `total_time_minutes` - Total time spent
- `comments_count` - Number of comments

## Status Values

### work_status (Order)
- `новый` - New
- `в работе` - In Progress
- `на паузе` - Paused
- `завершен` - Completed

### status (WorkOrderAssignment)
- `assigned` - Assigned
- `in_progress` - In Progress
- `paused` - Paused
- `completed` - Completed

## Performance Tips

1. **Use eager loading for relationships:**
   ```python
   from sqlalchemy.orm import joinedload
   
   orders = Order.query.options(
       joinedload(Order.assigned_mechanic),
       joinedload(Order.comments)
   ).all()
   ```

2. **Indexes are automatically created** for:
   - `work_order_assignments.mechanic_id`
   - `work_order_assignments.order_id`
   - `order_comments.order_id`
   - `time_logs.mechanic_id`
   - `time_logs.is_active`

3. **Use filtering with indexed columns:**
   ```python
   # Good - uses index
   TimeLog.query.filter_by(is_active=True).all()
   
   # Good - uses index
   WorkOrderAssignment.query.filter_by(mechanic_id=1).all()
   ```

## Troubleshooting

### Tables not created?
```python
from app import app, db
with app.app_context():
    db.create_all()
```

### Import error?
```python
# Make sure you're in the right directory
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

### Database locked (SQLite)?
Close all connections and try again. Consider using PostgreSQL for production.

## Next Steps

After setting up the models, you can:
1. Create REST API endpoints (see ticket for API requirements)
2. Add authentication for mechanics
3. Build frontend interfaces
4. Add Telegram bot integration
5. Create reports and analytics

For detailed information, see `MECHANICS_IMPLEMENTATION.md`.
