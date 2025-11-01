import os
import sys
import requests
from typing import Optional
from time import sleep
import logging
import hashlib
from datetime import datetime, timedelta

# Import translations from bot
bot_path = os.path.join(os.path.dirname(__file__), '../../bot')
sys.path.insert(0, bot_path)
try:
    from translations import get_text
except ImportError:
    # Fallback if translations not available
    def get_text(key: str, lang: str = 'ru', **kwargs) -> str:
        return key

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://felix-hub.example.com')


def send_telegram_notification(chat_id: str, message: str, parse_mode: str = 'HTML') -> bool:
    """
    Отправляет уведомление в Telegram через Bot API.
    
    Args:
        chat_id: Telegram ID получателя
        message: Текст сообщения
        parse_mode: Режим парсинга (HTML, Markdown)
        
    Returns:
        bool: True если отправлено успешно, False при ошибке
    """
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в переменных окружения")
        return False
    
    if not chat_id:
        logger.error("chat_id не указан")
        return False
    
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"Уведомление отправлено пользователю {chat_id}")
            return True
        else:
            logger.error(
                f"Ошибка отправки уведомления: {response.status_code} - {response.text}"
            )
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Таймаут при отправке уведомления пользователю {chat_id}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при отправке уведомления: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при отправке уведомления: {e}")
        return False


def notify_order_ready(order) -> bool:
    """
    Отправляет уведомление механику о готовности заказа.
    
    Args:
        order: Объект Order из базы данных
        
    Returns:
        bool: True если уведомление отправлено успешно
    """
    lang = getattr(order, 'language', 'ru') or 'ru'
    parts_list = "\n".join([f"  • {part}" for part in order.selected_parts])
    
    message = get_text('order_ready', lang,
        order_id=order.id,
        parts=parts_list,
        vin=order.vin,
        date=order.created_at.strftime('%d.%m.%Y %H:%M')
    )
    
    success = send_telegram_notification(order.telegram_id, message)
    
    if success:
        logger.info(f"Уведомление о готовности заказа №{order.id} отправлено")
    else:
        logger.warning(f"Не удалось отправить уведомление о заказе №{order.id}")
    
    return success


def notify_order_status_changed(order, old_status: str, new_status: str) -> bool:
    """
    Уведомляет механика об изменении статуса заказа.
    
    Args:
        order: Объект Order
        old_status: Предыдущий статус
        new_status: Новый статус
        
    Returns:
        bool: True если уведомление отправлено
    """
    status_emoji = {
        'новый': '🆕',
        'в работе': '⏳',
        'готов': '✅',
        'выдан': '📦'
    }
    
    emoji = status_emoji.get(new_status, '❓')
    
    message = (
        f"{emoji} <b>Статус заказа №{order.id} изменён</b>\n\n"
        f"Было: <i>{old_status}</i>\n"
        f"Стало: <b>{new_status}</b>\n\n"
        f"🚗 VIN: {order.vin}"
    )
    
    if new_status in ['готов', 'выдан']:
        return send_telegram_notification(order.telegram_id, message)
    
    return True


def send_order_delayed_notification(order) -> bool:
    """
    Уведомляет о задержке в обработке заказа.
    
    Args:
        order: Объект Order
        
    Returns:
        bool: True если уведомление отправлено
    """
    message = (
        f"⏰ <b>Заказ №{order.id}</b>\n\n"
        f"К сожалению, обработка заказа задерживается.\n"
        f"Мы свяжемся с тобой, как только запчасти будут готовы.\n\n"
        f"🚗 VIN: {order.vin}\n"
        f"Приносим извинения за неудобства! 🙏"
    )
    
    return send_telegram_notification(order.telegram_id, message)


def send_bulk_notification(telegram_ids: list, message: str) -> dict:
    """
    Отправляет массовое уведомление нескольким пользователям.
    
    Args:
        telegram_ids: Список Telegram ID получателей
        message: Текст сообщения
        
    Returns:
        dict: Статистика отправки {'success': int, 'failed': int}
    """
    results = {'success': 0, 'failed': 0}
    
    for telegram_id in telegram_ids:
        if send_telegram_notification(telegram_id, message):
            results['success'] += 1
        else:
            results['failed'] += 1
    
    logger.info(
        f"Массовая рассылка завершена: "
        f"успешно={results['success']}, ошибок={results['failed']}"
    )
    
    return results


def send_with_retry(chat_id: str, message: str, max_retries: int = 3) -> bool:
    """Отправка с повторными попытками"""
    for attempt in range(max_retries):
        if send_telegram_notification(chat_id, message):
            return True
        
        if attempt < max_retries - 1:
            sleep(2 ** attempt)
            logger.info(f"Повторная попытка {attempt + 1}/{max_retries}")
    
    return False


def _generate_message_hash(notification_type: str, order_id: int, mechanic_id: int) -> str:
    """Генерация хеша для защиты от дублирования уведомлений"""
    content = f"{notification_type}:{order_id}:{mechanic_id}"
    return hashlib.sha256(content.encode()).hexdigest()


