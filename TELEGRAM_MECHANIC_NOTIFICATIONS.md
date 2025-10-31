# Telegram Mechanic Notifications & Deeplinks

## Overview

This feature integrates Telegram notifications and deeplinks for mechanics when orders are assigned or reassigned to them. Mechanics can receive notifications in Telegram and click a link to automatically open the order in the React web application.

## Features

### 1. Assignment Notifications (Backend)
- **Location**: `felix_hub/backend/utils/notifier.py`
- **Function**: `notify_mechanic_assignment(order, mechanic, is_reassignment=False, db_session=None)`
- Sends Telegram notification when order is assigned or reassigned
- Generates JWT token for auto-login
- Creates deeplink with token
- Logs notifications to prevent duplicates (15-minute window)

### 2. Duplicate Prevention
- **Table**: `notification_logs` (in `models.py`)
- Tracks sent notifications with hash of (notification_type, order_id, mechanic_id)
- Prevents duplicate notifications within 15 minutes
- Logs success/failure for debugging

### 3. Bot Commands

#### `/myorders` Command
- **Location**: `felix_hub/bot/bot.py` → `myorders_command()`
- Lists all orders assigned to the mechanic
- Shows order ID, VIN, status, and assignment date
- Provides deeplink for each order
- Limits to 10 orders with "show more" indicator

#### Deeplink Support in `/start`
- **Format**: `/start order_123`
- Handles deeplink payload in start command
- Shows order details in Telegram
- Provides link to open in web app

### 4. Frontend Deeplink Handling

#### Token-Based Auto-Login
- **Endpoint**: `/api/mechanic/token-login` (POST)
- Validates JWT token from deeplink
- Checks mechanic exists and is active
- Returns full auth token for session

#### Deeplink Flow
1. User clicks deeplink: `https://frontend.com/mechanic/orders/123?token=JWT_TOKEN`
2. `DeeplinkHandler` component intercepts URL
3. Redirects to login page with token parameter
4. `MechanicLogin` component detects token
5. Calls `/api/mechanic/token-login` with token
6. On success, saves auth token and redirects to order page
7. On failure, shows error and allows manual login

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Backend .env
FRONTEND_URL=https://your-frontend-domain.com
SECRET_KEY=your-secret-key-for-jwt

# Bot .env
FRONTEND_URL=https://your-frontend-domain.com
SECRET_KEY=your-secret-key-for-jwt  # Must match backend
```

## Database Migration

Run the migration to create the `notification_logs` table:

```bash
cd felix_hub/backend
python migrate_notification_logs.py
```

## Usage Examples

### Backend: Send Notification on Assignment

```python
from utils.notifier import notify_mechanic_assignment

# In assign_order endpoint
order = Order.query.get(order_id)
mechanic = Mechanic.query.get(mechanic_id)

# Send notification
notify_mechanic_assignment(order, mechanic, is_reassignment=False, db_session=db.session)
```

### Bot: Handle /myorders Command

User types `/myorders` in Telegram:
- Bot fetches mechanic by telegram_id
- Gets assigned orders from backend
- Generates deeplinks with tokens
- Sends formatted list with clickable links

### Frontend: Handle Deeplink

URL: `https://app.com/mechanic/orders/123?token=eyJ0eXAi...`

1. `DeeplinkHandler` detects token
2. Redirects to `/mechanic/login?token=eyJ0eXAi...&order=123`
3. `MechanicLogin` calls token-login API
4. Saves session token
5. Redirects to `/mechanic/orders/123`

## Testing

### Manual Testing Steps

1. **Create a mechanic** with `telegram_id` set
2. **Assign order** to mechanic via admin panel
3. **Check Telegram** for notification with deeplink
4. **Click deeplink** - should open order in app
5. **Run /myorders** command - should show order list

### Test Notification

```python
# In Python shell
from app import app, db
from models import Order, Mechanic
from utils.notifier import notify_mechanic_assignment

with app.app_context():
    order = Order.query.get(1)
    mechanic = Mechanic.query.filter_by(telegram_id="YOUR_TELEGRAM_ID").first()
    
    notify_mechanic_assignment(order, mechanic, db_session=db.session)
```

### Test Deeplink

1. Generate token:
```python
import jwt
import time
import os

secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
payload = {
    'mechanic_id': 1,
    'telegram_id': '123456789',
    'exp': int(time.time()) + 86400
}
token = jwt.encode(payload, secret_key, algorithm='HS256')
print(f"https://your-frontend.com/mechanic/orders/1?token={token}")
```

2. Open URL in browser
3. Should auto-login and show order

## Translations

New translations added in `felix_hub/bot/translations.py`:
- `my_assigned_orders` - Header for orders list
- `no_assigned_orders` - Empty state message
- `assigned_order_item` - Order item format
- `not_a_mechanic` - Error when user not registered
- `opening_order` - Loading message

## Security Considerations

1. **JWT Tokens**: 24-hour expiration
2. **Token Validation**: Checks mechanic_id + telegram_id match
3. **Active Check**: Only active mechanics can login
4. **HTTPS Required**: Deeplinks should use HTTPS in production
5. **Duplicate Prevention**: 15-minute window to prevent spam

## Error Handling

### Backend
- Logs all notification attempts
- Records failures in notification_logs
- Continues operation if notification fails

### Bot
- Handles API timeouts gracefully
- Shows user-friendly error messages
- Logs errors for debugging

### Frontend
- Shows toast notifications for errors
- Allows manual login if token fails
- Clear error messages in Russian

## Monitoring

Check notification logs:

```sql
SELECT 
    notification_type,
    COUNT(*) as total,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failed
FROM notification_logs
WHERE sent_at > NOW() - INTERVAL '24 hours'
GROUP BY notification_type;
```

## Troubleshooting

### Notifications Not Sent
- Check `BOT_TOKEN` is set
- Verify mechanic has `telegram_id`
- Check notification_logs table for errors
- Ensure Telegram bot is not blocked by user

### Deeplinks Not Working
- Verify `FRONTEND_URL` is set correctly
- Check `SECRET_KEY` matches between backend and bot
- Ensure JWT token not expired
- Check browser console for errors

### Token Login Fails
- Verify JWT token format
- Check expiration time
- Ensure mechanic exists and is active
- Match telegram_id in token and database

## Future Enhancements

- [ ] Push notifications for mobile app
- [ ] Email notifications as fallback
- [ ] Notification preferences per mechanic
- [ ] Read receipts for notifications
- [ ] Bulk notification sending
- [ ] Notification templates
