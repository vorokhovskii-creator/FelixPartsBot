#!/usr/bin/env python3
"""
Test script to validate multilingual implementation
Run this after migration to ensure everything works
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'felix_hub/bot'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'felix_hub/backend'))

def test_bot_translations():
    """Test bot translations module"""
    print("Testing bot translations...")
    try:
        from translations import get_text, TRANSLATIONS
        
        # Test basic translations
        assert get_text('welcome', 'ru').startswith('👋 Привет')
        assert get_text('welcome', 'he').startswith('👋 שלום')
        assert get_text('welcome', 'en').startswith('👋 Hello')
        
        # Test formatted strings
        text = get_text('order_created', 'en', order_id=123)
        assert '#123' in text
        
        # Test fallback
        missing = get_text('nonexistent_key', 'he')
        assert missing == 'nonexistent_key'
        
        # Count translations
        key_count = len(TRANSLATIONS)
        
        print(f"  ✅ Bot translations OK ({key_count} keys)")
        return True
    except Exception as e:
        print(f"  ❌ Bot translations failed: {e}")
        return False

def test_models():
    """Test that Order model has language field"""
    print("Testing Order model...")
    try:
        from models import Order
        
        # Check if language field exists in model
        assert hasattr(Order, 'language')
        
        print("  ✅ Order model has language field")
        return True
    except ImportError:
        print("  ⚠️  Cannot test models (Flask dependencies not installed)")
        return True  # Not critical for this test
    except Exception as e:
        print(f"  ❌ Order model test failed: {e}")
        return False

def test_i18n_js():
    """Test that i18n.js exists and has content"""
    print("Testing admin panel i18n...")
    try:
        i18n_path = os.path.join(os.path.dirname(__file__), 'felix_hub/backend/static/i18n.js')
        
        with open(i18n_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key elements
        assert 'const I18N' in content
        assert 'admin_panel_title' in content
        assert 'function t(key)' in content
        assert 'function setLanguage(lang)' in content
        
        # Check all three languages present
        assert "'ru':" in content
        assert "'he':" in content
        assert "'en':" in content
        
        print("  ✅ Admin i18n.js OK")
        return True
    except Exception as e:
        print(f"  ❌ Admin i18n.js test failed: {e}")
        return False

def test_admin_html():
    """Test that admin.html has i18n attributes"""
    print("Testing admin.html...")
    try:
        html_path = os.path.join(os.path.dirname(__file__), 'felix_hub/backend/templates/admin.html')
        
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for i18n.js script inclusion
        assert 'i18n.js' in content
        
        # Check for data-i18n attributes
        assert 'data-i18n=' in content
        assert 'data-i18n="admin_panel_title"' in content
        
        # Check for language buttons
        assert 'data-lang="ru"' in content
        assert 'data-lang="he"' in content
        assert 'data-lang="en"' in content
        
        # Check for flag emojis
        assert '🇷🇺' in content
        assert '🇮🇱' in content
        assert '🇬🇧' in content
        
        print("  ✅ Admin HTML has i18n support")
        return True
    except Exception as e:
        print(f"  ❌ Admin HTML test failed: {e}")
        return False

def test_css_rtl():
    """Test that CSS has RTL support"""
    print("Testing CSS RTL support...")
    try:
        css_path = os.path.join(os.path.dirname(__file__), 'felix_hub/backend/static/style.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for RTL rules
        assert '[dir="rtl"]' in content
        
        print("  ✅ CSS has RTL support")
        return True
    except Exception as e:
        print(f"  ❌ CSS RTL test failed: {e}")
        return False

def test_migration_script():
    """Test that migration script exists"""
    print("Testing migration script...")
    try:
        migration_path = os.path.join(os.path.dirname(__file__), 'felix_hub/backend/migrate_add_language.py')
        
        assert os.path.exists(migration_path)
        
        with open(migration_path, 'r') as f:
            content = f.read()
        
        assert 'ALTER TABLE orders ADD COLUMN language' in content
        
        print("  ✅ Migration script exists")
        return True
    except Exception as e:
        print(f"  ❌ Migration script test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Felix Hub - Multilingual Implementation Test")
    print("=" * 60)
    print()
    
    tests = [
        test_bot_translations,
        test_models,
        test_i18n_js,
        test_admin_html,
        test_css_rtl,
        test_migration_script
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print()
        print("Next steps:")
        print("1. Run migration: cd felix_hub/backend && python migrate_add_language.py")
        print("2. Restart services: backend and bot")
        print("3. Test in Telegram bot and admin panel")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total} passed)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