def _check_duplicate_notification(notification_type: str, order_id: int, mechanic_id: int, db_session) -> bool:
    """
    Проверка, не было ли уже отправлено такое уведомление за последние 15 минут
    
    Returns:
        True если дубликат найден, False если уведомление можно отправить
    """
    try:
        from models import NotificationLog
        
        message_hash = _generate_message_hash(notification_type, order_id, mechanic_id)
        cutoff_time = datetime.utcnow() - timedelta(minutes=15)
        
        duplicate = NotificationLog.query.filter(
            NotificationLog.message_hash == message_hash,
            NotificationLog.sent_at > cutoff_time,
            NotificationLog.success == True
        ).first()
        
        return duplicate is not None
    except Exception as e:
        logger.warning(f"Error checking duplicate notification: {e}")
        return False


def _log_notification(notification_type: str, telegram_id: str, order_id: int = None, 
                      mechanic_id: int = None, success: bool = True, 
                      error_message: str = None, db_session=None):
    """Логирование отправленного уведомления"""
    try:
        from models import NotificationLog
        
        message_hash = _generate_message_hash(notification_type, order_id or 0, mechanic_id or 0)
        
        log_entry = NotificationLog(
            notification_type=notification_type,
            order_id=order_id,
            mechanic_id=mechanic_id,
            telegram_id=telegram_id,
            message_hash=message_hash,
            success=success,
            error_message=error_message
        )
        
        if db_session:
            db_session.add(log_entry)
            db_session.commit()
            logger.info(f"Notification logged: {notification_type} for mechanic {mechanic_id}, order {order_id}")
    except Exception as e:
        logger.error(f"Error logging notification: {e}")


def _generate_deeplink(order_id: int, mechanic_token: str = None) -> str:
    """Генерация deeplink для перехода к заказу"""
    base_url = FRONTEND_URL.rstrip('/')
    path = f"/mechanic/orders/{order_id}"

    if mechanic_token:
        path = f"{path}?token={mechanic_token}"

    return f"{base_url}/#{path}"


def _generate_mechanic_token(mechanic_id: int, telegram_id: str) -> str:
    """Генерация временного токена для механика"""
    import jwt
    import time
    
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    payload = {
        'mechanic_id': mechanic_id,
        'telegram_id': telegram_id,
        'exp': int(time.time()) + 86400  # 24 hours
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def notify_mechanic_assignment(order, mechanic, is_reassignment: bool = False, db_session=None) -> bool:
    """
    Уведомление механика о назначении или переназначении заказа
    
    Args:
        order: Объект Order
        mechanic: Объект Mechanic
        is_reassignment: True если это переназначение
        db_session: SQLAlchemy session для логирования
        
    Returns:
        bool: True если уведомление отправлено успешно
    """
    notification_type = 'mechanic_reassignment' if is_reassignment else 'mechanic_assignment'
    
    # Проверка дубликата
    if db_session and _check_duplicate_notification(notification_type, order.id, mechanic.id, db_session):
        logger.info(f"Duplicate notification prevented: {notification_type} for order {order.id}, mechanic {mechanic.id}")
        return True
    
    # Получить telegram_id механика
    telegram_id = mechanic.telegram_id
    
    if not telegram_id:
        logger.warning(f"Mechanic {mechanic.id} has no telegram_id, notification skipped")
        if db_session:
            _log_notification(notification_type, '', order.id, mechanic.id, 
                            success=False, error_message="No telegram_id", db_session=db_session)
        return False
    
    # Генерация токена для автологина
    try:
        mechanic_token = _generate_mechanic_token(mechanic.id, telegram_id)
    except Exception as e:
        logger.error(f"Error generating mechanic token: {e}")
        mechanic_token = None
    
    # Генерация deeplink
    deeplink = _generate_deeplink(order.id, mechanic_token)
    
    # Формирование сообщения
    action_text = "переназначен" if is_reassignment else "назначен"
    emoji = "🔄" if is_reassignment else "🔔"
    
    parts_list = "\n".join([f"  • {part}" for part in order.selected_parts[:5]])
    if len(order.selected_parts) > 5:
        parts_list += f"\n  ... и ещё {len(order.selected_parts) - 5}"
    
    message = (
        f"{emoji} <b>Новый заказ {action_text} на вас!</b>\n\n"
        f"📋 Заказ №{order.id}\n"
        f"🚗 VIN: {order.vin}\n"
        f"📦 Категория: {order.category}\n\n"
        f"<b>Запчасти:</b>\n{parts_list}\n\n"
        f"🔗 <a href='{deeplink}'>Открыть заказ в приложении</a>"
    )
    
    # Отправка уведомления
    success = send_telegram_notification(telegram_id, message)
    
    # Логирование
    if db_session:
        _log_notification(
            notification_type, 
            telegram_id, 
            order.id, 
            mechanic.id, 
            success=success,
            error_message=None if success else "Failed to send",
            db_session=db_session
        )
    
    if success:
        logger.info(f"Assignment notification sent for order {order.id} to mechanic {mechanic.id}")
    else:
        logger.warning(f"Failed to send assignment notification for order {order.id} to mechanic {mechanic.id}")
    
    return success
