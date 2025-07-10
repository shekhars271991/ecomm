#!/usr/bin/env python3
"""
Test script to verify CSV data loader functionality
"""
import os
import sys

# Add the project root to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.csv_data_loader import CSVDataLoader

def test_csv_parsing():
    """Test CSV parsing functionality"""
    print("Testing CSV parsing...")
    
    # Create a dummy loader (we don't need actual managers for parsing tests)
    loader = CSVDataLoader(None, None)
    
    # Test CSV file path (go up to project root, then to backend/datasets)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file_path = os.path.join(project_root, 'backend', 'datasets', 'GroceryDataset.csv')
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found at: {csv_file_path}")
        return False
    
    try:
        # Load CSV data
        products = loader.load_csv_data(csv_file_path)
        
        print(f"✅ Successfully loaded {len(products)} products")
        
        # Show first few products
        print("\nFirst 5 products:")
        for i, product in enumerate(products[:5]):
            print(f"  {i+1}. {product['title'][:50]}... - ${product['price']:.2f} - {product['category']}")
        
        # Get category mapping
        category_mapping = loader.get_category_mapping(products)
        print(f"\n✅ Found {len(category_mapping)} unique categories:")
        for category, category_id in sorted(category_mapping.items()):
            print(f"  {category_id}: {category}")
        
        # Test price parsing
        test_prices = ["$56.99", "$159.99", "$27.99", ""]
        print(f"\n✅ Price parsing test:")
        for price_str in test_prices:
            parsed = loader.parse_price(price_str)
            print(f"  '{price_str}' -> {parsed}")
        
        # Test rating parsing
        test_ratings = [
            "Rated 4.3 out of 5 stars based on 265 reviews.",
            "Rated 5 out of 5 stars based on 1 reviews.",
            "No Reviews",
            ""
        ]
        print(f"\n✅ Rating parsing test:")
        for rating_str in test_ratings:
            rating, count = loader.parse_rating(rating_str)
            print(f"  '{rating_str[:40]}...' -> Rating: {rating}, Reviews: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during CSV parsing: {e}")
        return False

def main():
    """Main test function"""
    print("=== CSV Data Loader Test ===")
    
    if test_csv_parsing():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 