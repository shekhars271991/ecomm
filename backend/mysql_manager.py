import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask_sqlalchemy import SQLAlchemy


class MySQLManager:
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.db_tracker = None
        # Model classes will be set during initialization
        self.Category = None
        self.Product = None
        self.Cart = None
        
    def initialize(self, app, db, db_tracker, models=None):
        """Initialize the MySQL manager with app context and models"""
        self.app = app
        self.db = db
        self.db_tracker = db_tracker
        
        # Set model classes if provided
        if models:
            self.Category = models.get('Category')
            self.Product = models.get('Product')
            self.Cart = models.get('Cart')
        
        print("MySQL Manager initialized successfully")
    
    def log_query(self, operation_type: str, query_description: str, start_time: float, end_time: float, result_count: int = 0):
        """Log database operations"""
        print(f"🔍 MySQLManager.log_query called: MYSQL {operation_type}")
        if self.db_tracker and self.db_tracker.enabled:
            self.db_tracker.log_query(
                f"MYSQL {operation_type}",
                query_description,
                start_time,
                end_time,
                result_count,
                database_type='mysql'
            )
        else:
            print(f"❌ DB tracker not available or disabled: tracker={self.db_tracker}, enabled={self.db_tracker.enabled if self.db_tracker else 'N/A'}")
    
    # Category operations
    def get_all_categories(self) -> List[Dict]:
        """Get all categories from MySQL"""
        if not self.Category:
            return []
            
        start_time = time.time()
        categories = self.Category.query.all()
        end_time = time.time()
        
        self.log_query('SELECT', 'SELECT * FROM categories', start_time, end_time, len(categories))
        return [{'id': cat.id, 'name': cat.name, 'icon': cat.icon} for cat in categories]
    
    # Product operations
    def get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """Get products from MySQL"""
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
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID from MySQL"""
        if not self.Product:
            return None
            
        start_time = time.time()
        product = self.Product.query.get(product_id)
        end_time = time.time()
        
        self.log_query('SELECT', f"SELECT * FROM products WHERE id = {product_id}", start_time, end_time, 1 if product else 0)
        
        if product:
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
        return None
    
    # Cart operations
    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get cart items from MySQL"""
        if not self.Cart or not self.Product:
            return []
            
        start_time = time.time()
        cart_items = self.Cart.query.filter_by(user_session=session_id).all()
        end_time = time.time()
        
        self.log_query('SELECT', f"SELECT * FROM cart WHERE user_session = '{session_id}'", start_time, end_time, len(cart_items))
        
        result = []
        for item in cart_items:
            # Get product information
            product = self.get_product_by_id(item.product_id)
            if product:
                cart_item = {
                    'id': item.id,
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'created_at': item.created_at.isoformat(),
                    'updated_at': item.updated_at.isoformat(),
                    'product': product,
                    'total': float(product['price']) * item.quantity
                }
                result.append(cart_item)
        
        return result
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart in MySQL"""
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
    
    def clear_cart(self, session_id: str) -> Dict:
        """Clear cart in MySQL"""
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
    
    def is_available(self) -> bool:
        """Check if MySQL is available"""
        return self.db is not None and self.Category is not None 