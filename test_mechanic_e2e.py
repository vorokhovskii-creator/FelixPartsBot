#!/usr/bin/env python3
"""
Comprehensive E2E Test Suite for Mechanic Module
Tests backend API and validates frontend integration points
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
API_BASE = f'{BASE_URL}/api'

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log_test(name: str, passed: bool, message: str = ''):
    global tests_passed, tests_failed
    
    if passed:
        tests_passed += 1
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}"
    else:
        tests_failed += 1
        status = f"{Colors.RED}✗ FAIL{Colors.RESET}"
    
    result = {
        'name': name,
        'passed': passed,
        'message': message
    }
    test_results.append(result)
    
    print(f"  {status} {name}")
    if message and not passed:
        print(f"    {Colors.YELLOW}{message}{Colors.RESET}")

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")

class MechanicE2ETest:
    def __init__(self):
        self.token: Optional[str] = None
        self.mechanic_id: Optional[int] = None
        self.test_order_id: Optional[int] = None
        
    def run_all_tests(self):
        """Run all E2E tests"""
        print(f"\n{Colors.BOLD}Starting Mechanic Module E2E Tests{Colors.RESET}")
        print(f"Target: {BASE_URL}\n")
        
        # Test groups
        self.test_authentication()
        
        if self.token:
            self.test_dashboard()
            self.test_order_details()
            self.test_time_tracking()
            self.test_profile()
            self.test_error_handling()
        
        self.print_summary()
    
    def test_authentication(self):
        """Test authentication and protected routes"""
        print_section("1. AUTHENTICATION & PROTECTED ROUTES")
        
        # Test 1.1: Login with invalid credentials
        try:
            response = requests.post(f'{API_BASE}/mechanic/login', json={
                'email': 'invalid@example.com',
                'password': 'wrongpass'
            }, timeout=5)
            log_test(
                "Invalid credentials return 401",
                response.status_code == 401,
                f"Expected 401, got {response.status_code}"
            )
        except Exception as e:
            log_test("Invalid credentials return 401", False, str(e))
        
        # Test 1.2: Login with valid credentials
        try:
            response = requests.post(f'{API_BASE}/mechanic/login', json={
                'email': 'test@example.com',
                'password': 'password123'
            }, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.mechanic_id = data.get('mechanic', {}).get('id')
                log_test("Valid credentials login succeeds", True)
                log_test("Token is returned", bool(self.token))
                log_test("Mechanic data is returned", bool(self.mechanic_id))
            else:
                log_test("Valid credentials login succeeds", False, 
                        f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            log_test("Valid credentials login succeeds", False, str(e))
        
        # Test 1.3: Protected route without token
        try:
            response = requests.get(f'{API_BASE}/mechanic/me', timeout=5)
            log_test(
                "Protected route without token returns 401",
                response.status_code == 401,
                f"Expected 401, got {response.status_code}"
            )
        except Exception as e:
            log_test("Protected route without token returns 401", False, str(e))
        
        # Test 1.4: Protected route with valid token
        if self.token:
            try:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(f'{API_BASE}/mechanic/me', 
                                       headers=headers, timeout=5)
                log_test(
                    "Protected route with token succeeds",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                log_test("Protected route with token succeeds", False, str(e))
    
    def test_dashboard(self):
        """Test dashboard functionality"""
        print_section("2. DASHBOARD")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test 2.1: Get stats
        try:
            response = requests.get(f'{API_BASE}/mechanic/stats', 
                                   headers=headers, timeout=5)
            if response.status_code == 200:
                stats = response.json()
                log_test("Stats endpoint works", True)
                log_test("Stats contain active_orders", 'active_orders' in stats)
                log_test("Stats contain completed_today", 'completed_today' in stats)
                log_test("Stats contain time_today_minutes", 'time_today_minutes' in stats)
            else:
                log_test("Stats endpoint works", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Stats endpoint works", False, str(e))
        
        # Test 2.2: Get all orders
        try:
            response = requests.get(f'{API_BASE}/mechanic/orders', 
                                   headers=headers, timeout=5)
            if response.status_code == 200:
                orders = response.json()
                log_test("Get all orders works", True)
                log_test("Orders is a list", isinstance(orders, list))
                if orders:
                    self.test_order_id = orders[0]['id']
                    log_test("Order contains required fields", 
                            all(k in orders[0] for k in ['id', 'work_status', 'category']))
            else:
                log_test("Get all orders works", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Get all orders works", False, str(e))
        
        # Test 2.3: Filter orders by status
        for status in ['новый', 'в работе', 'завершен']:
            try:
                response = requests.get(f'{API_BASE}/mechanic/orders', 
                                       params={'status': status},
                                       headers=headers, timeout=5)
                log_test(
                    f"Filter orders by '{status}' works",
                    response.status_code == 200,
                    f"Status: {response.status_code}"
                )
            except Exception as e:
                log_test(f"Filter orders by '{status}' works", False, str(e))
    
    def test_order_details(self):
        """Test order details functionality"""
        print_section("3. ORDER DETAILS")
        
        if not self.test_order_id:
            print(f"{Colors.YELLOW}  ⊘ Skipping - no test order available{Colors.RESET}")
            return
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test 3.1: Get order details
        try:
            response = requests.get(
                f'{API_BASE}/mechanic/orders/{self.test_order_id}',
                headers=headers, timeout=5
            )
            if response.status_code == 200:
                order = response.json()
                log_test("Get order details works", True)
                log_test("Order contains comments", 'comments' in order)
                log_test("Order contains time_logs", 'time_logs' in order)
                log_test("Order contains custom_works", 'custom_works' in order)
                log_test("Order contains custom_parts", 'custom_parts' in order)
            else:
                log_test("Get order details works", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Get order details works", False, str(e))
        
        # Test 3.2: Update order status
        try:
            response = requests.patch(
                f'{API_BASE}/mechanic/orders/{self.test_order_id}/status',
                json={'status': 'в работе'},
                headers=headers, timeout=5
            )
            log_test(
                "Update order status works",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Update order status works", False, str(e))
        
        # Test 3.3: Add comment
        try:
            response = requests.post(
                f'{API_BASE}/mechanic/orders/{self.test_order_id}/comments',
                json={'comment': 'E2E test comment'},
                headers=headers, timeout=5
            )
            log_test(
                "Add comment works",
                response.status_code in [200, 201],
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Add comment works", False, str(e))
        
        # Test 3.4: Get comments
        try:
            response = requests.get(
                f'{API_BASE}/mechanic/orders/{self.test_order_id}/comments',
                headers=headers, timeout=5
            )
            log_test(
                "Get comments works",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Get comments works", False, str(e))
    
    def test_time_tracking(self):
        """Test time tracking functionality"""
        print_section("4. TIME TRACKING")
        
        if not self.test_order_id:
            print(f"{Colors.YELLOW}  ⊘ Skipping - no test order available{Colors.RESET}")
            return
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test 4.1: Get active timer
        try:
            response = requests.get(f'{API_BASE}/mechanic/time/active',
                                   headers=headers, timeout=5)
            log_test(
                "Get active timer works",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Get active timer works", False, str(e))
        
        # Test 4.2: Add manual time
        try:
            now = datetime.utcnow()
            start = (now - timedelta(hours=1)).isoformat() + 'Z'
            end = now.isoformat() + 'Z'
            
            response = requests.post(
                f'{API_BASE}/mechanic/orders/{self.test_order_id}/time/manual',
                json={
                    'started_at': start,
                    'ended_at': end,
                    'duration_minutes': 60,
                    'notes': 'E2E test time entry'
                },
                headers=headers, timeout=5
            )
            log_test(
                "Add manual time works",
                response.status_code in [200, 201],
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Add manual time works", False, str(e))
        
        # Test 4.3: Get time history
        try:
            response = requests.get(f'{API_BASE}/mechanic/time/history',
                                   headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                log_test("Get time history works", True)
                log_test("History contains stats", 'stats' in data)
                log_test("History contains sessions", 'sessions' in data)
            else:
                log_test("Get time history works", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Get time history works", False, str(e))
        
        # Test 4.4: Get time history with date filter
        try:
            today = datetime.utcnow().date().isoformat()
            response = requests.get(
                f'{API_BASE}/mechanic/time/history',
                params={'start_date': today, 'end_date': today},
                headers=headers, timeout=5
            )
            log_test(
                "Time history with date filter works",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Time history with date filter works", False, str(e))
    
    def test_profile(self):
        """Test profile functionality"""
        print_section("5. PROFILE")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test 5.1: Get profile
        try:
            response = requests.get(f'{API_BASE}/mechanic/me',
                                   headers=headers, timeout=5)
            if response.status_code == 200:
                profile = response.json()
                log_test("Get profile works", True)
                log_test("Profile contains name", 'name' in profile)
                log_test("Profile contains email", 'email' in profile)
            else:
                log_test("Get profile works", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Get profile works", False, str(e))
        
        # Test 5.2: Update profile
        try:
            response = requests.patch(
                f'{API_BASE}/mechanic/profile',
                json={'phone': '+972501234567'},
                headers=headers, timeout=5
            )
            log_test(
                "Update profile works",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            log_test("Update profile works", False, str(e))
        
        # Test 5.3: Get all-time stats
        try:
            response = requests.get(
                f'{API_BASE}/mechanic/stats',
                params={'all_time': 'true'},
                headers=headers, timeout=5
            )
            if response.status_code == 200:
                stats = response.json()
                log_test("Get all-time stats works", True)
                log_test("All-time stats contain total_completed", 'total_completed' in stats)
                log_test("All-time stats contain total_minutes", 'total_minutes' in stats)
            else:
                log_test("Get all-time stats works", False, f"Status: {response.status_code}")
        except Exception as e:
            log_test("Get all-time stats works", False, str(e))
    
    def test_error_handling(self):
        """Test error handling"""
        print_section("6. ERROR HANDLING")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        # Test 6.1: Invalid order ID
        try:
            response = requests.get(
                f'{API_BASE}/mechanic/orders/99999',
                headers=headers, timeout=5
            )
            log_test(
                "Invalid order ID returns 404",
                response.status_code == 404,
                f"Expected 404, got {response.status_code}"
            )
        except Exception as e:
            log_test("Invalid order ID returns 404", False, str(e))
        
        # Test 6.2: Invalid status update
        if self.test_order_id:
            try:
                response = requests.patch(
                    f'{API_BASE}/mechanic/orders/{self.test_order_id}/status',
                    json={'status': 'invalid_status'},
                    headers=headers, timeout=5
                )
                log_test(
                    "Invalid status returns 400",
                    response.status_code == 400,
                    f"Expected 400, got {response.status_code}"
                )
            except Exception as e:
                log_test("Invalid status returns 400", False, str(e))
        
        # Test 6.3: Empty comment
        if self.test_order_id:
            try:
                response = requests.post(
                    f'{API_BASE}/mechanic/orders/{self.test_order_id}/comments',
                    json={'comment': ''},
                    headers=headers, timeout=5
                )
                log_test(
                    "Empty comment returns 400",
                    response.status_code == 400,
                    f"Expected 400, got {response.status_code}"
                )
            except Exception as e:
                log_test("Empty comment returns 400", False, str(e))
        
        # Test 6.4: Invalid token
        try:
            invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
            response = requests.get(
                f'{API_BASE}/mechanic/me',
                headers=invalid_headers, timeout=5
            )
            log_test(
                "Invalid token returns 401",
                response.status_code == 401,
                f"Expected 401, got {response.status_code}"
            )
        except Exception as e:
            log_test("Invalid token returns 401", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        print_section("TEST SUMMARY")
        
        total = tests_passed + tests_failed
        pass_rate = (tests_passed / total * 100) if total > 0 else 0
        
        print(f"\n  Total Tests: {Colors.BOLD}{total}{Colors.RESET}")
        print(f"  {Colors.GREEN}Passed: {tests_passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {tests_failed}{Colors.RESET}")
        print(f"  Pass Rate: {Colors.BOLD}{pass_rate:.1f}%{Colors.RESET}")
        
        if tests_failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for result in test_results:
                if not result['passed']:
                    print(f"  • {result['name']}")
                    if result['message']:
                        print(f"    {result['message']}")
        
        print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")
        
        # Exit with error if tests failed
        if tests_failed > 0:
            sys.exit(1)

def main():
    tester = MechanicE2ETest()
    tester.run_all_tests()

if __name__ == '__main__':
    main()
