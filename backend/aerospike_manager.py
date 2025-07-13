import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import aerospike


class AerospikeManager:
    def __init__(self, app=None):
        self.app = app
        self.aerospike_client = None
        self.db_tracker = None
        
    def initialize(self, app, db_tracker):
        """Initialize the Aerospike manager with app context"""
        self.app = app
        self.db_tracker = db_tracker
        self.connect_aerospike()
        
    def connect_aerospike(self):
        """Connect to Aerospike"""
        try:
            config = {
                'hosts': [('127.0.0.1', 3000)]
            }
            self.aerospike_client = aerospike.client(config).connect()
            print("Aerospike Manager connected successfully!")
        except Exception as e:
            print(f"Failed to connect to Aerospike: {e}")
            self.aerospike_client = None
    
    def log_query(self, operation_type: str, query_description: str, start_time: float, end_time: float, result_count: int = 0):
        """Log database operations"""
        print(f"🔍 AerospikeManager.log_query called: AEROSPIKE {operation_type}")
        if self.db_tracker and self.db_tracker.enabled:
            self.db_tracker.log_query(
                f"AEROSPIKE {operation_type}",
                query_description,
                start_time,
                end_time,
                result_count,
                database_type='aerospike'
            )
        else:
            print(f"❌ DB tracker not available or disabled: tracker={self.db_tracker}, enabled={self.db_tracker.enabled if self.db_tracker else 'N/A'}")
    
    # Category operations
    def get_all_categories(self) -> List[Dict]:
        """Get all categories from Aerospike"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        
        try:
            # Get all categories from single meta record
            key = ('grocery', 'meta', 'all_categories')
            key, metadata, record = self.aerospike_client.get(key)
            
            if record and 'categories' in record:
                categories = record['categories']
                end_time = time.time()
                self.log_query('GET', 'GET grocery.meta.all_categories', start_time, end_time, len(categories))
                return categories
            else:
                end_time = time.time()
                self.log_query('GET', 'GET grocery.meta.all_categories (NOT FOUND)', start_time, end_time, 0)
                return []
        except Exception as e:
            end_time = time.time()
            self.log_query('GET', f'GET grocery.meta.all_categories (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    # Product operations
    def get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """Get products from Aerospike"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'products')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                product = {
                    'id': record.get('id'),
                    'name': record.get('name'),
                    'description': record.get('description'),
                    'price': record.get('price'),
                    'image_url': record.get('image_url'),
                    'stock': record.get('stock'),
                    'category_id': record.get('category_id'),
                    'is_available': record.get('is_available')
                }
                
                # Apply filters
                if category_id and product.get('category_id') != category_id:
                    return
                
                if search_term and search_term.lower() not in product.get('name', '').lower():
                    return
                
                products.append(product)
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            query_description = 'SCAN grocery.products'
            if category_id:
                query_description += f' WHERE category_id = {category_id}'
            if search_term:
                query_description += f' WHERE name CONTAINS "{search_term}"'
            
            self.log_query('SCAN', query_description, start_time, end_time, len(products))
            return products
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN', f'SCAN grocery.products (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID from Aerospike"""
        if not self.aerospike_client:
            return None
        
        start_time = time.time()
        
        try:
            key = ('grocery', 'products', str(product_id))
            (key, metadata, record) = self.aerospike_client.get(key)
            end_time = time.time()
            
            self.log_query('GET', f'GET grocery.products.{product_id}', start_time, end_time, 1 if record else 0)
            
            if record:
                return {
                    'id': record.get('id'),
                    'name': record.get('name'),
                    'description': record.get('description'),
                    'price': record.get('price'),
                    'image_url': record.get('image_url'),
                    'stock': record.get('stock'),
                    'category_id': record.get('category_id'),
                    'is_available': record.get('is_available')
                }
            return None
        except Exception as e:
            end_time = time.time()
            self.log_query('GET', f'GET grocery.products.{product_id} (ERROR: {str(e)})', start_time, end_time, 0)
            return None
    
    # Cart operations
    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get cart items from Aerospike"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        cart_items = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'cart')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                if record.get('user_session') == session_id:
                    cart_items.append({
                        'id': record.get('id'),
                        'product_id': record.get('product_id'),
                        'quantity': record.get('quantity'),
                        'created_at': record.get('created_at'),
                        'updated_at': record.get('updated_at')
                    })
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('SCAN', f'SCAN grocery.cart WHERE user_session = "{session_id}"', start_time, end_time, len(cart_items))
            
            # Add product information to each cart item
            result = []
            for item in cart_items:
                product = self.get_product_by_id(item['product_id'])
                if product:
                    cart_item = {
                        'id': item['id'],
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at'],
                        'product': product,
                        'total': float(product['price']) * item['quantity']
                    }
                    result.append(cart_item)
            
            return result
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN', f'SCAN grocery.cart (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart in Aerospike"""
        if not self.aerospike_client:
            return {'success': False, 'message': 'Aerospike not connected'}
        
        # Check if product exists
        product = self.get_product_by_id(product_id)
        if not product:
            return {'success': False, 'message': 'Product not found'}
        
        start_time = time.time()
        
        try:
            # Create unique cart item key
            cart_key = f"{session_id}_{product_id}"
            key = ('grocery', 'cart', cart_key)
            
            # Check if item already exists
            try:
                (existing_key, metadata, existing_record) = self.aerospike_client.get(key)
                if existing_record:
                    # Update existing item
                    existing_record['quantity'] += quantity
                    existing_record['updated_at'] = datetime.utcnow().isoformat()
                    self.aerospike_client.put(key, existing_record)
                    operation = 'UPDATE'
                else:
                    raise Exception("Not found")
            except:
                # Add new item
                cart_item = {
                    'id': str(uuid.uuid4()),
                    'user_session': session_id,
                    'product_id': product_id,
                    'quantity': quantity,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                self.aerospike_client.put(key, cart_item)
                operation = 'INSERT'
            
            end_time = time.time()
            self.log_query(operation, f"{operation} grocery.cart.{cart_key}", start_time, end_time, 1)
            
            return {'success': True, 'message': 'Item added to cart', 'product': product}
        except Exception as e:
            end_time = time.time()
            self.log_query('PUT', f'PUT grocery.cart (ERROR: {str(e)})', start_time, end_time, 0)
            return {'success': False, 'message': f'Error adding to cart: {str(e)}'}
    
    def clear_cart(self, session_id: str) -> Dict:
        """Clear cart in Aerospike"""
        if not self.aerospike_client:
            return {'success': False, 'message': 'Aerospike not connected'}
        
        start_time = time.time()
        deleted_count = 0
        
        try:
            scan = self.aerospike_client.scan('grocery', 'cart')
            
            def scan_callback(input_tuple):
                nonlocal deleted_count
                key, metadata, record = input_tuple
                if record.get('user_session') == session_id:
                    if self.aerospike_client:
                        self.aerospike_client.remove(key)
                    deleted_count += 1
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('DELETE', f"DELETE FROM grocery.cart WHERE user_session = '{session_id}'", start_time, end_time, deleted_count)
            
            return {'success': True, 'message': 'Cart cleared successfully'}
        except Exception as e:
            end_time = time.time()
            self.log_query('DELETE', f'DELETE grocery.cart (ERROR: {str(e)})', start_time, end_time, 0)
            return {'success': False, 'message': f'Error clearing cart: {str(e)}'}
    
    def init_sample_data(self):
        """Initialize sample data in Aerospike"""
        if not self.aerospike_client:
            return
        
        # Sample categories
        categories = [
            {'id': 1, 'name': 'Fruits & Vegetables', 'icon': 'fas fa-carrot'},
            {'id': 2, 'name': 'Dairy & Eggs', 'icon': 'fas fa-glass-whiskey'},
            {'id': 3, 'name': 'Meat & Seafood', 'icon': 'fas fa-drumstick-bite'},
            {'id': 4, 'name': 'Bakery', 'icon': 'fas fa-bread-slice'},
            {'id': 5, 'name': 'Beverages', 'icon': 'fas fa-coffee'},
            {'id': 6, 'name': 'Snacks', 'icon': 'fas fa-cookie-bite'}
        ]
        
        # Sample products
        products = [
            {'id': 1, 'name': 'Fresh Apples', 'description': 'Crisp and juicy red apples', 'price': 2.99, 'stock': 50, 'category_id': 1, 'is_available': True, 'image_url': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300&h=200&fit=crop&crop=center'},
            {'id': 2, 'name': 'Whole Milk', 'description': 'Fresh whole milk - 1 gallon', 'price': 4.99, 'stock': 30, 'category_id': 2, 'is_available': True, 'image_url': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=200&fit=crop&crop=center'},
            {'id': 3, 'name': 'Salmon Fillet', 'description': 'Fresh Atlantic salmon fillet', 'price': 12.99, 'stock': 20, 'category_id': 3, 'is_available': True, 'image_url': 'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba?w=300&h=200&fit=crop&crop=center'},
            {'id': 4, 'name': 'Sourdough Bread', 'description': 'Fresh baked sourdough bread', 'price': 3.99, 'stock': 15, 'category_id': 4, 'is_available': True, 'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=200&fit=crop&crop=center'},
            {'id': 5, 'name': 'Orange Juice', 'description': 'Fresh squeezed orange juice', 'price': 5.99, 'stock': 25, 'category_id': 5, 'is_available': True, 'image_url': 'https://images.unsplash.com/photo-1597714026720-8f74c62310ba?w=300&h=200&fit=crop&crop=center'},
            {'id': 6, 'name': 'Potato Chips', 'description': 'Crispy potato chips', 'price': 2.49, 'stock': 40, 'category_id': 6, 'is_available': True, 'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=300&h=200&fit=crop&crop=center'}
        ]
        
        try:
            start_time = time.time()
            
            # Insert all categories as a single record
            key = ('grocery', 'meta', 'all_categories')
            bins = {
                'categories': categories
            }
            self.aerospike_client.put(key, bins)
            
            # Insert products
            for product in products:
                key = ('grocery', 'products', str(product['id']))
                self.aerospike_client.put(key, product)
            
            end_time = time.time()
            self.log_query('INSERT', f'Initialized {len(categories)} categories and {len(products)} products in Aerospike', start_time, end_time, len(categories) + len(products))
            
            print(f"✅ Initialized Aerospike with {len(categories)} categories and {len(products)} products")
        except Exception as e:
            end_time = time.time()
            self.log_query('INSERT', f'Failed to initialize Aerospike data: {str(e)}', start_time, end_time, 0)
            print(f"❌ Failed to initialize Aerospike data: {e}")
    
    def is_available(self) -> bool:
        """Check if Aerospike is available"""
        return self.aerospike_client is not None
    
    def close(self):
        """Close Aerospike connection"""
        if self.aerospike_client:
            self.aerospike_client.close()
            self.aerospike_client = None 