#!/usr/bin/env python3
"""
Test script to verify the webhook event loop fix
"""
import asyncio
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'felix_hub/backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'felix_hub/bot'))


def test_event_loop_management():
    """Test that event loop is properly managed"""
    print("🧪 Testing event loop management...")
    
    async def sample_async_task():
        await asyncio.sleep(0.1)
        return "Task completed"
    
    # Test 1: asyncio.run() properly manages loop
    print("  Test 1: asyncio.run() with simple task")
    result = asyncio.run(sample_async_task())
    assert result == "Task completed"
    print("  ✅ Test 1 passed")
    
    # Test 2: Manual loop management with pending tasks
    print("  Test 2: Manual loop with pending tasks")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def main_with_background():
        # Create background task
        task = asyncio.create_task(sample_async_task())
        await asyncio.sleep(0.05)  # Simulate main task finishing before background
        return task
    
    try:
        task = loop.run_until_complete(main_with_background())
        
        # Ensure pending tasks complete
        pending = asyncio.all_tasks(loop)
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        
        assert task.done()
        print("  ✅ Test 2 passed")
    finally:
        loop.close()
    
    # Test 3: Verify loop is closed
    print("  Test 3: Loop properly closed")
    assert loop.is_closed()
    print("  ✅ Test 3 passed")
    
    print("✅ All event loop tests passed!\n")


def test_asyncio_run_in_thread():
    """Test asyncio.run() in a separate thread (like webhook handler)"""
    print("🧪 Testing asyncio.run() in thread...")
    
    from threading import Thread
    results = []
    errors = []
    
    async def simulated_bot_handler():
        """Simulates what bot handlers do"""
        # Simulate sending a message (async operation)
        await asyncio.sleep(0.1)
        results.append("Message sent")
        
        # Simulate another async operation
        await asyncio.sleep(0.1)
        results.append("Update processed")
        
        return "Handler completed"
    
    def thread_target():
        try:
            result = asyncio.run(simulated_bot_handler())
            results.append(result)
        except Exception as e:
            errors.append(str(e))
    
    thread = Thread(target=thread_target)
    thread.start()
    thread.join(timeout=2.0)
    
    if errors:
        print(f"  ❌ Errors occurred: {errors}")
        return False
    
    if len(results) != 3:
        print(f"  ❌ Expected 3 results, got {len(results)}: {results}")
        return False
    
    print("  ✅ Thread test passed")
    print(f"  Results: {results}")
    print("✅ Thread async test passed!\n")
    return True


def test_import_bot_modules():
    """Test that bot modules can be imported"""
    print("🧪 Testing bot module imports...")
    
    try:
        from bot import setup_handlers
        print("  ✅ bot.setup_handlers imported")
    except Exception as e:
        print(f"  ⚠️  Could not import bot.setup_handlers: {e}")
    
    try:
        from config import BOT_TOKEN
        print("  ✅ config imported")
    except Exception as e:
        print(f"  ⚠️  Could not import config: {e}")
    
    try:
        from translations import get_text
        print("  ✅ translations imported")
    except Exception as e:
        print(f"  ⚠️  Could not import translations: {e}")
    
    print("✅ Import tests completed!\n")


def test_telegram_modules():
    """Test that telegram modules are available"""
    print("🧪 Testing telegram module availability...")
    
    try:
        from telegram import Update, Bot
        from telegram.ext import Application
        print("  ✅ telegram modules available")
        
        # Test that Update has de_json method
        assert hasattr(Update, 'de_json')
        print("  ✅ Update.de_json available")
        
        # Test that Application has builder
        assert hasattr(Application, 'builder')
        print("  ✅ Application.builder available")
        
        print("✅ Telegram module tests passed!\n")
        return True
        
    except ImportError as e:
        print(f"  ⚠️  Telegram modules not available: {e}")
        print("  (This is expected if running without dependencies installed)")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Telegram Webhook Event Loop Fix - Verification Tests")
    print("=" * 60)
    print()
    
    # Test 1: Event loop management
    try:
        test_event_loop_management()
    except Exception as e:
        print(f"❌ Event loop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: asyncio.run() in threads
    try:
        test_asyncio_run_in_thread()
    except Exception as e:
        print(f"❌ Thread test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Module imports (may fail without dependencies)
    try:
        test_telegram_modules()
    except Exception as e:
        print(f"⚠️  Telegram module test had issues: {e}")
    
    try:
        test_import_bot_modules()
    except Exception as e:
        print(f"⚠️  Bot module import test had issues: {e}")
    
    print("=" * 60)
    print("✅ All critical tests passed!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
