import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Конфигурация принтера из ENV
PRINTER_IP = os.getenv('PRINTER_IP', '192.168.0.50')
PRINTER_PORT = int(os.getenv('PRINTER_PORT', 9100))
PRINTER_ENABLED = os.getenv('PRINTER_ENABLED', 'false').lower() == 'true'
RECEIPT_WIDTH = int(os.getenv('RECEIPT_WIDTH', 32))  # 32 символа для 58мм, 48 для 80мм


def print_order_receipt(order) -> bool:
    """
    Печатает чек заказа на термопринтере ESC/POS.
    
    Args:
        order: Объект Order из базы данных
        
    Returns:
        bool: True если печать успешна, False при ошибке
    """
    if not PRINTER_ENABLED:
        logger.info("Печать отключена (PRINTER_ENABLED=false)")
        return False
    
    try:
        from escpos.printer import Network
        
        # Подключение к принтеру
        printer = Network(PRINTER_IP, port=PRINTER_PORT)
        logger.info(f"Подключение к принтеру {PRINTER_IP}:{PRINTER_PORT}")
        
        # --- ЗАГОЛОВОК ---
        printer.set(align='center', bold=True, double_height=True, double_width=True)
        printer.text("СТО Felix\n")
        
        printer.set(align='center', bold=False, double_height=False, double_width=False)
        printer.text("Автосервис премиум класса\n")
        printer.text("=" * RECEIPT_WIDTH + "\n")
        
        # --- ИНФОРМАЦИЯ О ЗАКАЗЕ ---
        printer.set(align='left', bold=True)
        printer.text(f"Заказ №{order.id}\n")
        
        printer.set(bold=False)
        printer.text(f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n")
        printer.text(f"Механик: {order.mechanic_name}\n")
        car_number_value = getattr(order, 'preferred_car_number', None) or getattr(order, 'car_number', None) or getattr(order, 'vin', None)
        if car_number_value:
            printer.text(f"Номер авто: {car_number_value}\n")
        if getattr(order, 'vin', None) and order.vin != car_number_value:
            printer.text(f"VIN: {order.vin}\n")
        printer.text(f"Категория: {order.category}\n")
        printer.text("=" * RECEIPT_WIDTH + "\n")
        
        # --- СПИСОК ДЕТАЛЕЙ ---
        printer.set(bold=True)
        printer.text("Запчасти:\n")
        printer.set(bold=False)
        
        for i, part in enumerate(order.selected_parts or [], 1):
            # Перенос длинных названий
            lines = wrap_text(part, RECEIPT_WIDTH - 4)
            for j, line in enumerate(lines):
                if j == 0:
                    printer.text(f"{i}. {line}\n")
                else:
                    printer.text(f"   {line}\n")
        
        printer.text("=" * RECEIPT_WIDTH + "\n")
        
        # --- ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ---
        printer.text(f"Тип: {'✨ Оригинал' if order.is_original else '🔧 Не оригинал'}\n")
        printer.text(f"Статус: {order.status.upper()}\n")
        
        if order.photo_url:
            printer.text("📸 Фото прикреплено\n")
        
        printer.text("=" * RECEIPT_WIDTH + "\n")
        
        # --- ФУТЕР ---
        printer.set(align='center')
        printer.text("\nСпасибо за работу!\n")
        printer.text("Felix Auto Service\n")
        printer.text(f"Напечатано: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        printer.text("\n")
        
        # --- QR-код с ID заказа (опционально) ---
        try:
            printer.qr(f"FELIX-ORDER-{order.id}", size=6)
        except Exception as e:
            logger.warning(f"Не удалось напечатать QR-код: {e}")
        
        # Отрезать чек
        printer.cut()
        
        logger.info(f"Чек заказа №{order.id} успешно напечатан")
        return True
        
    except ImportError:
        logger.error("python-escpos не установлен. Установите: pip install python-escpos")
        return False
    except Exception as e:
        logger.error(f"Ошибка печати заказа №{order.id}: {e}")
        return False


def wrap_text(text: str, width: int) -> list:
    """
    Переносит длинный текст на несколько строк.
    
    Args:
        text: Исходный текст
        width: Максимальная ширина строки
        
    Returns:
        list: Список строк
    """
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= width:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())
    
    return lines if lines else [text[:width]]


def print_test_receipt() -> bool:
    """
    Печатает тестовый чек для проверки принтера.
    
    Returns:
        bool: True если печать успешна
    """
    if not PRINTER_ENABLED:
        logger.info("Печать отключена")
        return False
    
    try:
        from escpos.printer import Network
        
        printer = Network(PRINTER_IP, port=PRINTER_PORT)
        
        printer.set(align='center', bold=True, double_height=True)
        printer.text("ТЕСТОВАЯ ПЕЧАТЬ\n")
        
        printer.set(align='center', bold=False, double_height=False)
        printer.text("=" * RECEIPT_WIDTH + "\n")
        printer.text("Принтер работает корректно\n")
        printer.text(f"IP: {PRINTER_IP}:{PRINTER_PORT}\n")
        printer.text(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        printer.text("=" * RECEIPT_WIDTH + "\n\n")
        
        printer.cut()
        
        logger.info("Тестовый чек напечатан")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестовой печати: {e}")
        return False


# ========== АЛЬТЕРНАТИВА: PDF для обычного принтера ==========

def generate_order_pdf(order, output_path: Optional[str] = None) -> Optional[str]:
    """
    Генерирует PDF-чек для печати на обычном принтере.
    
    Args:
        order: Объект Order
        output_path: Путь для сохранения PDF
        
    Returns:
        str: Путь к созданному PDF или None при ошибке
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
        
        if not output_path:
            output_path = f"/tmp/felix_order_{order.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        y = height - 50*mm
        
        # Заголовок
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, y, "СТО Felix")
        y -= 10*mm
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, y, "Автосервис премиум класса")
        y -= 15*mm
        
        # Информация о заказе
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50*mm, y, f"Заказ №{order.id}")
        y -= 8*mm
        
        c.setFont("Helvetica", 11)
        c.drawString(50*mm, y, f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
        y -= 6*mm
        c.drawString(50*mm, y, f"Механик: {order.mechanic_name}")
        y -= 6*mm
        car_number_value = getattr(order, 'preferred_car_number', None) or getattr(order, 'car_number', None) or getattr(order, 'vin', None)
        if car_number_value:
            c.drawString(50*mm, y, f"Номер авто: {car_number_value}")
            y -= 6*mm
        if getattr(order, 'vin', None) and order.vin != car_number_value:
            c.drawString(50*mm, y, f"VIN: {order.vin}")
            y -= 6*mm
        c.drawString(50*mm, y, f"Категория: {order.category}")
        y -= 10*mm
        
        # Линия
        c.line(50*mm, y, width-50*mm, y)
        y -= 8*mm
        
        # Список деталей
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50*mm, y, "Запчасти:")
        y -= 8*mm
        
        c.setFont("Helvetica", 11)
        for i, part in enumerate(order.selected_parts or [], 1):
            c.drawString(50*mm, y, f"{i}. {part}")
            y -= 6*mm
        
        y -= 5*mm
        c.line(50*mm, y, width-50*mm, y)
        y -= 8*mm
        
        # Дополнительная информация
        c.drawString(50*mm, y, f"Тип: {'Оригинал' if order.is_original else 'Не оригинал'}")
        y -= 6*mm
        c.drawString(50*mm, y, f"Статус: {order.status.upper()}")
        y -= 15*mm
        
        # Футер
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, y, "Спасибо за работу!")
        y -= 5*mm
        c.drawCentredString(width/2, y, "Felix Auto Service")
        
        c.save()
        
        logger.info(f"PDF-чек для заказа №{order.id} создан: {output_path}")
        return output_path
        
    except ImportError:
        logger.error("reportlab не установлен. Установите: pip install reportlab")
        return None
    except Exception as e:
        logger.error(f"Ошибка создания PDF для заказа №{order.id}: {e}")
        return None


def print_order_with_fallback(order) -> bool:
    """
    Пытается напечатать на термопринтере, при ошибке создает PDF.
    
    Args:
        order: Объект Order
        
    Returns:
        bool: True если хотя бы один метод сработал
    """
    # Сначала пробуем термопринтер
    if print_order_receipt(order):
        return True
    
    # Если не получилось, создаем PDF
    logger.warning(f"Термопринтер недоступен, создаю PDF для заказа №{order.id}")
    pdf_path = generate_order_pdf(order)
    
    if pdf_path:
        logger.info(f"PDF создан, можно распечатать вручную: {pdf_path}")
        return True
    
    logger.error(f"Не удалось напечатать заказ №{order.id} ни одним методом")
    return False
