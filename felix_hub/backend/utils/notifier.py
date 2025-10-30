import os
import sys
import requests
from typing import Optional
from time import sleep
import logging

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
