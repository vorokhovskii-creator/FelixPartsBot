import os
import sys
import logging
import time
import requests
from typing import Optional, List

# Add backend directory to path for config import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config

from utils.logging_utils import StructuredLogger, get_correlation_id
from utils.circuit_breaker import get_circuit_breaker

logger = logging.getLogger(__name__)
slogger = StructuredLogger(__name__)

MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # seconds

# Initialize circuit breaker for Telegram API
telegram_breaker = get_circuit_breaker('telegram_api', failure_threshold=10, timeout=120.0)


def _get_bot_token() -> Optional[str]:
    """Get bot token from environment."""
    return os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN')


def _get_admin_chat_ids_raw() -> str:
    """Get raw admin chat IDs from environment."""
    return os.getenv('ADMIN_CHAT_IDS', '').strip()


def _is_feature_enabled() -> bool:
    """Check if admin notifications are enabled."""
    return config.ENABLE_TG_ADMIN_NOTIFS


def _get_frontend_url() -> str:
    """Get frontend URL from environment."""
    return os.getenv('FRONTEND_URL', 'https://felix-hub.example.com')


def _get_admin_chat_ids() -> List[str]:
    """Parse and return admin chat IDs from environment variable."""
    admin_chat_ids = _get_admin_chat_ids_raw()
    if not admin_chat_ids:
        return []
    return [chat_id.strip() for chat_id in admin_chat_ids.split(',') if chat_id.strip()]


def _format_order_summary(order) -> str:
    """Format order details into a summary message."""
    try:
        part_names = []
        if hasattr(order, 'get_part_names'):
            part_names = order.get_part_names()
        elif hasattr(order, 'selected_parts'):
            raw_parts = order.selected_parts or []
            if isinstance(raw_parts, list):
                for item in raw_parts:
                    if isinstance(item, dict):
                        name = item.get('name') or item.get('label')
                        if name:
                            part_names.append(str(name))
                    else:
                        part_names.append(str(item))
        
        parts_text = "\n".join([f"  • {part}" for part in part_names]) if part_names else "  • —"
        
        car_identifier = getattr(order, 'car_number', None) or getattr(order, 'preferred_car_number', None) or getattr(order, 'vin', None) or '—'
        
        return parts_text, car_identifier
    except Exception as e:
        logger.error(f"Error formatting order summary: {e}")
        return "  • —", "—"


def _generate_admin_order_link(order_id: int) -> str:
    """Generate link to admin order page."""
    base_url = _get_frontend_url().rstrip('/')
    return f"{base_url}/#/admin/orders/{order_id}"


