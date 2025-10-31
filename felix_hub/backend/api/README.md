# API Routes

This directory contains Flask blueprints for different API modules.

## Mechanic Routes

**File**: `mechanic_routes.py`

**Prefix**: `/api/mechanic`

**Description**: REST API endpoints for mechanic functionality including authentication, order management, time tracking, comments, and custom items.

**Authentication**: JWT token required for all endpoints except `/login`

**Documentation**: See `/MECHANIC_API_DOCUMENTATION.md` in project root

### Quick Start

```python
from api.mechanic_routes import mechanic_bp
app.register_blueprint(mechanic_bp)
```

### Endpoints Summary

- Authentication (2): login, me
- Orders (3): list, details, update status
- Comments (2): add, list
- Time Tracking (4): start, stop, manual, active
- Custom Items (2): add work, add part
- Statistics (1): get stats

Total: 14 endpoints

For detailed API documentation, see `MECHANIC_API_DOCUMENTATION.md`
