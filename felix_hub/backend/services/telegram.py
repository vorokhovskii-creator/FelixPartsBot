import os
import logging
import time
import requests
from typing import Optional, List

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # seconds


def _get_bot_token() -> Optional[str]:
    """Get bot token from environment."""
    return os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('BOT_TOKEN')


def _get_admin_chat_ids_raw() -> str:
    """Get raw admin chat IDs from environment."""
    return os.getenv('ADMIN_CHAT_IDS', '').strip()


def _is_feature_enabled() -> bool:
    """Check if admin notifications are enabled."""
    return os.getenv('ENABLE_TG_ADMIN_NOTIFS', 'false').lower() in ('true', '1', 'yes')


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


def _send_telegram_message(chat_id: str, message: str, parse_mode: str = 'HTML') -> bool:
    """
    Send a message via Telegram Bot API with retry logic and exponential backoff.
    
    Args:
        chat_id: Telegram chat ID
        message: Message text
        parse_mode: Parse mode (HTML or Markdown)
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    bot_token = _get_bot_token()
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False
    
    if not chat_id:
        logger.error("chat_id is empty")
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
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Message sent successfully to admin chat {chat_id}")
                return True
            elif response.status_code == 429:
                # Rate limit hit
                retry_after = response.json().get('parameters', {}).get('retry_after', BASE_RETRY_DELAY * (2 ** attempt))
                logger.warning(f"Rate limit hit, retrying after {retry_after}s")
                time.sleep(retry_after)
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                
                # Don't retry on client errors (4xx except 429)
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    return False
                
                if attempt < MAX_RETRIES - 1:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(delay)
                    
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending message to {chat_id} (attempt {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error sending message to {chat_id}: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
        except Exception as e:
            logger.error(f"Unexpected error sending message to {chat_id}: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                time.sleep(delay)
    
    # Dead-letter logging
    logger.error(
        f"DEAD_LETTER: Failed to send message to {chat_id} after {MAX_RETRIES} attempts. "
        f"Message preview: {message[:100]}..."
    )
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
            if _send_telegram_message(chat_id, message):
                success_count += 1
            else:
                logger.error(f"Failed to notify admin chat {chat_id} about order {order.id}")
        
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
