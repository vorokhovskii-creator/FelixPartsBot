# Mechanics Models Implementation

## Overview

This document describes the mechanics models and database schema that have been added to support mechanic assignments, time tracking, comments, and custom work/parts tracking.

## Database Schema

### New Tables

#### 1. **mechanics** - Mechanic profiles
```sql
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR(100), NOT NULL)
- phone (VARCHAR(20))
- telegram_id (BIGINT, UNIQUE)
- telegram_username (VARCHAR(100))
- email (VARCHAR(100), UNIQUE)
- password_hash (VARCHAR(255))
- specialty (VARCHAR(100))
- active (BOOLEAN, DEFAULT TRUE)
- created_at (DATETIME)
- updated_at (DATETIME)
```

#### 2. **work_order_assignments** - Order assignments to mechanics
```sql
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY -> orders.id, NOT NULL)
- mechanic_id (INTEGER, FOREIGN KEY -> mechanics.id, NOT NULL)
- assigned_at (DATETIME)
- assigned_by_id (INTEGER, FOREIGN KEY -> mechanics.id)
- status (VARCHAR(20), DEFAULT 'assigned')
- notes (TEXT)

INDEXES:
- idx_assignments_mechanic (mechanic_id)
- idx_assignments_order (order_id)
```

#### 3. **order_comments** - Comments on orders
```sql
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY -> orders.id, NOT NULL)
- mechanic_id (INTEGER, FOREIGN KEY -> mechanics.id, NOT NULL)
- comment (TEXT, NOT NULL)
- created_at (DATETIME)

INDEXES:
- idx_comments_order (order_id)
```

#### 4. **time_logs** - Time tracking for work
```sql
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY -> orders.id, NOT NULL)
- mechanic_id (INTEGER, FOREIGN KEY -> mechanics.id, NOT NULL)
- started_at (DATETIME, NOT NULL)
- ended_at (DATETIME)
- duration_minutes (INTEGER)
- notes (TEXT)
- is_active (BOOLEAN, DEFAULT TRUE)

INDEXES:
- idx_time_logs_mechanic (mechanic_id)
- idx_time_logs_active (is_active)
```

#### 5. **custom_work_items** - Custom work added to orders
```sql
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY -> orders.id, NOT NULL)
- name (VARCHAR(200), NOT NULL)
- description (TEXT)
- price (FLOAT)
- estimated_time_minutes (INTEGER)
- added_by_mechanic_id (INTEGER, FOREIGN KEY -> mechanics.id, NOT NULL)
- created_at (DATETIME)
```

#### 6. **custom_part_items** - Custom parts added to orders
```sql
- id (INTEGER, PRIMARY KEY)
- order_id (INTEGER, FOREIGN KEY -> orders.id, NOT NULL)
- name (VARCHAR(200), NOT NULL)
- part_number (VARCHAR(100))
- price (FLOAT)
- quantity (INTEGER, DEFAULT 1)
- added_by_mechanic_id (INTEGER, FOREIGN KEY -> mechanics.id, NOT NULL)
- created_at (DATETIME)
```

### Extended Tables

#### **orders** - Extended with mechanic fields
New fields added:
```sql
- assigned_mechanic_id (INTEGER, FOREIGN KEY -> mechanics.id)
- work_status (VARCHAR(20), DEFAULT 'новый')
- total_time_minutes (INTEGER, DEFAULT 0)
- comments_count (INTEGER, DEFAULT 0)
```

## Models

### Python Models (SQLAlchemy)

All models are defined in `felix_hub/backend/models.py` and include:

- Full relationship definitions
- `to_dict()` methods for JSON serialization
- Proper indexes for performance
- Support for both SQLite (dev) and PostgreSQL (prod)

### Key Relationships

```
Mechanic
├── assigned_orders -> Order (one-to-many)
├── assignments -> WorkOrderAssignment (one-to-many)
├── comments -> OrderComment (one-to-many)
├── time_logs -> TimeLog (one-to-many)
├── custom_works -> CustomWorkItem (one-to-many)
└── custom_parts -> CustomPartItem (one-to-many)

Order
├── assigned_mechanic -> Mechanic (many-to-one)
├── assignments -> WorkOrderAssignment (one-to-many)
├── comments -> OrderComment (one-to-many, ordered by created_at desc)
├── time_logs -> TimeLog (one-to-many, ordered by started_at desc)
├── custom_works -> CustomWorkItem (one-to-many)
└── custom_parts -> CustomPartItem (one-to-many)
```

