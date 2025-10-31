#!/usr/bin/env python3
"""
Test script for mechanic API endpoints
"""
import sys
import os
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_mechanic_login():
    """Test mechanic login"""
    print("\n🔑 Testing mechanic login...")
    
    response = requests.post(f'{BASE_URL}/api/mechanic/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"Token: {data['token'][:50]}...")
        print(f"Mechanic: {data['mechanic']['name']}")
        return data['token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_get_current_mechanic(token):
    """Test getting current mechanic"""
    print("\n👤 Testing get current mechanic...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/mechanic/me', headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got mechanic info!")
        print(f"Name: {data['name']}")
        print(f"Email: {data['email']}")
    else:
        print(f"❌ Failed: {response.text}")

def test_get_orders(token):
    """Test getting mechanic orders"""
    print("\n📋 Testing get mechanic orders...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/mechanic/orders', headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        orders = response.json()
        print(f"✅ Got {len(orders)} orders")
    else:
        print(f"❌ Failed: {response.text}")

def test_get_stats(token):
    """Test getting mechanic stats"""
    print("\n📊 Testing get mechanic stats...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/mechanic/stats', headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ Got stats!")
        print(f"Active orders: {stats['active_orders']}")
        print(f"Completed today: {stats['completed_today']}")
        print(f"Time today (minutes): {stats['time_today_minutes']}")
    else:
        print(f"❌ Failed: {response.text}")

def test_get_active_timer(token):
    """Test getting active timer"""
    print("\n⏱️  Testing get active timer...")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/mechanic/time/active', headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        timer = response.json()
        if timer:
            print(f"✅ Active timer found!")
            print(f"Order ID: {timer['order_id']}")
        else:
            print(f"✅ No active timer")
    else:
        print(f"❌ Failed: {response.text}")

def main():
    print("=" * 60)
    print("Testing Mechanic API Endpoints")
    print("=" * 60)
    
    # Test login
    token = test_mechanic_login()
    if not token:
        print("\n❌ Login failed, cannot proceed with other tests")
        return
    
    # Test other endpoints
    test_get_current_mechanic(token)
    test_get_orders(token)
    test_get_stats(token)
    test_get_active_timer(token)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()
