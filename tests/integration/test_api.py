#!/usr/bin/env python3
"""
Test script to verify the backend API endpoints are working correctly
"""

import requests
import json
import time

API_BASE_URL = 'http://localhost:5001/api'

def test_api_endpoint(endpoint, method='GET', data=None, params=None):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}/{endpoint}"
    
    print(f"\n🔍 Testing {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ Success: {json.dumps(result, indent=2)}")
            return result, True
        else:
            print(f"❌ Error: {response.text}")
            return None, False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None, False

def main():
    print("🚀 Starting API Tests...")
    
    # Test 1: Get Categories
    print("\n" + "="*50)
    print("TEST 1: Get Categories")
    categories, success = test_api_endpoint('categories')
    
    if not success:
        print("❌ Categories test failed - backend might not be running")
        return
    
    # Test 2: Get Products
    print("\n" + "="*50)
    print("TEST 2: Get Products")
    products, success = test_api_endpoint('products')
    
    if not success:
        print("❌ Products test failed")
        return
    
    # Test 3: Get Product by ID
    if products and products.get('products'):
        product_id = products['products'][0]['id']
        print("\n" + "="*50)
        print(f"TEST 3: Get Product by ID ({product_id})")
        product, success = test_api_endpoint(f'products/{product_id}')
    
    # Test 4: Register User
    print("\n" + "="*50)
    print("TEST 4: Register User")
    user_data = {
        'action': 'register',
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test User',
        'address': '123 Test Street',
        'phone': '555-1234'
    }
    user_result, success = test_api_endpoint('user', method='POST', data=user_data)
    
    # Test 5: Login User
    print("\n" + "="*50)
    print("TEST 5: Login User")
    login_data = {
        'action': 'login',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    login_result, success = test_api_endpoint('user', method='POST', data=login_data)
    
    # Test 6: Test Cart
    print("\n" + "="*50)
    print("TEST 6: Test Cart")
    cart_data = {
        'cart_items': [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ]
    }
    cart_result, success = test_api_endpoint('cart', method='POST', data=cart_data)
    
    # Test 7: Create Order (if user was created successfully)
    if user_result and user_result.get('user'):
        print("\n" + "="*50)
        print("TEST 7: Create Order")
        order_data = {
            'user_id': user_result['user']['id'],
            'total_amount': 25.97,
            'delivery_address': '123 Test Street',
            'items': [
                {'product_id': 1, 'quantity': 2, 'price': 2.99},
                {'product_id': 2, 'quantity': 1, 'price': 3.49}
            ]
        }
        order_result, success = test_api_endpoint('orders', method='POST', data=order_data)
        
        # Test 8: Get Orders for User
        if order_result:
            print("\n" + "="*50)
            print("TEST 8: Get Orders for User")
            orders_result, success = test_api_endpoint('orders', params={'user_id': user_result['user']['id']})
    
    print("\n" + "="*50)
    print("✅ API Tests Completed!")
    print("🌐 Frontend should be running at: http://localhost:5000")
    print("🔧 Backend API is running at: http://localhost:5001")

if __name__ == '__main__':
    main() 