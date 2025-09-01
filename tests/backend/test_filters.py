#!/usr/bin/env python3
"""
Test script for database filter operations
Tests filter functionality across MySQL, Aerospike, and MongoDB
"""

import sys
import os
import time
import requests
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from unified_database_manager import UnifiedDatabaseManager

# API base URL
API_BASE_URL = "http://localhost:5001"

def test_filter_operations():
    """Test filter operations across all databases"""
    
    print("🧪 Testing Filter Operations Across All Databases")
    print("=" * 60)
    
    # Test databases
    databases = ['mysql', 'aerospike', 'mongodb']
    
    for db_type in databases:
        print(f"\n📊 Testing {db_type.upper()} Database")
        print("-" * 40)
        
        # Set database via header
        headers = {'X-Database': db_type}
        
        # Test 1: Price Range Filter
        print("1. Testing Price Range Filter...")
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/products/filter/price",
                params={'min_price': 10, 'max_price': 50},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {len(data.get('data', []))} products between $10-$50")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test 2: Rating Filter (only for Aerospike and MongoDB)
        if db_type in ['aerospike', 'mongodb']:
            print("2. Testing Rating Filter...")
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/products/filter/rating",
                    params={'min_rating': 4.0},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Found {len(data.get('data', []))} products with rating >= 4.0")
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("2. Skipping Rating Filter (not supported in MySQL)")
        
        # Test 3: Discount Status Filter (only for Aerospike and MongoDB)
        if db_type in ['aerospike', 'mongodb']:
            print("3. Testing Discount Status Filter...")
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/products/filter/discount",
                    params={'has_discount': 'true'},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Found {len(data.get('data', []))} products with discounts")
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("3. Skipping Discount Filter (not supported in MySQL)")
        
        # Test 4: Feature Filter (only for Aerospike and MongoDB)
        if db_type in ['aerospike', 'mongodb']:
            print("4. Testing Feature Filter...")
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/products/filter/feature",
                    params={'feature': 'Kosher'},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Found {len(data.get('data', []))} products with 'Kosher' feature")
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("4. Skipping Feature Filter (not supported in MySQL)")
        
        # Test 5: Stock Level Filter (MySQL specific)
        if db_type == 'mysql':
            print("5. Testing Stock Level Filter...")
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/products/filter/stock",
                    params={'min_stock': 50},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Found {len(data.get('data', []))} products with stock >= 50")
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("5. Skipping Stock Filter (MySQL specific)")
        
        # Test 6: Availability Filter (MySQL specific)
        if db_type == 'mysql':
            print("6. Testing Availability Filter...")
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/products/filter/availability",
                    params={'is_available': 'true'},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Found {len(data.get('data', []))} available products")
                else:
                    print(f"   ❌ Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("6. Skipping Availability Filter (MySQL specific)")
        
        # Test 7: Advanced Filter
        print("7. Testing Advanced Filter...")
        try:
            params = {'min_price': 20, 'max_price': 100}
            if db_type in ['aerospike', 'mongodb']:
                params.update({'min_rating': 4.0, 'has_discount': 'true'})
            else:
                params.update({'min_stock': 10})
            
            response = requests.get(
                f"{API_BASE_URL}/api/products/filter/advanced",
                params=params,
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {len(data.get('data', []))} products with advanced filters")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(1)  # Brief pause between databases
    
    print("\n🎉 Filter operation tests completed!")

def test_api_endpoints():
    """Test that all filter API endpoints are accessible"""
    
    print("\n🔗 Testing API Endpoint Accessibility")
    print("=" * 40)
    
    endpoints = [
        '/api/products/filter/price',
        '/api/products/filter/rating', 
        '/api/products/filter/discount',
        '/api/products/filter/feature',
        '/api/products/filter/stock',
        '/api/products/filter/availability',
        '/api/products/filter/advanced'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            if response.status_code in [200, 400]:  # 400 is OK for missing parameters
                print(f"   ✅ {endpoint} - Accessible")
            else:
                print(f"   ❌ {endpoint} - Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Filter Operations Test Suite")
    print("Make sure the Flask app is running on http://localhost:5001")
    print("Make sure all databases are loaded with data")
    
    # Test API endpoints first
    test_api_endpoints()
    
    # Test filter operations
    test_filter_operations()
    
    print("\n✨ Test suite completed!") 