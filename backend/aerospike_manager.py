import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import aerospike
from aerospike_helpers.batch import records as br


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
            _, metadata, record = self.aerospike_client.get(key)
            
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
        """Get products from Aerospike using optimized storage"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        
        try:
            if category_id:
                # Get products for specific category using category-based storage
                category_key = ('grocery', 'category_products', f'cat:{category_id}')
                _, metadata, record = self.aerospike_client.get(category_key)
                
                if record and 'products' in record:
                    products = record['products']
                    
                    # Apply search term filter if provided
                    if search_term:
                        products = [p for p in products if search_term.lower() in p.get('name', '').lower()]
                    
                    end_time = time.time()
                    query_description = f'GET grocery.category_products.cat:{category_id}'
                    if search_term:
                        query_description += f' FILTERED BY name CONTAINS "{search_term}"'
                    
                    self.log_query('GET', query_description, start_time, end_time, len(products))
                    return products
                else:
                    end_time = time.time()
                    self.log_query('GET', f'GET grocery.category_products.cat:{category_id} (NOT FOUND)', start_time, end_time, 0)
                    return []
            
            else:
                # Get all products using primary key lookups (faster than scanning)
                all_products = self.get_all_products_direct()
                
                # Apply search term filter if provided
                if search_term:
                    all_products = [p for p in all_products if search_term.lower() in p.get('name', '').lower()]
                    # Only log if we applied search filtering (get_all_products_direct already logged the batch operation)
                    end_time = time.time()
                    query_description = 'FILTER grocery.products'
                    query_description += f' BY name CONTAINS "{search_term}"'
                    self.log_query('FILTER', query_description, start_time, end_time, len(all_products))
                
                return all_products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('GET', f'GET grocery.products (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID from Aerospike using direct lookup"""
        if not self.aerospike_client:
            return None
        
        start_time = time.time()
        
        try:
            # Direct product lookup using individual product key
            product_key = ('grocery', 'products', f'product:{product_id}')
            _, metadata, record = self.aerospike_client.get(product_key)
            
            if record:
                end_time = time.time()
                self.log_query('GET', f'GET grocery.products.product:{product_id}', start_time, end_time, 1)
                return record
            else:
                end_time = time.time()
                self.log_query('GET', f'GET grocery.products.product:{product_id} (NOT FOUND)', start_time, end_time, 0)
                return None
                
        except Exception as e:
            end_time = time.time()
            self.log_query('GET', f'GET grocery.products.product:{product_id} (ERROR: {str(e)})', start_time, end_time, 0)
            return None
    
    def get_all_products_direct(self) -> List[Dict]:
        """Get all products using batch primary key lookups from category-collected IDs"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        all_products = []
        
        try:
            # Get all categories to collect product IDs
            categories = self.get_all_categories()
            all_product_ids = set()
            
            # Collect all product IDs from all categories
            for category in categories:
                cat_id = category['id']
                category_key = ('grocery', 'category_products', f'cat:{cat_id}')
                
                try:
                    _, metadata, record = self.aerospike_client.get(category_key)
                    if record and 'products' in record:
                        for product in record['products']:
                            all_product_ids.add(product.get('id'))
                except Exception as e:
                    print(f"Error getting product IDs from category {cat_id}: {e}")
                    continue
            
                        # Use efficient sequential gets (avoiding threading overhead)
            batch_keys = [('grocery', 'products', f'product:{product_id}') for product_id in all_product_ids]

            brs = self.aerospike_client.batch_read(batch_keys)
            for batch_record in brs.batch_records:
                if batch_record.result == 0 and batch_record.record:
                    _, _, bins = batch_record.record
                    all_products.append(bins)


            
            # # Get all products efficiently in a tight loop
            # for key in batch_keys:
            #     try:
            #         _, metadata, record = self.aerospike_client.get(key)
            #         if record:
            #             all_products.append(record)
            #     except:
            #         continue
            
            end_time = time.time()
            self.log_query('BATCH_GET', f'GET ALL {len(all_product_ids)} products via primary key lookups', start_time, end_time, len(all_products))
            return all_products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('BATCH_GET', f'BATCH GET products via primary key lookups (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
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
        """Initialize sample data in Aerospike - CSV data only, no hardcoded samples"""
        if not self.aerospike_client:
            return
        
        # No sample data - all data should be loaded from CSV files
        print("ℹ️  Aerospike initialized - data will be loaded from CSV files only")
    
    def is_available(self) -> bool:
        """Check if Aerospike is available"""
        return self.aerospike_client is not None
    
    def close(self):
        """Close Aerospike connection"""
        if self.aerospike_client:
            self.aerospike_client.close()
            self.aerospike_client = None 