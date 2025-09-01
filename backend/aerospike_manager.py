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
            
            end_time = time.time()
            self.log_query('BATCH_GET', f'GET ALL {len(all_product_ids)} products via primary key lookups', start_time, end_time, len(all_products))
            return all_products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('BATCH_GET', f'BATCH GET products via primary key lookups (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    # Cart operations - New efficient implementation without scan operations
    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get cart items from Aerospike using direct key lookup (O(1) operation)"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        
        try:
            # Direct key lookup - much more efficient than scan
            key = ('grocery', 'cart', session_id)
            (cart_key, metadata, cart_record) = self.aerospike_client.get(key)
            
            if not cart_record:
                end_time = time.time()
                self.log_query('GET', f'GET grocery.cart.{session_id} (empty cart)', start_time, end_time, 0)
                return []
            
            cart_items = cart_record.get('items', [])
            end_time = time.time()
            
            self.log_query('GET', f'GET grocery.cart.{session_id}', start_time, end_time, len(cart_items))
            
            # Add product information to each cart item
            result = []
            for item in cart_items:
                product = self.get_product_by_id(item['product_id'])
                if product:
                    cart_item = {
                        'id': f"{session_id}_{item['product_id']}",  # Generate consistent ID
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'created_at': item.get('added_at', cart_record.get('created_at')),
                        'updated_at': item.get('updated_at', cart_record.get('updated_at')),
                        'product': product,
                        'total': float(product['price']) * item['quantity']
                    }
                    result.append(cart_item)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            self.log_query('GET', f'GET grocery.cart.{session_id} (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart using efficient single-record model"""
        if not self.aerospike_client:
            return {'success': False, 'message': 'Aerospike not connected'}
        
        # Check if product exists
        product = self.get_product_by_id(product_id)
        if not product:
            return {'success': False, 'message': 'Product not found'}
        
        start_time = time.time()
        
        try:
            key = ('grocery', 'cart', session_id)
            current_time = datetime.utcnow().isoformat()
            
            # Get existing cart or create new one
            try:
                (cart_key, metadata, cart_record) = self.aerospike_client.get(key)
                if not cart_record:
                    # Create new cart
                    cart_record = {
                        'session_id': session_id,
                        'items': [],
                        'created_at': current_time,
                        'updated_at': current_time
                    }
                    operation = 'CREATE'
                else:
                    operation = 'UPDATE'
            except:
                # Create new cart
                cart_record = {
                    'session_id': session_id,
                    'items': [],
                    'created_at': current_time,
                    'updated_at': current_time
                }
                operation = 'CREATE'
            
            # Find existing item or add new one
            items = cart_record.get('items', [])
            existing_item = None
            
            for item in items:
                if item['product_id'] == product_id:
                    existing_item = item
                    break
            
            if existing_item:
                # Update existing item quantity
                existing_item['quantity'] += quantity
                existing_item['updated_at'] = current_time
                item_operation = 'UPDATE'
            else:
                # Add new item to cart
                new_item = {
                    'product_id': product_id,
                    'quantity': quantity,
                    'added_at': current_time,
                    'updated_at': current_time
                }
                items.append(new_item)
                item_operation = 'ADD'
            
            # Update cart record
            cart_record['items'] = items
            cart_record['updated_at'] = current_time
            
            # Save cart back to Aerospike
            self.aerospike_client.put(key, cart_record)
            
            end_time = time.time()
            self.log_query(operation, f"{operation} grocery.cart.{session_id} ({item_operation} product {product_id})", start_time, end_time, 1)
            
            return {'success': True, 'message': 'Item added to cart', 'product': product}
            
        except Exception as e:
            end_time = time.time()
            self.log_query('PUT', f'PUT grocery.cart.{session_id} (ERROR: {str(e)})', start_time, end_time, 0)
            return {'success': False, 'message': f'Error adding to cart: {str(e)}'}
    
    def clear_cart(self, session_id: str) -> Dict:
        """Clear cart using efficient single-record deletion"""
        if not self.aerospike_client:
            return {'success': False, 'message': 'Aerospike not connected'}
        
        start_time = time.time()
        
        try:
            key = ('grocery', 'cart', session_id)
            
            # Check if cart exists before trying to remove
            try:
                (cart_key, metadata, cart_record) = self.aerospike_client.get(key)
                if not cart_record:
                    end_time = time.time()
                    self.log_query('DELETE', f'DELETE grocery.cart.{session_id} (already empty)', start_time, end_time, 0)
                    return {'success': True, 'message': 'Cart was already empty'}
                
                item_count = len(cart_record.get('items', []))
            except:
                item_count = 0
            
            # Remove the entire cart record
            self.aerospike_client.remove(key)
            
            end_time = time.time()
            self.log_query('DELETE', f'DELETE grocery.cart.{session_id} (removed {item_count} items)', start_time, end_time, item_count)
            
            return {'success': True, 'message': 'Cart cleared successfully'}
            
        except Exception as e:
            end_time = time.time()
            self.log_query('DELETE', f'DELETE grocery.cart.{session_id} (ERROR: {str(e)})', start_time, end_time, 0)
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
    
    # Filter operations skr
    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """Get products within a specific price range using Aerospike scan with filters"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'products')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                
                # Get price and handle both string and float formats
                price_raw = record.get('price', 0)
                try:
                    if isinstance(price_raw, str):
                        # Remove currency symbols and whitespace if it's a string
                        import re
                        price_clean = re.sub(r'[^\d.]', '', price_raw.strip())
                        price = float(price_clean)
                    else:
                        price = float(price_raw)
                except (ValueError, TypeError):
                    price = 0.0
                
                if min_price <= price <= max_price:
                    products.append(record)
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('SCAN_FILTER', f'SCAN grocery.products WHERE price BETWEEN {min_price} AND {max_price}', start_time, end_time, len(products))
            return products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN_FILTER', f'SCAN grocery.products price filter (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_products_by_rating(self, min_rating: float) -> List[Dict]:
        """Get products with minimum rating using Aerospike scan with filters"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'products')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                # Extract rating from "Rated X.X out of 5 stars" format
                rating_text = record.get('rating', '')
                if 'Rated' in rating_text:
                    try:
                        rating = float(rating_text.split('Rated ')[1].split(' ')[0])
                        if rating >= min_rating:
                            products.append(record)
                    except:
                        pass
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('SCAN_FILTER', f'SCAN grocery.products WHERE rating >= {min_rating}', start_time, end_time, len(products))
            return products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN_FILTER', f'SCAN grocery.products rating filter (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_products_by_discount_status(self, has_discount: bool = True) -> List[Dict]:
        """Get products by discount status using Aerospike scan with filters"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'products')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                discount = record.get('discount', 'No Discount')
                
                if has_discount and discount != 'No Discount':
                    products.append(record)
                elif not has_discount and discount == 'No Discount':
                    products.append(record)
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            discount_status = "has discount" if has_discount else "no discount"
            self.log_query('SCAN_FILTER', f'SCAN grocery.products WHERE {discount_status}', start_time, end_time, len(products))
            return products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN_FILTER', f'SCAN grocery.products discount filter (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_products_by_feature(self, feature_keyword: str) -> List[Dict]:
        """Get products containing specific features using Aerospike scan with filters"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'products')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                feature = record.get('feature', '').lower()
                description = record.get('product_description', '').lower()
                
                if feature_keyword.lower() in feature or feature_keyword.lower() in description:
                    products.append(record)
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('SCAN_FILTER', f'SCAN grocery.products WHERE feature CONTAINS "{feature_keyword}"', start_time, end_time, len(products))
            return products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN_FILTER', f'SCAN grocery.products feature filter (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_products_advanced_filter(self, 
                                    min_price: Optional[float] = None,
                                    max_price: Optional[float] = None,
                                    min_rating: Optional[float] = None,
                                    category_id: Optional[int] = None,
                                    has_discount: Optional[bool] = None,
                                    feature_keyword: Optional[str] = None,
                                    min_stock: Optional[int] = None,
                                    is_available: Optional[bool] = None,
                                    search_term: Optional[str] = None) -> List[Dict]:
        """Advanced product filtering with multiple criteria using Aerospike scan. Ignores min_stock, is_available, search_term."""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'products')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                
                # Get price once and handle both string and float formats
                price_raw = record.get('price', 0)
                try:
                    if isinstance(price_raw, str):
                        # Remove currency symbols and whitespace if it's a string
                        import re
                        price_clean = re.sub(r'[^\d.]', '', price_raw.strip())
                        price = float(price_clean)
                    else:
                        price = float(price_raw)
                except (ValueError, TypeError):
                    price = 0.0
                
                # Apply all filters
                if min_price is not None and price < min_price:
                    return
                
                if max_price is not None and price > max_price:
                    return
                
                if min_rating is not None:
                    rating_text = record.get('rating', '')
                    if 'Rated' in rating_text:
                        try:
                            rating = float(rating_text.split('Rated ')[1].split(' ')[0])
                            if rating < min_rating:
                                return
                        except:
                            return
                    else:
                        return
                
                if category_id is not None:
                    if record.get('category_id') != category_id:
                        return
                
                if has_discount is not None:
                    discount = record.get('discount', 'No Discount')
                    if has_discount and discount == 'No Discount':
                        return
                    elif not has_discount and discount != 'No Discount':
                        return
                
                if feature_keyword is not None:
                    feature = record.get('feature', '').lower()
                    description = record.get('product_description', '').lower()
                    if feature_keyword.lower() not in feature and feature_keyword.lower() not in description:
                        return
                
                products.append(record)
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            # Build query description
            filters = []
            if min_price is not None:
                filters.append(f"price >= {min_price}")
            if max_price is not None:
                filters.append(f"price <= {max_price}")
            if min_rating is not None:
                filters.append(f"rating >= {min_rating}")
            if category_id is not None:
                filters.append(f"category_id = {category_id}")
            if has_discount is not None:
                filters.append(f"discount {'!=' if has_discount else '=='} 'No Discount'")
            if feature_keyword is not None:
                filters.append(f"feature CONTAINS '{feature_keyword}'")
            
            query_desc = f"SCAN grocery.products WHERE {' AND '.join(filters)}" if filters else "SCAN grocery.products"
            self.log_query('SCAN_FILTER', query_desc, start_time, end_time, len(products))
            return products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN_FILTER', f'SCAN grocery.products advanced filter (ERROR: {str(e)})', start_time, end_time, 0)
            return [] 