def _send_telegram_message(chat_id: str, message: str, parse_mode: str = 'HTML', order_id: Optional[int] = None) -> bool:
    """
    Send a message via Telegram Bot API with retry logic, exponential backoff, and circuit breaker.
    
    Args:
        chat_id: Telegram chat ID
        message: Message text
        parse_mode: Parse mode (HTML or Markdown)
        order_id: Optional order ID for structured logging
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    bot_token = _get_bot_token()
    if not bot_token:
        slogger.error("TELEGRAM_BOT_TOKEN not configured", chat_id=chat_id, orderId=order_id)
        return False
    
    if not chat_id:
        slogger.error("chat_id is empty", orderId=order_id)
        return False
    
    # Check circuit breaker before attempting
    breaker_state = telegram_breaker.get_state()
    if breaker_state.value == 'open':
        slogger.warning(
            "Telegram circuit breaker is OPEN, skipping send attempt",
            chat_id=chat_id,
            orderId=order_id
        )
        return False
    
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}"
    url = f"{telegram_api_url}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            def _make_request():
                return requests.post(url, json=payload, timeout=10)
            
            # Use circuit breaker for the actual request
            success, response = telegram_breaker.call(_make_request)
            
            if not success:
                slogger.warning(
                    "Circuit breaker rejected request",
                    chat_id=chat_id,
                    orderId=order_id,
                    attempt=attempt + 1
                )
                return False
            
            if response.status_code == 200:
                slogger.info(
                    "Telegram message sent successfully",
                    chat_id=chat_id,
                    orderId=order_id,
                    attempt=attempt + 1
                )
                return True
            elif response.status_code == 429:
                # Rate limit hit
                retry_after = response.json().get('parameters', {}).get('retry_after', BASE_RETRY_DELAY * (2 ** attempt))
                slogger.warning(
                    "Telegram rate limit hit",
                    chat_id=chat_id,
                    orderId=order_id,
                    retry_after_seconds=retry_after,
                    attempt=attempt + 1
                )
                time.sleep(retry_after)
            else:
                slogger.error(
                    "Failed to send Telegram message",
                    chat_id=chat_id,
                    orderId=order_id,
                    status_code=response.status_code,
                    error=response.text[:200],
                    attempt=attempt + 1
                )
                
                # Don't retry on client errors (4xx except 429)
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    return False
                
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    slogger.info(
                        "Retrying Telegram send",
                        chat_id=chat_id,
                        orderId=order_id,
                        delay_seconds=delay,
                        attempt=attempt + 1
                    )
                    time.sleep(delay)
                    
        except requests.exceptions.Timeout:
            slogger.error(
                "Timeout sending Telegram message",
                chat_id=chat_id,
                orderId=order_id,
                attempt=attempt + 1
            )
            if attempt < MAX_RETRIES - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            slogger.error(
                "Request error sending Telegram message",
                chat_id=chat_id,
                orderId=order_id,
                error=str(e),
                attempt=attempt + 1
            )
            if attempt < MAX_RETRIES - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
        except Exception as e:
            slogger.error(
                "Unexpected error sending Telegram message",
                chat_id=chat_id,
                orderId=order_id,
                error=str(e),
                error_type=type(e).__name__,
                attempt=attempt + 1
            )
            if attempt < MAX_RETRIES - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
    
    # Dead-letter logging
    slogger.critical(
        "DEAD_LETTER: Failed to send Telegram message after all retries",
        chat_id=chat_id,
        orderId=order_id,
        max_retries=MAX_RETRIES,
        message_preview=message[:100]
    )
    return False


def _is_mechanic_notifs_enabled() -> bool:
    """Check if mechanic status change notifications are enabled."""
    return config.ENABLE_TG_MECH_NOTIFS


def _generate_mechanic_order_link(order_id: int) -> str:
    """Generate link to mechanic order page."""
    base_url = _get_frontend_url().rstrip('/')
    return f"{base_url}/#/mechanic/orders/{order_id}"


def notify_mechanic_status_change(order, old_status: str, new_status: str, mechanic, db_session=None) -> bool:
    """
    Notify mechanic about order status change.
    
    Args:
        order: Order object from database
        old_status: Previous status
        new_status: New status
        mechanic: Mechanic object from database
        db_session: Optional database session for logging
        
    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    if not _is_mechanic_notifs_enabled():
        logger.debug("Mechanic notifications disabled via ENABLE_TG_MECH_NOTIFS flag")
        return True
    
    if not mechanic:
        logger.warning(f"No mechanic assigned to order {order.id}, notification skipped")
        return False
    
    telegram_id = mechanic.telegram_id
    if not telegram_id:
        logger.warning(f"Mechanic {mechanic.id} ({mechanic.name}) has no telegram_id, notification skipped for order {order.id}")
        if db_session:
            try:
                from models import NotificationLog
                log_entry = NotificationLog(
                    notification_type='mechanic_status_change',
                    order_id=order.id,
                    mechanic_id=mechanic.id,
                    telegram_id='',
                    message_hash=f"mechanic_status_change:{order.id}:{mechanic.id}:{new_status}",
                    success=False,
                    error_message="Mechanic has no telegram_id"
                )
                db_session.add(log_entry)
                db_session.commit()
            except Exception as e:
                logger.error(f"Error logging missing telegram_id: {e}")
        return False
    
    bot_token = _get_bot_token()
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False
    
    try:
        # Status emoji mapping
        status_emoji = {
            'новый': '🆕',
            'в работе': '⏳',
            'готов': '✅',
            'выдан': '📦'
        }
        emoji = status_emoji.get(new_status, '❓')
        
        # Format order details
        parts_text, car_identifier = _format_order_summary(order)
        mechanic_link = _generate_mechanic_order_link(order.id)
        
        # Build message
        message = (
            f"{emoji} <b>Статус заказа изменён</b>\n\n"
            f"📋 <b>Заказ #{order.id}</b>\n"
            f"🚗 <b>Номер авто:</b> {car_identifier}\n"
            f"📂 <b>Категория:</b> {order.category}\n\n"
            f"<b>Было:</b> <i>{old_status}</i>\n"
            f"<b>Стало:</b> <b>{new_status}</b>\n\n"
            f"<b>Запчасти:</b>\n{parts_text}\n\n"
            f"🔗 <a href='{mechanic_link}'>Открыть заказ</a>"
        )
        
        # Send notification with retry logic
        success = _send_telegram_message(telegram_id, message, order_id=order.id)
        
        # Log notification
        if db_session:
            try:
                from models import NotificationLog
                log_entry = NotificationLog(
                    notification_type='mechanic_status_change',
                    order_id=order.id,
                    mechanic_id=mechanic.id,
                    telegram_id=telegram_id,
                    message_hash=f"mechanic_status_change:{order.id}:{mechanic.id}:{new_status}",
                    success=success,
                    error_message=None if success else "Failed to send"
                )
                db_session.add(log_entry)
                db_session.commit()
                logger.info(f"Mechanic notification logged for order {order.id}")
            except Exception as e:
                logger.error(f"Error logging mechanic notification: {e}")
                # Don't rollback the main transaction
        
        if success:
            logger.info(
                f"Mechanic notification sent successfully for order {order.id} "
                f"to mechanic {mechanic.id} ({mechanic.name})"
            )
            return True
        else:
            logger.error(f"Failed to notify mechanic {mechanic.id} about order {order.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error in notify_mechanic_status_change for order {order.id}: {e}")
        # Don't raise - we don't want to break status update
        return False


