# Mechanic API Documentation

## Overview

This document describes the REST API endpoints for the mechanic module. All endpoints use JSON for request and response bodies.

## Base URL

```
/api/mechanic
```

## Authentication

Most endpoints require JWT authentication. After logging in, include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Authentication

#### Login
```http
POST /api/mechanic/login
Content-Type: application/json

{
  "email": "mechanic@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "mechanic": {
    "id": 1,
    "email": "mechanic@example.com",
    "name": "John Mechanic",
    "active": true,
    "created_at": "2024-01-01T10:00:00"
  }
}
```

**Error (401):**
```json
{
  "error": "Неверный email или пароль"
}
```

#### Get Current Mechanic
```http
GET /api/mechanic/me
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "email": "mechanic@example.com",
  "name": "John Mechanic",
  "active": true,
  "created_at": "2024-01-01T10:00:00"
}
```

### 2. Orders

#### Get Mechanic Orders
```http
GET /api/mechanic/orders?status=в работе
Authorization: Bearer <token>
```

Query parameters:
- `status` (optional): Filter by work_status ('новый', 'в работе', 'на паузе', 'завершен')

**Response (200):**
```json
[
  {
    "id": 1,
    "mechanic_name": "Customer Name",
    "telegram_id": "123456789",
    "category": "Двигатель",
    "vin": "1HGBH41JXMN109186",
    "selected_parts": ["Масляный фильтр", "Воздушный фильтр"],
    "is_original": true,
    "photo_url": "https://...",
    "status": "новый",
    "work_status": "в работе",
    "assigned_mechanic_id": 1,
    "comments_count": 3,
    "total_time_minutes": 120,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

#### Get Order Details
```http
GET /api/mechanic/orders/{order_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "mechanic_name": "Customer Name",
  "...": "...",
  "comments": [
    {
      "id": 1,
      "order_id": 1,
      "mechanic_id": 1,
      "mechanic_name": "John Mechanic",
      "comment": "Started work on the engine",
      "created_at": "2024-01-01T10:30:00"
    }
  ],
  "time_logs": [
    {
      "id": 1,
      "order_id": 1,
      "mechanic_id": 1,
      "started_at": "2024-01-01T10:00:00",
      "ended_at": "2024-01-01T12:00:00",
      "duration_minutes": 120,
      "notes": null,
      "is_active": false,
      "created_at": "2024-01-01T10:00:00"
    }
  ],
  "custom_works": [],
  "custom_parts": []
}
```

#### Update Order Status
```http
PATCH /api/mechanic/orders/{order_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "в работе"
}
```

Valid statuses: `новый`, `в работе`, `на паузе`, `завершен`

**Response (200):**
```json
{
  "id": 1,
  "work_status": "в работе",
  "...": "..."
}
```

### 3. Comments

#### Add Comment
```http
POST /api/mechanic/orders/{order_id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "comment": "Found additional issues with the brake system"
}
```

**Response (201):**
```json
{
  "id": 5,
  "order_id": 1,
  "mechanic_id": 1,
  "mechanic_name": "John Mechanic",
  "comment": "Found additional issues with the brake system",
  "created_at": "2024-01-01T14:30:00"
}
```

#### Get Comments
```http
GET /api/mechanic/orders/{order_id}/comments
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 5,
    "order_id": 1,
    "mechanic_id": 1,
    "mechanic_name": "John Mechanic",
    "comment": "Found additional issues with the brake system",
    "created_at": "2024-01-01T14:30:00"
  }
]
```

### 4. Time Tracking

#### Start Timer
```http
POST /api/mechanic/orders/{order_id}/time/start
Authorization: Bearer <token>
```

**Response (201):**
```json
{
  "id": 3,
  "order_id": 1,
  "mechanic_id": 1,
  "started_at": "2024-01-01T15:00:00",
  "ended_at": null,
  "duration_minutes": 0,
  "notes": null,
  "is_active": true,
  "created_at": "2024-01-01T15:00:00"
}
```

**Error (400):**
```json
{
  "error": "У вас уже запущен таймер"
}
```

#### Stop Timer
```http
POST /api/mechanic/orders/{order_id}/time/stop
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 3,
  "order_id": 1,
  "mechanic_id": 1,
  "started_at": "2024-01-01T15:00:00",
  "ended_at": "2024-01-01T16:30:00",
  "duration_minutes": 90,
  "notes": null,
  "is_active": false,
  "created_at": "2024-01-01T15:00:00"
}
```

#### Add Manual Time
```http
POST /api/mechanic/orders/{order_id}/time/manual
Authorization: Bearer <token>
Content-Type: application/json