## Usage Examples

### Creating a Mechanic
```python
from models import db, Mechanic

mechanic = Mechanic(
    name="John Doe",
    phone="+972501234567",
    email="john@example.com",
    specialty="Engine Repair",
    active=True
)
db.session.add(mechanic)
db.session.commit()
```

### Assigning an Order to a Mechanic
```python
from models import db, Order, WorkOrderAssignment

order = Order.query.get(order_id)
order.assigned_mechanic_id = mechanic.id
order.work_status = 'в работе'

assignment = WorkOrderAssignment(
    order_id=order.id,
    mechanic_id=mechanic.id,
    status='in_progress',
    notes='Started engine repair'
)
db.session.add(assignment)
db.session.commit()
```

### Adding a Comment
```python
from models import db, OrderComment

comment = OrderComment(
    order_id=order.id,
    mechanic_id=mechanic.id,
    comment='Found issue with timing belt'
)
db.session.add(comment)

# Update comments count
order.comments_count = len(order.comments)
db.session.commit()
```

### Starting Time Tracking
```python
from models import db, TimeLog
from datetime import datetime

time_log = TimeLog(
    order_id=order.id,
    mechanic_id=mechanic.id,
    started_at=datetime.utcnow(),
    is_active=True,
    notes='Working on engine'
)
db.session.add(time_log)
db.session.commit()
```

### Stopping Time Tracking
```python
from datetime import datetime

time_log = TimeLog.query.filter_by(
    order_id=order.id,
    mechanic_id=mechanic.id,
    is_active=True
).first()

if time_log:
    time_log.ended_at = datetime.utcnow()
    time_log.is_active = False
    
    # Calculate duration
    duration = (time_log.ended_at - time_log.started_at).total_seconds() / 60
    time_log.duration_minutes = int(duration)
    
    # Update order total time
    order.total_time_minutes += time_log.duration_minutes
    db.session.commit()
```

### Adding Custom Work
```python
from models import db, CustomWorkItem

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
```

### Adding Custom Parts
```python
from models import db, CustomPartItem

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
```

## Database Initialization

The database is automatically initialized when the app starts. All tables are created via `db.create_all()` in the `init_database()` function in `app.py`.

## Seeding Test Data

To seed test mechanics data:

```bash
cd felix_hub/backend
python seed_mechanics.py
```

This creates 4 test mechanics:
- Иван Петров (Двигатель)
- Алексей Сидоров (Ходовая)
- Михаил Иванов (Электрика)
- Дмитрий Козлов (Диагностика)

## Running Tests

Test the models and relationships:

```bash
cd felix_hub/backend
python test_mechanics_models.py
```

Test backwards compatibility:

```bash
cd felix_hub/backend
python test_backwards_compatibility.py
```

## Migration Support

A migration script is available at `felix_hub/backend/migrations/add_mechanics.py` that:
- Creates all new tables
- Adds new columns to the orders table
- Works with both SQLite and PostgreSQL

The migration runs automatically when tables are created via `db.create_all()`.

## Performance Considerations

### Indexes
All frequently queried columns have indexes:
- `work_order_assignments`: mechanic_id, order_id
- `order_comments`: order_id
- `time_logs`: mechanic_id, is_active

### Query Optimization
- Use `order_by` in relationships for sorted results
- Lazy loading is used by default
- Use eager loading for performance when needed:
  ```python
  from sqlalchemy.orm import joinedload
  
  orders = Order.query.options(
      joinedload(Order.assigned_mechanic),
      joinedload(Order.comments)
  ).all()
  ```

## Backwards Compatibility

✅ All existing code continues to work without changes
✅ New fields have sensible defaults
✅ Existing Order queries and operations work as before
✅ to_dict() includes both old and new fields

## Database Support

✅ SQLite (development)
✅ PostgreSQL (production)

Both databases are fully supported with appropriate column types and foreign key constraints.

## Next Steps

After implementing these models, you can:
1. Create REST API endpoints for mechanics operations
2. Add authentication for mechanics
3. Build a frontend for mechanic dashboard
4. Add real-time notifications for assignments
5. Create reports and analytics

See the main ticket for API endpoint requirements.