def notify_admin_new_order(order, db_session=None) -> bool:
    """
    Notify admin chat(s) about a new order.
    
    Args:
        order: Order object from database
        db_session: Optional database session for logging
        
    Returns:
        bool: True if notification sent to at least one admin, False otherwise
    """
    if not _is_feature_enabled():
        logger.debug("Admin notifications disabled via ENABLE_TG_ADMIN_NOTIFS flag")
        return True
    
    admin_chat_ids = _get_admin_chat_ids()
    
    if not admin_chat_ids:
        logger.warning("No admin chat IDs configured in ADMIN_CHAT_IDS")
        return False
    
    bot_token = _get_bot_token()
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False
    
    try:
        # Format order details
        parts_text, car_identifier = _format_order_summary(order)
        admin_link = _generate_admin_order_link(order.id)
        
        # Build message
        message = (
            f"🆕 <b>Новый заказ #{order.id}</b>\n\n"
            f"🚗 <b>Номер авто:</b> {car_identifier}\n"
            f"👤 <b>Механик:</b> {order.mechanic_name}\n"
            f"📂 <b>Категория:</b> {order.category}\n\n"
            f"<b>Запчасти:</b>\n{parts_text}\n\n"
            f"🔗 <a href='{admin_link}'>Открыть в админ-панели</a>"
        )
        
        # Send to all admin chats
        success_count = 0
        for chat_id in admin_chat_ids:
            if _send_telegram_message(chat_id, message, order_id=order.id):
                success_count += 1
            else:
                slogger.error("Failed to notify admin chat", chat_id=chat_id, orderId=order.id)
        
        # Log notification
        if db_session:
            try:
                from models import NotificationLog
                
                for chat_id in admin_chat_ids:
                    log_entry = NotificationLog(
                        notification_type='admin_new_order',
                        order_id=order.id,
                        mechanic_id=None,
                        telegram_id=chat_id,
                        message_hash=f"admin_new_order:{order.id}:{chat_id}",
                        success=(success_count > 0),
                        error_message=None if success_count > 0 else "Failed to send to all admins"
                    )
                    db_session.add(log_entry)
                
                db_session.commit()
                logger.info(f"Admin notification logged for order {order.id}")
            except Exception as e:
                logger.error(f"Error logging admin notification: {e}")
                # Don't rollback the main transaction
        
        if success_count > 0:
            logger.info(
                f"Admin notification sent successfully for order {order.id} "
                f"({success_count}/{len(admin_chat_ids)} admins)"
            )
            return True
        else:
            logger.error(f"Failed to notify any admin about order {order.id}")
            return False
            
    except Exception as e:
        logger.error(f"Error in notify_admin_new_order for order {order.id}: {e}")
        # Don't raise - we don't want to break order creation
        return False
