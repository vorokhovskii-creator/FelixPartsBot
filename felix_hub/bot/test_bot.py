import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CATEGORIES, CATEGORY, PARTS_SELECTION, VIN_INPUT, ORIGINAL_CHOICE, PHOTO_UPLOAD, CONFIRMATION


class TestBotConfiguration(unittest.TestCase):
    
    def test_categories_exist(self):
        self.assertIsNotNone(CATEGORIES)
        self.assertIsInstance(CATEGORIES, dict)
        self.assertGreater(len(CATEGORIES), 0)
    
    def test_categories_structure(self):
        required_categories = [
            "🔧 Тормоза",
            "⚙️ Двигатель",
            "🔩 Подвеска",
            "⚡ Электрика",
            "💧 Расходники"
        ]
        
        for category in required_categories:
            self.assertIn(category, CATEGORIES)
            self.assertIsInstance(CATEGORIES[category], list)
            self.assertGreater(len(CATEGORIES[category]), 0)
    
    def test_brake_parts(self):
        brake_parts = CATEGORIES["🔧 Тормоза"]
        required_parts = [
            "Передние колодки",
            "Задние колодки",
            "Диски передние",
            "Диски задние",
            "Тормозная жидкость",
            "Суппорт передний",
            "Суппорт задний"
        ]
        
        for part in required_parts:
            self.assertIn(part, brake_parts)
    
    def test_engine_parts(self):
        engine_parts = CATEGORIES["⚙️ Двигатель"]
        required_parts = [
            "Масло моторное",
            "Масляный фильтр",
            "Воздушный фильтр",
            "Свечи зажигания",
            "Ремень ГРМ",
            "Помпа",
            "Термостат"
        ]
        
        for part in required_parts:
            self.assertIn(part, engine_parts)
    
    def test_suspension_parts(self):
        suspension_parts = CATEGORIES["🔩 Подвеска"]
        required_parts = [
            "Амортизаторы передние",
            "Амортизаторы задние",
            "Стойки",
            "Рычаги передние",
            "Сайлентблоки",
            "Шаровые опоры",
            "Стойки стабилизатора"
        ]
        
        for part in required_parts:
            self.assertIn(part, suspension_parts)
    
    def test_electrical_parts(self):
        electrical_parts = CATEGORIES["⚡ Электрика"]
        required_parts = [
            "Аккумулятор",
            "Генератор",
            "Стартер",
            "Проводка",
            "Предохранители",
            "Датчики",
            "Лампы"
        ]
        
        for part in required_parts:
            self.assertIn(part, electrical_parts)
    
    def test_consumables_parts(self):
        consumables = CATEGORIES["💧 Расходники"]
        required_parts = [
            "Фильтр салона",
            "Щетки стеклоочистителя",
            "Антифриз",
            "Омывающая жидкость",
            "Тормозная жидкость",
            "Масло трансмиссионное"
        ]
        
        for part in required_parts:
            self.assertIn(part, consumables)
    
    def test_conversation_states(self):
        self.assertEqual(CATEGORY, 0)
        self.assertEqual(PARTS_SELECTION, 1)
        self.assertEqual(VIN_INPUT, 2)
        self.assertEqual(ORIGINAL_CHOICE, 3)
        self.assertEqual(PHOTO_UPLOAD, 4)
        self.assertEqual(CONFIRMATION, 5)


class TestBotFunctions(unittest.TestCase):
    
    def test_bot_imports(self):
        try:
            import bot
            self.assertTrue(hasattr(bot, 'start'))
            self.assertTrue(hasattr(bot, 'select_category'))
            self.assertTrue(hasattr(bot, 'select_parts'))
            self.assertTrue(hasattr(bot, 'toggle_part'))
            self.assertTrue(hasattr(bot, 'input_vin'))
            self.assertTrue(hasattr(bot, 'process_vin'))
            self.assertTrue(hasattr(bot, 'original_choice'))
            self.assertTrue(hasattr(bot, 'upload_photo'))
            self.assertTrue(hasattr(bot, 'skip_photo'))
            self.assertTrue(hasattr(bot, 'show_confirmation'))
            self.assertTrue(hasattr(bot, 'confirm_order'))
            self.assertTrue(hasattr(bot, 'my_orders'))
            self.assertTrue(hasattr(bot, 'cancel'))
            self.assertTrue(hasattr(bot, 'main'))
        except ImportError as e:
            self.fail(f"Failed to import bot module: {e}")


class TestBotAcceptanceCriteria(unittest.TestCase):
    
    def test_all_categories_have_emojis(self):
        for category in CATEGORIES.keys():
            emoji_found = False
            for char in category:
                if ord(char) > 127:
                    emoji_found = True
                    break
            self.assertTrue(emoji_found, f"Category '{category}' should have emoji")
    
    def test_min_parts_per_category(self):
        for category, parts in CATEGORIES.items():
            self.assertGreaterEqual(len(parts), 5, f"Category '{category}' should have at least 5 parts")
    
    def test_unique_parts_per_category(self):
        for category, parts in CATEGORIES.items():
            self.assertEqual(len(parts), len(set(parts)), f"Category '{category}' has duplicate parts")


if __name__ == '__main__':
    unittest.main()
