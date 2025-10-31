# Mechanic API Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
cd felix_hub/backend
python migrate_mechanic_tables.py
```

### 3. Create Test Mechanic
```bash
python create_test_mechanic.py
```

This creates:
- **Email**: `test@example.com`
- **Password**: `password123`

### 4. Start Server
```bash
python app.py
```

Server will start on `http://localhost:5000`

### 5. Test API
```bash
# In another terminal
python test_mechanic_api.py
```

## 📋 All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/mechanic/login` | Login and get JWT token |
| `GET` | `/api/mechanic/me` | Get current mechanic info |
| `GET` | `/api/mechanic/orders` | List mechanic's orders |
| `GET` | `/api/mechanic/orders/:id` | Get order details |
| `PATCH` | `/api/mechanic/orders/:id/status` | Update order status |
| `POST` | `/api/mechanic/orders/:id/comments` | Add comment |
| `GET` | `/api/mechanic/orders/:id/comments` | Get comments |
| `POST` | `/api/mechanic/orders/:id/time/start` | Start timer |
| `POST` | `/api/mechanic/orders/:id/time/stop` | Stop timer |
| `POST` | `/api/mechanic/orders/:id/time/manual` | Add manual time |
| `GET` | `/api/mechanic/time/active` | Get active timer |
| `POST` | `/api/mechanic/orders/:id/custom-works` | Add custom work |
| `POST` | `/api/mechanic/orders/:id/custom-parts` | Add custom part |
| `GET` | `/api/mechanic/stats` | Get statistics |

## 💻 Quick Test with cURL

```bash
# 1. Login
curl -X POST http://localhost:5000/api/mechanic/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Save the token from response, then:

# 2. Get current mechanic
curl -X GET http://localhost:5000/api/mechanic/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 3. Get orders
curl -X GET http://localhost:5000/api/mechanic/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 4. Get statistics
curl -X GET http://localhost:5000/api/mechanic/stats \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔧 Frontend Integration

### Login
```javascript
const response = await fetch('/api/mechanic/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'mechanic@example.com',
    password: 'password123'
  })
});

const { token, mechanic } = await response.json();
localStorage.setItem('token', token);
```

### Protected Request
```javascript
const token = localStorage.getItem('token');

const response = await fetch('/api/mechanic/orders', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const orders = await response.json();
```

## 📁 Key Files

- `felix_hub/backend/models.py` - Database models
- `felix_hub/backend/auth.py` - JWT authentication
- `felix_hub/backend/api/mechanic_routes.py` - API endpoints
- `felix_hub/backend/app.py` - Main Flask application
- `MECHANIC_API_DOCUMENTATION.md` - Full API documentation

## 🎯 Common Tasks

### Create New Mechanic
```python
from werkzeug.security import generate_password_hash
from models import Mechanic, db

mechanic = Mechanic(
    email='mechanic@example.com',
    password_hash=generate_password_hash('password'),
    name='John Doe',
    active=True
)
db.session.add(mechanic)
db.session.commit()
```

### Assign Order to Mechanic
```python
order = Order.query.get(order_id)
order.assigned_mechanic_id = mechanic_id
order.work_status = 'новый'
db.session.commit()
```

### Check Active Timers
```python
active_timers = TimeLog.query.filter_by(
    mechanic_id=mechanic_id,
    is_active=True
).all()
```

## 🔐 Environment Variables

```bash
# .env file
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///database.db
ALLOWED_ORIGINS=http://localhost:3000
PORT=5000
```

## 🐛 Troubleshooting

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Table doesn't exist"
```bash
python migrate_mechanic_tables.py
```

### "401 Unauthorized"
- Check if token is valid
- Token expires after 7 days
- Login again to get new token

### "400 Bad Request"
- Check request body format
- Ensure required fields are provided
- Verify JSON is valid

## 📚 Documentation

- **Full API Docs**: `MECHANIC_API_DOCUMENTATION.md`
- **Implementation Summary**: `MECHANIC_API_IMPLEMENTATION_SUMMARY.md`
- **Model Reference**: `felix_hub/backend/models.py`

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Database migrated
- [ ] Test mechanic created
- [ ] Server running
- [ ] API tests passing
- [ ] Frontend can login
- [ ] Orders loading correctly
- [ ] Timer working
- [ ] Comments posting

---

**Ready to use!** 🎉

For detailed information, see `MECHANIC_API_DOCUMENTATION.md`
