import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.printer import (
    wrap_text,
    print_order_receipt,
    print_test_receipt,
    generate_order_pdf,
    print_order_with_fallback
)


class TestPrinterFunctions(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_order = Mock()
        self.mock_order.id = 123
        self.mock_order.mechanic_name = "Иван Иванов"
        self.mock_order.vin = "WVWZZZ1KZBW123456"
        self.mock_order.category = "Двигатель"
        self.mock_order.selected_parts = [
            "Фильтр масляный оригинальный",
            "Свечи зажигания NGK",
            "Прокладка клапанной крышки"
        ]
        self.mock_order.is_original = True
        self.mock_order.status = "готов"
        self.mock_order.photo_url = "https://example.com/photo.jpg"
        self.mock_order.created_at = datetime(2023, 10, 29, 14, 30, 0)
    
    def test_wrap_text_short(self):
        """Test wrap_text with short text"""
        result = wrap_text("Short text", 20)
        self.assertEqual(result, ["Short text"])
    
    def test_wrap_text_long(self):
        """Test wrap_text with long text"""
        text = "This is a very long text that needs to be wrapped"
        result = wrap_text(text, 20)
        self.assertTrue(len(result) > 1)
        for line in result:
            self.assertLessEqual(len(line), 20)
    
    def test_wrap_text_exact_width(self):
        """Test wrap_text with text exactly at width"""
        text = "Exactly20characters!"
        result = wrap_text(text, 20)
        self.assertEqual(result, ["Exactly20characters!"])
    
    def test_wrap_text_empty(self):
        """Test wrap_text with empty text"""
        result = wrap_text("", 20)
        self.assertEqual(result, [""])
    
    @patch.dict(os.environ, {'PRINTER_ENABLED': 'false'})
    def test_print_order_receipt_disabled(self):
        """Test print_order_receipt when printer is disabled"""
        result = print_order_receipt(self.mock_order)
        self.assertFalse(result)
    
    @patch.dict(os.environ, {'PRINTER_ENABLED': 'true', 'PRINTER_IP': '192.168.0.50', 'PRINTER_PORT': '9100'})
    @patch('escpos.printer.Network')
    def test_print_order_receipt_success(self, mock_network):
        """Test successful print_order_receipt"""
        mock_printer = MagicMock()
        mock_network.return_value = mock_printer
        
        result = print_order_receipt(self.mock_order)
        
        self.assertTrue(result)
        mock_network.assert_called_once()
        mock_printer.set.assert_called()
        mock_printer.text.assert_called()
        mock_printer.cut.assert_called_once()
    
    @patch.dict(os.environ, {'PRINTER_ENABLED': 'true', 'PRINTER_IP': '192.168.0.50'})
    @patch('escpos.printer.Network')
    def test_print_order_receipt_connection_error(self, mock_network):
        """Test print_order_receipt with connection error"""
        mock_network.side_effect = Exception("Connection refused")
        
        result = print_order_receipt(self.mock_order)
        
        self.assertFalse(result)
    
    @patch.dict(os.environ, {'PRINTER_ENABLED': 'false'})
    def test_print_test_receipt_disabled(self):
        """Test print_test_receipt when printer is disabled"""
        result = print_test_receipt()
        self.assertFalse(result)
    
    @patch.dict(os.environ, {'PRINTER_ENABLED': 'true', 'PRINTER_IP': '192.168.0.50', 'PRINTER_PORT': '9100'})
    @patch('escpos.printer.Network')
    def test_print_test_receipt_success(self, mock_network):
        """Test successful print_test_receipt"""
        mock_printer = MagicMock()
        mock_network.return_value = mock_printer
        
        result = print_test_receipt()
        
        self.assertTrue(result)
        mock_network.assert_called_once()
        mock_printer.cut.assert_called_once()
    
    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_generate_order_pdf_success(self, mock_canvas):
        """Test successful PDF generation"""
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = generate_order_pdf(self.mock_order, "/tmp/test.pdf")
        
        self.assertEqual(result, "/tmp/test.pdf")
        mock_canvas.assert_called_once()
        mock_canvas_instance.save.assert_called_once()
    
    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_generate_order_pdf_with_auto_path(self, mock_canvas):
        """Test PDF generation with automatic path"""
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = generate_order_pdf(self.mock_order)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith("/tmp/felix_order_"))
        self.assertTrue(result.endswith(".pdf"))
    
    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_generate_order_pdf_error(self, mock_canvas):
        """Test PDF generation with error"""
        mock_canvas.side_effect = Exception("PDF error")
        
        result = generate_order_pdf(self.mock_order, "/tmp/test.pdf")
        
        self.assertIsNone(result)
    
    @patch('utils.printer.print_order_receipt')
    def test_print_order_with_fallback_thermal_success(self, mock_print_receipt):
        """Test print_order_with_fallback when thermal printer works"""
        mock_print_receipt.return_value = True
        
        result = print_order_with_fallback(self.mock_order)
        
        self.assertTrue(result)
        mock_print_receipt.assert_called_once_with(self.mock_order)
    
    @patch('utils.printer.print_order_receipt')
    @patch('utils.printer.generate_order_pdf')
    def test_print_order_with_fallback_pdf_success(self, mock_pdf, mock_print_receipt):
        """Test print_order_with_fallback when thermal fails but PDF works"""
        mock_print_receipt.return_value = False
        mock_pdf.return_value = "/tmp/test.pdf"
        
        result = print_order_with_fallback(self.mock_order)
        
        self.assertTrue(result)
        mock_print_receipt.assert_called_once_with(self.mock_order)
        mock_pdf.assert_called_once_with(self.mock_order)
    
    @patch('utils.printer.print_order_receipt')
    @patch('utils.printer.generate_order_pdf')
    def test_print_order_with_fallback_both_fail(self, mock_pdf, mock_print_receipt):
        """Test print_order_with_fallback when both methods fail"""
        mock_print_receipt.return_value = False
        mock_pdf.return_value = None
        
        result = print_order_with_fallback(self.mock_order)
        
        self.assertFalse(result)
        mock_print_receipt.assert_called_once_with(self.mock_order)
        mock_pdf.assert_called_once_with(self.mock_order)


if __name__ == '__main__':
    unittest.main()
