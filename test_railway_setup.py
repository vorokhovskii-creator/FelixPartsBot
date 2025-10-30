#!/usr/bin/env python
"""Test script to verify Railway deployment setup"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from felix_hub.backend.app import app
        print("✓ Backend app imports successfully")
    except Exception as e:
        print(f"✗ Backend app import failed: {e}")
        return False
    
    try:
        from felix_hub.backend.models import db, Order, Category, Part
        print("✓ Backend models import successfully")
    except Exception as e:
        print(f"✗ Backend models import failed: {e}")
        return False
    
    # Test bot config with dummy token
    os.environ['TELEGRAM_TOKEN'] = 'test_token_123'
    
    try:
        from felix_hub.bot.config import TELEGRAM_TOKEN, BACKEND_URL
        print("✓ Bot config imports successfully")
    except Exception as e:
        print(f"✗ Bot config import failed: {e}")
        return False
    
    try:
        from felix_hub.bot.bot import main
        print("✓ Bot module imports successfully")
    except Exception as e:
        print(f"✗ Bot module import failed: {e}")
        return False
    
    return True

def test_database_config():
    """Test database configuration"""
    print("\nTesting database configuration...")
    
    from felix_hub.backend.app import app
    
    # Test SQLite default
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        print("✓ Default SQLite configuration works")
    
    # Test PostgreSQL URL conversion
    os.environ['DATABASE_URL'] = 'postgres://user:pass@localhost/db'
    
    # Reimport to test conversion
    import importlib
    import felix_hub.backend.app as app_module
    importlib.reload(app_module)
    
    if 'postgresql://' in app_module.app.config['SQLALCHEMY_DATABASE_URI']:
        print("✓ PostgreSQL URL conversion works")
    else:
        print("✗ PostgreSQL URL conversion failed")
        return False
    
    return True

def test_health_endpoint():
    """Test that health endpoint exists"""
    print("\nTesting health endpoint...")
    
    from felix_hub.backend.app import app
    
    with app.test_client() as client:
        response = client.get('/health')
        if response.status_code == 200:
            print("✓ Health check endpoint works")
            data = response.get_json()
            print(f"  Response: {data}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False

def test_files_exist():
    """Test that all required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        'Procfile',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'felix_hub/__init__.py',
        'felix_hub/backend/__init__.py',
        'felix_hub/backend/init_db.py',
        'felix_hub/backend/app.py',
        'felix_hub/backend/models.py',
        'felix_hub/bot/__init__.py',
        'felix_hub/bot/bot.py',
        'felix_hub/bot/config.py',
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    print("=" * 60)
    print("Railway Deployment Setup Test")
    print("=" * 60)
    
    tests = [
        ("Files Check", test_files_exist),
        ("Import Test", test_imports),
        ("Database Config", test_database_config),
        ("Health Endpoint", test_health_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Ready for Railway deployment.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