{
  "started_at": "2024-01-01T09:00:00",
  "ended_at": "2024-01-01T10:30:00",
  "duration_minutes": 90,
  "notes": "Morning work session"
}
```

**Response (201):**
```json
{
  "id": 4,
  "order_id": 1,
  "mechanic_id": 1,
  "started_at": "2024-01-01T09:00:00",
  "ended_at": "2024-01-01T10:30:00",
  "duration_minutes": 90,
  "notes": "Morning work session",
  "is_active": false,
  "created_at": "2024-01-01T15:00:00"
}
```

#### Get Active Timer
```http
GET /api/mechanic/time/active
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 3,
  "order_id": 1,
  "mechanic_id": 1,
  "started_at": "2024-01-01T15:00:00",
  "ended_at": null,
  "duration_minutes": 0,
  "notes": null,
  "is_active": true,
  "created_at": "2024-01-01T15:00:00"
}
```

Or `null` if no active timer.

### 5. Custom Work and Parts

#### Add Custom Work
```http
POST /api/mechanic/orders/{order_id}/custom-works
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Engine diagnostics",
  "description": "Full engine diagnostic check",
  "price": 150.00,
  "estimated_time_minutes": 60
}
```

**Response (201):**
```json
{
  "id": 1,
  "order_id": 1,
  "name": "Engine diagnostics",
  "description": "Full engine diagnostic check",
  "price": 150.00,
  "estimated_time_minutes": 60,
  "added_by_mechanic_id": 1,
  "created_at": "2024-01-01T15:30:00"
}
```

#### Add Custom Part
```http
POST /api/mechanic/orders/{order_id}/custom-parts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Brake pads",
  "part_number": "BP-12345",
  "price": 80.00,
  "quantity": 2
}
```

**Response (201):**
```json
{
  "id": 1,
  "order_id": 1,
  "name": "Brake pads",
  "part_number": "BP-12345",
  "price": 80.00,
  "quantity": 2,
  "added_by_mechanic_id": 1,
  "created_at": "2024-01-01T15:35:00"
}
```

### 6. Statistics

#### Get Mechanic Stats
```http
GET /api/mechanic/stats
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "active_orders": 3,
  "completed_today": 2,
  "time_today_minutes": 240
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Требуется авторизация"
}
```

```json
{
  "error": "Токен истёк"
}
```

```json
{
  "error": "Недействительный токен"
}
```

### 404 Not Found
```json
{
  "error": "Заказ не найден"
}
```

### 400 Bad Request
```json
{
  "error": "Email и пароль обязательны"
}
```

## Testing

### Create Test Mechanic

```bash
cd felix_hub/backend
python create_test_mechanic.py
```

This creates a test mechanic with:
- Email: `test@example.com`
- Password: `password123`

### Run API Tests

```bash
# Start the Flask server first
python felix_hub/backend/app.py

# In another terminal, run tests
python felix_hub/backend/test_mechanic_api.py
```

## CORS Configuration

The API is configured with CORS support for:
- Methods: GET, POST, PATCH, DELETE, OPTIONS
- Headers: Content-Type, Authorization
- Origins: Configurable via `ALLOWED_ORIGINS` environment variable

## Security Notes

1. **JWT Tokens**: Expire after 7 days
2. **Password Hashing**: Uses werkzeug's `generate_password_hash` with default settings
3. **Secret Key**: Configure via `SECRET_KEY` environment variable
4. **HTTPS**: Always use HTTPS in production to protect tokens and credentials

## Complete Request Example (curl)

```bash
# Login
TOKEN=$(curl -X POST http://localhost:5000/api/mechanic/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.token')

# Get current mechanic
curl -X GET http://localhost:5000/api/mechanic/me \
  -H "Authorization: Bearer $TOKEN"

# Get orders
curl -X GET http://localhost:5000/api/mechanic/orders \
  -H "Authorization: Bearer $TOKEN"

# Start timer
curl -X POST http://localhost:5000/api/mechanic/orders/1/time/start \
  -H "Authorization: Bearer $TOKEN"

# Add comment
curl -X POST http://localhost:5000/api/mechanic/orders/1/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment":"Working on brakes"}'
```
