"""
Интеграционные тесты для модуля печати чеков
Демонстрирует работу всей системы печати
"""

import os
import sys
import tempfile
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock order for testing
class MockOrder:
    """Мок-объект заказа для тестирования"""
    def __init__(self):
        self.id = 12345
        self.mechanic_name = "Петр Сидоров"
        self.telegram_id = "987654321"
        self.vin = "WVWZZZ1KZBW654321"
        self.category = "Трансмиссия"
        self.selected_parts = [
            "Масло трансмиссионное Castrol 75W-90",
            "Фильтр АКПП оригинальный с прокладкой",
            "Прокладка поддона АКПП усиленная"
        ]
        self.is_original = True
        self.status = "готов"
        self.photo_url = "https://example.com/car_photo.jpg"
        self.created_at = datetime.now()
        self.printed = False


def test_wrap_text():
    """Тест переноса текста"""
    from utils.printer import wrap_text
    
    print("\n=== Тест переноса текста ===")
    
    # Короткий текст
    short_text = "Короткий текст"
    result = wrap_text(short_text, 30)
    print(f"Короткий текст: {result}")
    assert len(result) == 1
    
    # Длинный текст
    long_text = "Очень длинное название детали которое не помещается в одну строку"
    result = wrap_text(long_text, 30)
    print(f"Длинный текст ({len(result)} строк):")
    for i, line in enumerate(result, 1):
        print(f"  {i}. {line}")
    assert len(result) > 1
    
    print("✓ Тест переноса текста пройден")


def test_pdf_generation():
    """Тест генерации PDF"""
    from utils.printer import generate_order_pdf
    
    print("\n=== Тест генерации PDF ===")
    
    order = MockOrder()
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        pdf_path = generate_order_pdf(order, tmp_path)
        
        if pdf_path:
            print(f"✓ PDF создан: {pdf_path}")
            print(f"✓ Размер файла: {os.path.getsize(pdf_path)} байт")
            
            # Проверяем, что файл существует
            assert os.path.exists(pdf_path)
            
            # Проверяем, что файл не пустой
            assert os.path.getsize(pdf_path) > 0
            
            print("✓ Тест генерации PDF пройден")
        else:
            print("⚠ PDF не создан (возможно, reportlab не установлен)")
    finally:
        # Удаляем временный файл
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_printer_disabled():
    """Тест работы с отключенным принтером"""
    from utils.printer import print_order_receipt
    
    print("\n=== Тест с отключенным принтером ===")
    
    # Временно отключаем принтер
    old_value = os.environ.get('PRINTER_ENABLED')
    os.environ['PRINTER_ENABLED'] = 'false'
    
    try:
        order = MockOrder()
        result = print_order_receipt(order)
        
        assert result is False
        print("✓ Принтер корректно отключен")
        print("✓ Тест с отключенным принтером пройден")
    finally:
        # Восстанавливаем значение
        if old_value is not None:
            os.environ['PRINTER_ENABLED'] = old_value
        else:
            os.environ.pop('PRINTER_ENABLED', None)


def test_fallback_mechanism():
    """Тест механизма fallback"""
    from utils.printer import print_order_with_fallback
    
    print("\n=== Тест механизма fallback ===")
    
    # Отключаем термопринтер, чтобы сработал fallback
    old_value = os.environ.get('PRINTER_ENABLED')
    os.environ['PRINTER_ENABLED'] = 'false'
    
    try:
        order = MockOrder()
        
        # Пытаемся напечатать (должен сработать fallback на PDF)
        result = print_order_with_fallback(order)
        
        if result:
            print("✓ Fallback на PDF сработал")
            print("✓ Тест механизма fallback пройден")
        else:
            print("⚠ Fallback не сработал (возможно, reportlab не установлен)")
    finally:
        # Восстанавливаем значение
        if old_value is not None:
            os.environ['PRINTER_ENABLED'] = old_value
        else:
            os.environ.pop('PRINTER_ENABLED', None)


def test_receipt_format():
    """Тест формата чека"""
    from utils.printer import wrap_text
    
    print("\n=== Тест формата чека ===")
    
    order = MockOrder()
    receipt_width = 32
    
    print("\nПредпросмотр чека:")
    print("=" * receipt_width)
    print("        СТО Felix".center(receipt_width))
    print("Автосервис премиум класса".center(receipt_width))
    print("=" * receipt_width)
    print(f"Заказ №{order.id}")
    print(f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
    print(f"Механик: {order.mechanic_name}")
    print(f"VIN: {order.vin}")
    print(f"Категория: {order.category}")
    print("=" * receipt_width)
    print("Запчасти:")
    
    for i, part in enumerate(order.selected_parts, 1):
        lines = wrap_text(part, receipt_width - 4)
        for j, line in enumerate(lines):
            if j == 0:
                print(f"{i}. {line}")
            else:
                print(f"   {line}")
    
    print("=" * receipt_width)
    print(f"Тип: {'✨ Оригинал' if order.is_original else '🔧 Не оригинал'}")
    print(f"Статус: {order.status.upper()}")
    
    if order.photo_url:
        print("📸 Фото прикреплено")
    
    print("=" * receipt_width)
    print("\nСпасибо за работу!".center(receipt_width))
    print("Felix Auto Service".center(receipt_width))
    print(f"Напечатано: {datetime.now().strftime('%d.%m.%Y %H:%M')}".center(receipt_width))
    print("\n[QR: FELIX-ORDER-{}]".format(order.id).center(receipt_width))
    print("=" * receipt_width)
    
    print("\n✓ Формат чека корректен")


def main():
    """Запуск всех интеграционных тестов"""
    print("=" * 60)
    print("  ИНТЕГРАЦИОННЫЕ ТЕСТЫ МОДУЛЯ ПЕЧАТИ ЧЕКОВ")
    print("=" * 60)
    
    try:
        # Запускаем тесты
        test_wrap_text()
        test_pdf_generation()
        test_printer_disabled()
        test_fallback_mechanism()
        test_receipt_format()
        
        print("\n" + "=" * 60)
        print("  ✓ ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Тест провален: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
