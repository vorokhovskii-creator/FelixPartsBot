#!/usr/bin/env python3
"""
Smoke Test Runner
Runs all API contract tests and E2E smoke tests.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test_suite(suite_name, test_modules):
    """Run a suite of tests"""
    print(f"\n{'='*70}")
    print(f"Running {suite_name}")
    print(f"{'='*70}\n")
    
    total_passed = 0
    total_failed = 0
    
    for module_name, module_path in test_modules:
        print(f"\n{'─'*70}")
        print(f"Module: {module_name}")
        print(f"{'─'*70}")
        
        # Import and run the test module
        spec = __import__('importlib.util').util.spec_from_file_location(module_name, module_path)
        module = __import__('importlib.util').util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
            
            # Run the tests
            if hasattr(module, 'run_all_tests'):
                success = module.run_all_tests()
                if success:
                    total_passed += 1
                else:
                    total_failed += 1
            else:
                print(f"⚠️  No run_all_tests() function found in {module_name}")
                total_failed += 1
        
        except Exception as e:
            print(f"❌ Error running {module_name}: {e}")
            import traceback
            traceback.print_exc()
            total_failed += 1
    
    return total_passed, total_failed


def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("SMOKE TESTS - Felix Hub")
    print("="*70)
    
    # Define test suites
    api_tests = [
        ('test_orders_api', os.path.join(os.path.dirname(__file__), 'api', 'test_orders_api.py')),
        ('test_categories_api', os.path.join(os.path.dirname(__file__), 'api', 'test_categories_api.py')),
        ('test_custom_parts_api', os.path.join(os.path.dirname(__file__), 'api', 'test_custom_parts_api.py')),
    ]
    
    e2e_tests = [
        ('test_order_flow_smoke', os.path.join(os.path.dirname(__file__), 'e2e', 'test_order_flow_smoke.py')),
    ]
    
    # Run API contract tests
    api_passed, api_failed = run_test_suite("API Contract Tests", api_tests)
    
    # Run E2E smoke tests
    e2e_passed, e2e_failed = run_test_suite("E2E Smoke Tests", e2e_tests)
    
    # Summary
    total_passed = api_passed + e2e_passed
    total_failed = api_failed + e2e_failed
    
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"API Tests:  {api_passed} passed, {api_failed} failed")
    print(f"E2E Tests:  {e2e_passed} passed, {e2e_failed} failed")
    print(f"{'─'*70}")
    print(f"TOTAL:      {total_passed} passed, {total_failed} failed")
    print("="*70 + "\n")
    
    if total_failed > 0:
        print("❌ Some tests failed!")
        return 1
    else:
        print("✅ All smoke tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
