import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import aerospike
from flask_sqlalchemy import SQLAlchemy
from flask import current_app


class DatabaseManager:
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.current_db = 'mysql'  # Default to MySQL
        self.aerospike_client = None
        self.db_tracker = None
        # Model classes will be set during initialization
        self.Category = None
        self.Product = None
        self.Cart = None
        
    def initialize(self, app, db, db_tracker, models=None):
        self.app = app
        self.db = db
        self.db_tracker = db_tracker
        
        # Set model classes if provided
        if models:
            self.Category = models.get('Category')
            self.Product = models.get('Product')
            self.Cart = models.get('Cart')
        
        self.connect_aerospike()
        
    def connect_aerospike(self):
        """Connect to Aerospike"""
        try:
            config = {
                'hosts': [('127.0.0.1', 3000)]
            }
            self.aerospike_client = aerospike.client(config).connect()
            print("Connected to Aerospike!")
        except Exception as e:
            print(f"Failed to connect to Aerospike: {e}")
            self.aerospike_client = None
    
    def set_database(self, db_type: str):
        """Switch between MySQL and Aerospike"""
        if db_type in ['mysql', 'aerospike']:
            self.current_db = db_type
            print(f"Switched to {db_type} database")
        else:
            raise ValueError("Database type must be 'mysql' or 'aerospike'")
    
    def get_current_database(self):
        """Get current database type"""
        return self.current_db
    
    def log_query(self, operation_type: str, query_description: str, start_time: float, end_time: float, result_count: int = 0):
        """Log database operations"""
        print(f"🔍 DatabaseManager.log_query called: {self.current_db.upper()} {operation_type}")
        if self.db_tracker and self.db_tracker.enabled:
            self.db_tracker.log_query(
                f"{self.current_db.upper()} {operation_type}",
                query_description,
                start_time,
                end_time,
                result_count,
                database_type=self.current_db
            )
        else:
            print(f"❌ DB tracker not available or disabled: tracker={self.db_tracker}, enabled={self.db_tracker.enabled if self.db_tracker else 'N/A'}")
    
    # Category operations
    def get_all_categories(self) -> List[Dict]:
        """Get all categories from current database"""
        if self.current_db == 'mysql':
            return self._mysql_get_all_categories()
        else:
            return self._aerospike_get_all_categories()
    
    def _mysql_get_all_categories(self) -> List[Dict]:
        """MySQL: Get all categories"""
        if not self.Category:
            return []
            
        start_time = time.time()
        categories = self.Category.query.all()
        end_time = time.time()
        
        self.log_query('SELECT', 'SELECT * FROM categories', start_time, end_time, len(categories))
        return [{'id': cat.id, 'name': cat.name, 'icon': cat.icon} for cat in categories]
    
    def _aerospike_get_all_categories(self) -> List[Dict]:
        """Aerospike: Get all categories"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        categories = []
        
        try:
            # Scan all records in categories set
            scan = self.aerospike_client.scan('grocery', 'categories')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                categories.append({
                    'id': record.get('id'),
                    'name': record.get('name'),
                    'icon': record.get('icon')
                })
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('SCAN', 'SCAN grocery.categories', start_time, end_time, len(categories))
            return categories
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN', f'SCAN grocery.categories (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    # Product operations
    def get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """Get products from current database"""
        if self.current_db == 'mysql':
            return self._mysql_get_all_products(category_id, search_term)
        else:
            return self._aerospike_get_all_products(category_id, search_term)
    
    def _mysql_get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """MySQL: Get products"""
        if not self.Product:
            return []
            
        start_time = time.time()
        
        query = self.Product.query
        query_description = "SELECT * FROM products"
        
        if category_id:
            query = query.filter(self.Product.category_id == category_id)
            query_description += f" WHERE category_id = {category_id}"
        
        if search_term:
            search_filter = self.Product.name.contains(search_term)
            query = query.filter(search_filter)
            query_description += f" WHERE name LIKE '%{search_term}%'"
        
        products = query.all()
        end_time = time.time()
        
        self.log_query('SELECT', query_description, start_time, end_time, len(products))
        
        return [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price),
            'image_url': p.image_url,
            'stock': p.stock,
            'category_id': p.category_id,
            'is_available': p.is_available
        } for p in products]
    
    def _aerospike_get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """Aerospike: Get products"""
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
            
            filter_desc = []
            if category_id:
                filter_desc.append(f"category_id = {category_id}")
            if search_term:
                filter_desc.append(f"name LIKE '%{search_term}%'")
            
            query_desc = "SCAN grocery.products"
            if filter_desc:
                query_desc += f" WHERE {' AND '.join(filter_desc)}"
            
            self.log_query('SCAN', query_desc, start_time, end_time, len(products))
            return products
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN', f'SCAN grocery.products (ERROR: {str(e)})', start_time, end_time, 0)
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID from current database"""
        if self.current_db == 'mysql':
            return self._mysql_get_product_by_id(product_id)
        else:
            return self._aerospike_get_product_by_id(product_id)
    
    def _mysql_get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """MySQL: Get product by ID"""
        if not self.Product:
            return None
            
        start_time = time.time()
        product = self.Product.query.get(product_id)
        end_time = time.time()
        
        self.log_query('SELECT', f'SELECT * FROM products WHERE id = {product_id}', start_time, end_time, 1 if product else 0)
        
        if not product:
            return None
        
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'image_url': product.image_url,
            'stock': product.stock,
            'category_id': product.category_id,
            'is_available': product.is_available
        }
    
    def _aerospike_get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Aerospike: Get product by ID"""
        if not self.aerospike_client:
            return None
        
        start_time = time.time()
        
        try:
            key = ('grocery', 'products', str(product_id))
            (key, metadata, record) = self.aerospike_client.get(key)
            end_time = time.time()
            
            self.log_query('GET', f'GET grocery.products.{product_id}', start_time, end_time, 1 if record else 0)
            
            if not record:
                return None
            
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
        except Exception as e:
            end_time = time.time()
            self.log_query('GET', f'GET grocery.products.{product_id} (ERROR: {str(e)})', start_time, end_time, 0)
            return None
    
    # Cart operations
    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get cart items from current database"""
        if self.current_db == 'mysql':
            return self._mysql_get_cart_items(session_id)
        else:
            return self._aerospike_get_cart_items(session_id)
    
    def _mysql_get_cart_items(self, session_id: str) -> List[Dict]:
        """MySQL: Get cart items"""
        if not self.Cart:
            return []
            
        start_time = time.time()
        cart_items = self.Cart.query.filter_by(user_session=session_id).all()
        end_time = time.time()
        
        self.log_query('SELECT', f"SELECT * FROM cart WHERE user_session = '{session_id}'", start_time, end_time, len(cart_items))
        
        return [item.to_dict() for item in cart_items]
    
    def _aerospike_get_cart_items(self, session_id: str) -> List[Dict]:
        """Aerospike: Get cart items"""
        if not self.aerospike_client:
            return []
        
        start_time = time.time()
        cart_items = []
        
        try:
            scan = self.aerospike_client.scan('grocery', 'cart')
            
            def scan_callback(input_tuple):
                key, metadata, record = input_tuple
                if record.get('user_session') == session_id:
                    product = self.get_product_by_id(record.get('product_id'))
                    if product:
                        cart_items.append({
                            'id': record.get('id'),
                            'product_id': record.get('product_id'),
                            'quantity': record.get('quantity'),
                            'user_session': record.get('user_session'),
                            'created_at': record.get('created_at'),
                            'updated_at': record.get('updated_at'),
                            'product': product,
                            'total': product['price'] * record.get('quantity')
                        })
            
            scan.foreach(scan_callback)
            end_time = time.time()
            
            self.log_query('SCAN', f"SCAN grocery.cart WHERE user_session = '{session_id}'", start_time, end_time, len(cart_items))
            return cart_items
        except Exception as e:
            end_time = time.time()
            self.log_query('SCAN', f"SCAN grocery.cart (ERROR: {str(e)})", start_time, end_time, 0)
            return []
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart in current database"""
        if self.current_db == 'mysql':
            return self._mysql_add_to_cart(session_id, product_id, quantity)
        else:
            return self._aerospike_add_to_cart(session_id, product_id, quantity)
    
    def _mysql_add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """MySQL: Add item to cart"""
        if not self.Cart or not self.Product:
            return {'success': False, 'message': 'Models not initialized'}
        
        # Check if product exists
        product = self.get_product_by_id(product_id)
        if not product:
            return {'success': False, 'message': 'Product not found'}
        
        # Check if item already exists in cart
        start_time = time.time()
        existing_cart_item = self.Cart.query.filter_by(user_session=session_id, product_id=product_id).first()
        end_time = time.time()
        
        self.log_query('SELECT', f"SELECT * FROM cart WHERE user_session = '{session_id}' AND product_id = {product_id}", start_time, end_time, 1 if existing_cart_item else 0)
        
        if existing_cart_item:
            # Update existing item
            existing_cart_item.quantity += quantity
            existing_cart_item.updated_at = datetime.utcnow()
            
            start_time = time.time()
            if self.db:
                self.db.session.commit()
            end_time = time.time()
            
            self.log_query('UPDATE', f"UPDATE cart SET quantity = {existing_cart_item.quantity} WHERE id = {existing_cart_item.id}", start_time, end_time, 1)
        else:
            # Add new item
            new_cart_item = self.Cart(
                user_session=session_id,
                product_id=product_id,
                quantity=quantity
            )
            
            start_time = time.time()
            if self.db:
                self.db.session.add(new_cart_item)
                self.db.session.commit()
            end_time = time.time()
            
            self.log_query('INSERT', f"INSERT INTO cart (user_session, product_id, quantity) VALUES ('{session_id}', {product_id}, {quantity})", start_time, end_time, 1)
        
        return {'success': True, 'message': 'Item added to cart', 'product': product}
    
    def _aerospike_add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Aerospike: Add item to cart"""
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
        """Clear cart in current database"""
        if self.current_db == 'mysql':
            return self._mysql_clear_cart(session_id)
        else:
            return self._aerospike_clear_cart(session_id)
    
    def _mysql_clear_cart(self, session_id: str) -> Dict:
        """MySQL: Clear cart"""
        if not self.Cart:
            return {'success': False, 'message': 'Cart model not initialized'}
            
        start_time = time.time()
        cart_items = self.Cart.query.filter_by(user_session=session_id).all()
        item_count = len(cart_items)
        
        for item in cart_items:
            if self.db:
                self.db.session.delete(item)
        
        if self.db:
            self.db.session.commit()
        end_time = time.time()
        
        self.log_query('DELETE', f"DELETE FROM cart WHERE user_session = '{session_id}'", start_time, end_time, item_count)
        
        return {'success': True, 'message': 'Cart cleared successfully'}
    
    def _aerospike_clear_cart(self, session_id: str) -> Dict:
        """Aerospike: Clear cart"""
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
        if not self.aerospike_client or self.current_db != 'aerospike':
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
            
            # Insert categories
            for category in categories:
                key = ('grocery', 'categories', str(category['id']))
                self.aerospike_client.put(key, category)
            
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
    
    def close(self):
        """Close database connections"""
        if self.aerospike_client:
            self.aerospike_client.close() 