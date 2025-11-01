# Telegram Admin Notifications

This feature enables automatic Telegram notifications to admin chats whenever a new order is created.

## Overview

When a mechanic submits a new order through the Telegram bot or web interface, the system automatically sends a notification to configured admin chat(s) with order details.

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Telegram bot token (can use either variable name)
TELEGRAM_BOT_TOKEN=your_bot_token_here
BOT_TOKEN=your_bot_token_here

# Comma-separated list of admin Telegram chat IDs
ADMIN_CHAT_IDS=123456789,987654321

# Feature flag to enable/disable admin notifications
ENABLE_TG_ADMIN_NOTIFS=true
```

### Getting Admin Chat IDs

1. Add your Telegram bot to a group chat or get the bot's chat ID with the admin
2. Send a message to the bot
3. Use the Telegram Bot API to get updates: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Look for the `chat.id` field in the response
5. Add the chat ID(s) to `ADMIN_CHAT_IDS`

## Features

### Notification Content

Each notification includes:
- **Order ID**: Unique identifier for the order
- **Car Number**: Vehicle identifier (car number or VIN)
- **Mechanic**: Name of the mechanic who created the order
- **Category**: Parts category
- **Parts List**: Summary of requested parts
- **Admin Link**: Direct link to view order in admin panel

### Retry Logic

The notification system includes robust error handling:
- **Exponential Backoff**: Retries with 1s, 2s delays on failure
- **Rate Limit Handling**: Respects Telegram API rate limits (429 errors)
- **Dead Letter Logging**: Failed messages are logged for manual review
- **Graceful Degradation**: Order creation succeeds even if notification fails

### Database Logging

All notification attempts are logged to the `notification_logs` table:
- Notification type: `admin_new_order`
- Order ID reference
- Target chat ID
- Success/failure status
- Error messages (if any)

## API Integration

The notification is triggered in `backend/api/orders.py` after successful order creation:

```python
from services.telegram import notify_admin_new_order

# After order is saved to database
notify_admin_new_order(order, db_session=db.session)
```

## Testing

Run the test suite:

```bash
python tests/services/test_telegram_notifications.py
```

The tests cover:
- Message formatting
- Retry logic with exponential backoff
- Rate limit handling
- Feature flag behavior
- Database logging
- Error handling

## Disabling Notifications

To disable admin notifications:

1. Set `ENABLE_TG_ADMIN_NOTIFS=false` in your `.env` file
2. Or remove the `ENABLE_TG_ADMIN_NOTIFS` variable (defaults to false)

## Troubleshooting

### Notifications not sending

1. Check that `ENABLE_TG_ADMIN_NOTIFS=true` is set
2. Verify `TELEGRAM_BOT_TOKEN` or `BOT_TOKEN` is configured
3. Confirm `ADMIN_CHAT_IDS` contains valid chat IDs
4. Check application logs for error messages
5. Review `notification_logs` table for failed attempts

### Rate limiting

If you experience rate limiting:
- The system automatically retries with exponential backoff
- Telegram allows ~30 messages/second to different chats
- Failed messages are logged to `notification_logs`

### Testing in development

Set up a test environment:

```bash
# Use a test bot token
TELEGRAM_BOT_TOKEN=test_bot_token

# Use your personal chat ID for testing
ADMIN_CHAT_IDS=your_chat_id

# Enable notifications
ENABLE_TG_ADMIN_NOTIFS=true
```

## Architecture

```
Order Creation Flow:
1. Client POSTs to /api/orders
2. backend/api/orders.py validates and creates Order
3. Order saved to database (commit)
4. services/telegram.py sends notification to admins
5. Notification logged to notification_logs table
6. Response returned to client (regardless of notification result)
```

## Files

- `felix_hub/backend/services/telegram.py` - Notification service
- `felix_hub/backend/api/orders.py` - Order creation endpoint
- `tests/services/test_telegram_notifications.py` - Test suite
- `.env.example` - Configuration template
