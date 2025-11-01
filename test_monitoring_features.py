#!/usr/bin/env python3
"""
Simple test to verify monitoring features are working.
Run this after deployment to verify basic functionality.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'felix_hub/backend'))


def test_imports():
    """Test that all new modules can be imported."""
    print("Testing imports...")
    
    try:
        from utils.logging_utils import StructuredLogger, generate_correlation_id, set_correlation_id
        print("✓ logging_utils imported")
    except Exception as e:
        print(f"✗ logging_utils import failed: {e}")
        return False
    
    try:
        from utils.circuit_breaker import CircuitBreaker, get_circuit_breaker
        print("✓ circuit_breaker imported")
    except Exception as e:
        print(f"✗ circuit_breaker import failed: {e}")
        return False
    
    try:
        from utils.analytics import MetricsCollector
        print("✓ analytics imported")
    except Exception as e:
        print(f"✗ analytics import failed: {e}")
        return False
    
    return True


def test_structured_logging():
    """Test structured logging functionality."""
    print("\nTesting structured logging...")
    
    try:
        from utils.logging_utils import StructuredLogger, generate_correlation_id, set_correlation_id
        
        # Generate correlation ID
        corr_id = generate_correlation_id()
        assert len(corr_id) > 0, "Correlation ID should not be empty"
        print(f"✓ Generated correlation ID: {corr_id[:8]}...")
        
        # Set correlation ID
        set_correlation_id(corr_id)
        print("✓ Set correlation ID in context")
        
        # Create structured logger
        slogger = StructuredLogger(__name__)
        print("✓ Created structured logger")
        
        # Log a test message (won't actually output in test mode)
        slogger.info("Test message", orderId=123, test=True)
        print("✓ Structured logging works")
        
        return True
    except Exception as e:
        print(f"✗ Structured logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\nTesting circuit breaker...")
    
    try:
        from utils.circuit_breaker import CircuitBreaker, CircuitState
        
        # Create a test circuit breaker
        breaker = CircuitBreaker("test", failure_threshold=2, timeout=1.0)
        print("✓ Created circuit breaker")
        
        # Check initial state
        assert breaker.get_state() == CircuitState.CLOSED, "Initial state should be CLOSED"
        print("✓ Initial state is CLOSED")
        
        # Test successful call
        def success_func():
            return "success"
        
        success, result = breaker.call(success_func)
        assert success == True, "Successful call should return True"
        assert result == "success", "Result should be returned"
        print("✓ Successful call works")
        
        # Test failed calls (without actually calling a function)
        breaker._on_failure()
        breaker._on_failure()
        assert breaker.get_state() == CircuitState.OPEN, "State should be OPEN after failures"
        print("✓ Circuit breaker opens after failures")
        
        # Get metrics
        metrics = breaker.get_metrics()
        assert metrics['state'] == 'open', "Metrics should show open state"
        print(f"✓ Circuit breaker metrics: {metrics['state']}, failures: {metrics['failure_count']}")
        
        return True
    except Exception as e:
        print(f"✗ Circuit breaker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Monitoring Features Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Structured Logging", test_structured_logging()))
    results.append(("Circuit Breaker", test_circuit_breaker()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
