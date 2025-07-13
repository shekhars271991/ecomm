import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


class MongoManager:
    def __init__(self, app=None):
        self.app = app
        self.mongo_client = None
        self.db_tracker = None
        self.database = None
        
    def initialize(self, app, db_tracker):
        """Initialize the MongoDB manager with app context"""
        self.app = app
        self.db_tracker = db_tracker
        self.connect_mongo()
        
    def connect_mongo(self):
        """Connect to MongoDB"""
        try:
            # MongoDB connection with authentication
            connection_string = 'mongodb://root:rootpassword@localhost:27017/'
            self.mongo_client = MongoClient(connection_string)
            
            # Test the connection
            self.mongo_client.admin.command('ping')
            
            # Use 'grocery' database
            self.database = self.mongo_client['grocery']
            
            print("MongoDB Manager connected successfully!")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.mongo_client = None
            self.database = None
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            self.mongo_client = None
            self.database = None
    
    def log_query(self, operation_type: str, query_description: str, start_time: float, end_time: float, result_count: int = 0):
        """Log database operations"""
        print(f"🔍 MongoManager.log_query called: MONGODB {operation_type}")
        if self.db_tracker and self.db_tracker.enabled:
            self.db_tracker.log_query(
                f"MONGODB {operation_type}",
                query_description,
                start_time,
                end_time,
                result_count,
                database_type='mongodb'
            )
        else:
            print(f"❌ DB tracker not available or disabled: tracker={self.db_tracker}, enabled={self.db_tracker.enabled if self.db_tracker else 'N/A'}")
    
    # Category operations
    def get_all_categories(self) -> List[Dict]:
        """Get all categories from MongoDB"""
        if self.database is None:
            return []
        
        start_time = time.time()
        
        try:
            # Get all categories from meta collection (like Aerospike)
            meta_doc = self.database.meta.find_one({'_id': 'all_categories'})
            
            if meta_doc and 'categories' in meta_doc:
                categories = meta_doc['categories']
                # Ensure categories are properly serialized (no ObjectId values)
                serialized_categories = []
                for cat in categories:
                    serialized_categories.append({
                        'id': cat.get('id'),
                        'name': cat.get('name'),
                        'icon': cat.get('icon')
                    })
                end_time = time.time()
                self.log_query('FIND', 'db.meta.findOne({_id: "all_categories"})', start_time, end_time, len(serialized_categories))
                return serialized_categories
            else:
                # Fallback: get from categories collection
                categories_cursor = self.database.categories.find({})
                categories = []
                for cat in categories_cursor:
                    categories.append({
                        'id': cat.get('id'),
                        'name': cat.get('name'),
                        'icon': cat.get('icon')
                    })
                
                end_time = time.time()
                self.log_query('FIND', 'db.categories.find({})', start_time, end_time, len(categories))
                return categories
        except Exception as e:
            end_time = time.time()
            self.log_query('FIND', f'db.meta.findOne ERROR: {str(e)}', start_time, end_time, 0)
            return []
    
    # Product operations
    def get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """Get products from MongoDB"""
        if self.database is None:
            return []
        
        start_time = time.time()
        products = []
        
        try:
            # Build query filter
            query_filter = {}
            query_description = "db.products.find("
            
            if category_id:
                query_filter['category_id'] = category_id
                
            if search_term:
                query_filter['name'] = {'$regex': search_term, '$options': 'i'}
            
            query_description += str(query_filter) + ")"
            
            # Execute query
            products_cursor = self.database.products.find(query_filter)
            
            for product in products_cursor:
                products.append({
                    'id': product.get('id'),
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'price': product.get('price'),
                    'image_url': product.get('image_url'),
                    'stock': product.get('stock'),
                    'category_id': product.get('category_id'),
                    'is_available': product.get('is_available')
                })
            
            end_time = time.time()
            self.log_query('FIND', query_description, start_time, end_time, len(products))
            return products
            
        except Exception as e:
            end_time = time.time()
            self.log_query('FIND', f'db.products.find ERROR: {str(e)}', start_time, end_time, 0)
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID from MongoDB"""
        if self.database is None:
            return None
        
        start_time = time.time()
        
        try:
            product = self.database.products.find_one({'id': product_id})
            
            if product:
                result = {
                    'id': product.get('id'),
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'price': product.get('price'),
                    'image_url': product.get('image_url'),
                    'stock': product.get('stock'),
                    'category_id': product.get('category_id'),
                    'is_available': product.get('is_available')
                }
                end_time = time.time()
                self.log_query('FIND', f'db.products.findOne({{id: {product_id}}})', start_time, end_time, 1)
                return result
            else:
                end_time = time.time()
                self.log_query('FIND', f'db.products.findOne({{id: {product_id}}}) NOT FOUND', start_time, end_time, 0)
                return None
                
        except Exception as e:
            end_time = time.time()
            self.log_query('FIND', f'db.products.findOne ERROR: {str(e)}', start_time, end_time, 0)
            return None
    
    # Cart operations
    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get cart items for a session from MongoDB"""
        if self.database is None:
            return []
        
        start_time = time.time()
        cart_items = []
        
        try:
            cart_cursor = self.database.cart.find({'user_session': session_id})
            
            for cart_item in cart_cursor:
                # Get product details
                product = self.database.products.find_one({'id': cart_item.get('product_id')})
                
                if product:
                    cart_items.append({
                        'id': str(cart_item.get('_id')),  # Convert ObjectId to string
                        'user_session': cart_item.get('user_session'),
                        'product_id': cart_item.get('product_id'),
                        'quantity': cart_item.get('quantity'),
                        'product': {
                            'id': product.get('id'),
                            'name': product.get('name'),
                            'price': product.get('price'),
                            'image_url': product.get('image_url')
                        },
                        'total': float(product.get('price', 0)) * cart_item.get('quantity', 0),
                        'created_at': cart_item.get('created_at', ''),
                        'updated_at': cart_item.get('updated_at', '')
                    })
            
            end_time = time.time()
            self.log_query('FIND', f'db.cart.find({{user_session: "{session_id}"}})', start_time, end_time, len(cart_items))
            return cart_items
            
        except Exception as e:
            end_time = time.time()
            self.log_query('FIND', f'db.cart.find ERROR: {str(e)}', start_time, end_time, 0)
            return []
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart in MongoDB"""
        if self.database is None:
            return {'success': False, 'message': 'MongoDB not available'}
        
        start_time = time.time()
        
        try:
            # Check if product exists
            product = self.database.products.find_one({'id': product_id})
            if not product:
                return {'success': False, 'message': 'Product not found'}
            
            # Check if item already exists in cart
            existing_item = self.database.cart.find_one({
                'user_session': session_id,
                'product_id': product_id
            })
            
            if existing_item:
                # Update quantity
                new_quantity = existing_item.get('quantity', 0) + quantity
                self.database.cart.update_one(
                    {'_id': existing_item['_id']},
                    {
                        '$set': {
                            'quantity': new_quantity,
                            'updated_at': datetime.now().isoformat()
                        }
                    }
                )
                operation = 'UPDATE'
                message = f'Updated {product["name"]} quantity to {new_quantity}'
            else:
                # Insert new item
                cart_item = {
                    'user_session': session_id,
                    'product_id': product_id,
                    'quantity': quantity,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                self.database.cart.insert_one(cart_item)
                operation = 'INSERT'
                message = f'Added {product["name"]} to cart'
            
            end_time = time.time()
            self.log_query(operation, f'db.cart.{operation.lower()} for session {session_id}', start_time, end_time, 1)
            
            return {
                'success': True,
                'message': message,
                'product': {
                    'id': product.get('id'),
                    'name': product.get('name'),
                    'price': product.get('price')
                }
            }
            
        except Exception as e:
            end_time = time.time()
            self.log_query('INSERT/UPDATE', f'db.cart operation ERROR: {str(e)}', start_time, end_time, 0)
            return {'success': False, 'message': f'Error adding to cart: {str(e)}'}
    
    def clear_cart(self, session_id: str) -> Dict:
        """Clear cart for a session in MongoDB"""
        if self.database is None:
            return {'success': False, 'message': 'MongoDB not available'}
        
        start_time = time.time()
        
        try:
            result = self.database.cart.delete_many({'user_session': session_id})
            
            end_time = time.time()
            self.log_query('DELETE', f'db.cart.deleteMany({{user_session: "{session_id}"}})', start_time, end_time, result.deleted_count)
            
            return {
                'success': True,
                'message': f'Cleared {result.deleted_count} items from cart'
            }
            
        except Exception as e:
            end_time = time.time()
            self.log_query('DELETE', f'db.cart.deleteMany ERROR: {str(e)}', start_time, end_time, 0)
            return {'success': False, 'message': f'Error clearing cart: {str(e)}'}
    
    def init_sample_data(self):
        """Initialize sample data in MongoDB"""
        if self.database is None:
            print("❌ MongoDB not available for sample data initialization")
            return
        
        try:
            # Sample categories
            sample_categories = [
                {'id': 1, 'name': 'Fruits & Vegetables', 'icon': '🥕'},
                {'id': 2, 'name': 'Dairy & Eggs', 'icon': '🥛'},
                {'id': 3, 'name': 'Meat & Seafood', 'icon': '🥩'},
                {'id': 4, 'name': 'Bakery', 'icon': '🍞'},
                {'id': 5, 'name': 'Beverages', 'icon': '🥤'},
                {'id': 6, 'name': 'Snacks', 'icon': '🍿'}
            ]
            
            # Clear existing data
            self.database.categories.delete_many({})
            self.database.products.delete_many({})
            self.database.meta.delete_many({})
            
            # Insert categories
            self.database.categories.insert_many(sample_categories)
            
            # Store categories in meta collection (like Aerospike)
            self.database.meta.insert_one({
                '_id': 'all_categories',
                'categories': sample_categories
            })
            
            # Sample products
            sample_products = [
                {'id': 1, 'name': 'Fresh Apples', 'description': 'Crisp red apples', 'price': 2.99, 'category_id': 1, 'stock': 100, 'is_available': True, 'image_url': ''},
                {'id': 2, 'name': 'Organic Milk', 'description': 'Fresh organic milk 1L', 'price': 4.49, 'category_id': 2, 'stock': 50, 'is_available': True, 'image_url': ''},
                {'id': 3, 'name': 'Chicken Breast', 'description': 'Fresh chicken breast 1kg', 'price': 8.99, 'category_id': 3, 'stock': 25, 'is_available': True, 'image_url': ''},
                {'id': 4, 'name': 'Whole Wheat Bread', 'description': 'Fresh baked bread', 'price': 3.49, 'category_id': 4, 'stock': 30, 'is_available': True, 'image_url': ''},
                {'id': 5, 'name': 'Orange Juice', 'description': 'Freshly squeezed orange juice 1L', 'price': 5.99, 'category_id': 5, 'stock': 40, 'is_available': True, 'image_url': ''},
                {'id': 6, 'name': 'Potato Chips', 'description': 'Crispy potato chips 200g', 'price': 2.49, 'category_id': 6, 'stock': 75, 'is_available': True, 'image_url': ''}
            ]
            
            self.database.products.insert_many(sample_products)
            
            print(f"✅ MongoDB sample data initialized: {len(sample_categories)} categories, {len(sample_products)} products")
            
        except Exception as e:
            print(f"❌ Failed to initialize MongoDB sample data: {e}")
    
    def is_available(self) -> bool:
        """Check if MongoDB is available"""
        return self.mongo_client is not None and self.database is not None
    
    def close(self):
        """Close MongoDB connection"""
        if self.mongo_client:
            self.mongo_client.close()
            print("MongoDB connection closed") 