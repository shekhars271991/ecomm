from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from datetime import datetime
import os
import time
import logging
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://grocery_user:grocery_password@localhost:3306/grocery_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable demo mode for showing database operations
app.config['DEMO_MODE'] = True

db = SQLAlchemy(app)
api = Api(app)
CORS(app)

# Demo mode: Track database operations
class DatabaseTracker:
    def __init__(self):
        self.enabled = app.config.get('DEMO_MODE', False)
    
    def log_query(self, query_type, query, start_time, end_time, result_count=None):
        if not self.enabled:
            return
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Format the operation string
        operation = f"{query_type}: {str(query)}"
        
        # Create and save the log entry
        log_entry = DbLog(
            operation=operation,
            response_count=result_count or 0,
            time_taken_ms=round(duration, 2)
        )
        
        try:
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            # If we can't log to db, just continue - don't break the app
            db.session.rollback()
            print(f"Failed to log query: {e}")
    
    def get_recent_queries(self):
        # Get last 10 queries from database, most recent first
        try:
            logs = DbLog.query.order_by(DbLog.timestamp.desc()).limit(10).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            print(f"Failed to get recent queries: {e}")
            return []
    
    def clear_queries(self):
        try:
            DbLog.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to clear queries: {e}")

# Global tracker instance
db_tracker = DatabaseTracker()

# Wrapper function to track database operations
def track_db_operation(operation_type, operation_func, *args, **kwargs):
    if not db_tracker.enabled:
        return operation_func(*args, **kwargs)
    
    start_time = time.time()
    result = operation_func(*args, **kwargs)
    end_time = time.time()
    
    # Extract query information
    query_info = "Database operation"
    result_count = None
    
    if hasattr(result, 'count'):
        try:
            result_count = result.count()
        except:
            pass
    elif isinstance(result, list):
        result_count = len(result)
    
    db_tracker.log_query(operation_type, query_info, start_time, end_time, result_count)
    return result

# Helper function to create API response with debug info
def create_api_response(data, success=True, message="Success"):
    response = {
        'success': success,
        'message': message,
        'data': data
    }
    
    if db_tracker.enabled:
        response['debug'] = {
            'recent_queries': db_tracker.get_recent_queries(),
            'demo_mode': True
        }
    
    return response

# -------------------------------
# DATABASE MODELS
# -------------------------------

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(50))
    
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'image_url': self.image_url,
            'stock': self.stock,
            'category_id': self.category_id,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat(),
            'category': self.category.to_dict() if self.category else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    delivery_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # Get items dynamically to avoid iteration issues
        order_items = OrderItem.query.filter_by(order_id=self.id).all()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'delivery_address': self.delivery_address,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in order_items]
        }

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    def to_dict(self):
        # Get product dynamically to avoid relationship issues
        product = Product.query.get(self.product_id)
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': float(self.price),
            'product': product.to_dict() if product else None
        }

class DbLog(db.Model):
    __tablename__ = 'db_logs'
    id = db.Column(db.Integer, primary_key=True)
    operation = db.Column(db.String(500), nullable=False)
    response_count = db.Column(db.Integer, default=0)
    time_taken_ms = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'operation': self.operation,
            'response_count': self.response_count,
            'time_taken_ms': self.time_taken_ms,
            'timestamp': self.timestamp.strftime('%H:%M:%S')
        }

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_session = db.Column(db.String(255), nullable=False)  # Session ID to track cart
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = db.relationship('Product', backref='cart_items', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_session': self.user_session,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'product': self.product.to_dict() if self.product else None,
            'total': float(self.product.price * self.quantity) if self.product else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# -------------------------------
# API RESOURCES
# -------------------------------

# API Resource classes with demo tracking
class UserResource(Resource):
    def post(self):
        data = request.get_json()
        
        if not data or 'email' not in data:
            return create_api_response(None, False, "Email is required"), 400
        
        # Check if this is login or registration
        if 'password' not in data:
            return create_api_response(None, False, "Password is required"), 400
        
        start_time = time.time()
        existing_user = User.query.filter_by(email=data['email']).first()
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM users WHERE email = '{data['email']}'", start_time, end_time, 1 if existing_user else 0)
        
        if existing_user:
            # Login attempt
            if check_password_hash(existing_user.password_hash, data['password']):
                user_data = {
                    'id': existing_user.id,
                    'email': existing_user.email,
                    'name': existing_user.name,
                    'address': existing_user.address,
                    'phone': existing_user.phone
                }
                return create_api_response({'user': user_data}, True, "Login successful")
            else:
                return create_api_response(None, False, "Invalid credentials"), 401
        else:
            # Registration
            if 'name' not in data:
                return create_api_response(None, False, "Name is required for registration"), 400
            
            new_user = User(
                email=data['email'],
                password_hash=generate_password_hash(data['password']),
                name=data['name'],
                address=data.get('address', ''),
                phone=data.get('phone', '')
            )
            
            start_time = time.time()
            db.session.add(new_user)
            db.session.commit()
            end_time = time.time()
            
            db_tracker.log_query('INSERT', f"INSERT INTO users (email, name, ...) VALUES ('{data['email']}', '{data['name']}', ...)", start_time, end_time, 1)
            
            user_data = {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'address': new_user.address,
                'phone': new_user.phone
            }
            
            return create_api_response({'user': user_data}, True, "Registration successful"), 201

class CategoriesResource(Resource):
    def get(self):
        start_time = time.time()
        categories = Category.query.all()
        end_time = time.time()
        
        db_tracker.log_query('SELECT', 'SELECT * FROM categories', start_time, end_time, len(categories))
        
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'icon': category.icon
            })
        
        return create_api_response(categories_data)

class ProductsResource(Resource):
    def get(self):
        start_time = time.time()
        
        # Get query parameters
        category_id = request.args.get('category')
        search_term = request.args.get('search')
        
        # Build query
        query = Product.query
        query_description = "SELECT * FROM products"
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
            query_description += f" WHERE category_id = {category_id}"
        
        if search_term:
            search_filter = Product.name.contains(search_term)
            query = query.filter(search_filter)
            query_description += f" WHERE name LIKE '%{search_term}%'"
        
        products = query.all()
        end_time = time.time()
        
        db_tracker.log_query('SELECT', query_description, start_time, end_time, len(products))
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image_url': product.image_url,
                'stock': product.stock,
                'category_id': product.category_id,
                'is_available': product.is_available
            })
        
        return create_api_response(products_data)

class ProductResource(Resource):
    def get(self, product_id):
        start_time = time.time()
        product = Product.query.get(product_id)
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f'SELECT * FROM products WHERE id = {product_id}', start_time, end_time, 1 if product else 0)
        
        if not product:
            return create_api_response(None, False, "Product not found"), 404
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'image_url': product.image_url,
            'stock': product.stock,
            'category_id': product.category_id,
            'is_available': product.is_available
        }
        
        return create_api_response({'product': product_data})

class CartResource(Resource):
    def get(self):
        # Get cart items for current session
        session_id = request.args.get('session_id')
        
        if not session_id:
            return create_api_response(None, False, "Session ID is required"), 400
        
        start_time = time.time()
        cart_items = Cart.query.filter_by(user_session=session_id).all()
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM cart WHERE user_session = '{session_id}'", start_time, end_time, len(cart_items))
        
        processed_cart_items = []
        total = 0
        
        for cart_item in cart_items:
            item_dict = cart_item.to_dict()
            processed_cart_items.append(item_dict)
            total += item_dict['total']
        
        return create_api_response({
            'cart_items': processed_cart_items,
            'total': total
        }, True, "Cart retrieved successfully")
    
    def post(self):
        # Add item to cart
        data = request.get_json()
        
        if not data or 'session_id' not in data or 'product_id' not in data:
            return create_api_response(None, False, "Session ID and product ID are required"), 400
        
        session_id = data['session_id']
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        # Check if product exists
        start_time = time.time()
        product = Product.query.get(product_id)
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM products WHERE id = {product_id}", start_time, end_time, 1 if product else 0)
        
        if not product:
            return create_api_response(None, False, "Product not found"), 404
        
        # Check if item already exists in cart
        start_time = time.time()
        existing_cart_item = Cart.query.filter_by(user_session=session_id, product_id=product_id).first()
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM cart WHERE user_session = '{session_id}' AND product_id = {product_id}", start_time, end_time, 1 if existing_cart_item else 0)
        
        if existing_cart_item:
            # Update existing item
            existing_cart_item.quantity += quantity
            existing_cart_item.updated_at = datetime.utcnow()
            
            start_time = time.time()
            db.session.commit()
            end_time = time.time()
            
            db_tracker.log_query('UPDATE', f"UPDATE cart SET quantity = {existing_cart_item.quantity} WHERE id = {existing_cart_item.id}", start_time, end_time, 1)
        else:
            # Add new item
            new_cart_item = Cart(
                user_session=session_id,
                product_id=product_id,
                quantity=quantity
            )
            
            start_time = time.time()
            db.session.add(new_cart_item)
            db.session.commit()
            end_time = time.time()
            
            db_tracker.log_query('INSERT', f"INSERT INTO cart (user_session, product_id, quantity) VALUES ('{session_id}', {product_id}, {quantity})", start_time, end_time, 1)
        
        return create_api_response({
            'message': f'{product.name} added to cart',
            'product': product.to_dict()
        }, True, "Item added to cart successfully")
    
    def delete(self):
        # Clear cart for session
        session_id = request.args.get('session_id')
        
        if not session_id:
            return create_api_response(None, False, "Session ID is required"), 400
        
        start_time = time.time()
        cart_items = Cart.query.filter_by(user_session=session_id).all()
        item_count = len(cart_items)
        
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('DELETE', f"DELETE FROM cart WHERE user_session = '{session_id}'", start_time, end_time, item_count)
        
        return create_api_response(None, True, "Cart cleared successfully")

class CartItemResource(Resource):
    def delete(self, item_id):
        # Remove specific item from cart
        start_time = time.time()
        cart_item = Cart.query.get(item_id)
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM cart WHERE id = {item_id}", start_time, end_time, 1 if cart_item else 0)
        
        if not cart_item:
            return create_api_response(None, False, "Cart item not found"), 404
        
        product_name = cart_item.product.name if cart_item.product else "Unknown"
        
        start_time = time.time()
        db.session.delete(cart_item)
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('DELETE', f"DELETE FROM cart WHERE id = {item_id}", start_time, end_time, 1)
        
        return create_api_response({
            'message': f'{product_name} removed from cart'
        }, True, "Item removed from cart successfully")
    
    def put(self, item_id):
        # Update cart item quantity
        data = request.get_json()
        
        if not data or 'quantity' not in data:
            return create_api_response(None, False, "Quantity is required"), 400
        
        quantity = data['quantity']
        
        if quantity <= 0:
            return create_api_response(None, False, "Quantity must be greater than 0"), 400
        
        start_time = time.time()
        cart_item = Cart.query.get(item_id)
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM cart WHERE id = {item_id}", start_time, end_time, 1 if cart_item else 0)
        
        if not cart_item:
            return create_api_response(None, False, "Cart item not found"), 404
        
        cart_item.quantity = quantity
        cart_item.updated_at = datetime.utcnow()
        
        start_time = time.time()
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('UPDATE', f"UPDATE cart SET quantity = {quantity} WHERE id = {item_id}", start_time, end_time, 1)
        
        return create_api_response({
            'message': 'Cart updated',
            'cart_item': cart_item.to_dict()
        }, True, "Cart item updated successfully")

class OrdersResource(Resource):
    def post(self):
        data = request.get_json()
        
        if not data or 'user_id' not in data or 'items' not in data:
            return create_api_response(None, False, "User ID and items are required"), 400
        
        # Create order
        total_amount = 0
        for item in data['items']:
            start_time = time.time()
            product = Product.query.get(item['product_id'])
            end_time = time.time()
            
            db_tracker.log_query('SELECT', f"SELECT * FROM products WHERE id = {item['product_id']}", start_time, end_time, 1 if product else 0)
            
            if product:
                total_amount += float(product.price) * item['quantity']
        
        new_order = Order(
            user_id=data['user_id'],
            total_amount=total_amount,
            status='pending',
            delivery_address=data.get('delivery_address', '')
        )
        
        start_time = time.time()
        db.session.add(new_order)
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('INSERT', f"INSERT INTO orders (user_id, total_amount, ...) VALUES ({data['user_id']}, {total_amount}, ...)", start_time, end_time, 1)
        
        # Add order items
        for item in data['items']:
            start_time = time.time()
            product = Product.query.get(item['product_id'])
            end_time = time.time()
            
            if product:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price=product.price
                )
                db.session.add(order_item)
        
        start_time = time.time()
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('INSERT', 'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (...)', start_time, end_time, len(data['items']))
        
        order_data = {
            'id': new_order.id,
            'user_id': new_order.user_id,
            'total_amount': float(new_order.total_amount),
            'status': new_order.status,
            'created_at': new_order.created_at.isoformat()
        }
        
        return create_api_response({'order': order_data}, True, "Order created successfully"), 201
    
    def get(self):
        user_id = request.args.get('user_id')
        
        if not user_id:
            return create_api_response(None, False, "User ID is required"), 400
        
        start_time = time.time()
        orders = Order.query.filter_by(user_id=user_id).all()
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f'SELECT * FROM orders WHERE user_id = {user_id}', start_time, end_time, len(orders))
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'user_id': order.user_id,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            })
        
        return create_api_response(orders_data)

# Debug endpoint for demo mode
class DebugResource(Resource):
    def get(self):
        if not db_tracker.enabled:
            return create_api_response(None, False, "Demo mode is not enabled"), 404
        
        recent_queries = db_tracker.get_recent_queries()
        return create_api_response({
            'all_queries': recent_queries,
            'recent_queries': recent_queries,
            'demo_mode': True
        })
    
    def delete(self):
        if not db_tracker.enabled:
            return create_api_response(None, False, "Demo mode is not enabled"), 404
        
        db_tracker.clear_queries()
        return create_api_response(None, True, "Query history cleared")

# DB Logs endpoint for widget
class DbLogsResource(Resource):
    def get(self):
        try:
            # Get all db logs, most recent first
            logs = DbLog.query.order_by(DbLog.timestamp.desc()).all()
            logs_data = [log.to_dict() for log in logs]
            
            return create_api_response({
                'logs': logs_data,
                'count': len(logs_data)
            })
        except Exception as e:
            return create_api_response(None, False, f"Failed to get logs: {str(e)}"), 500
    
    def delete(self):
        try:
            DbLog.query.delete()
            db.session.commit()
            return create_api_response(None, True, "All logs cleared")
        except Exception as e:
            db.session.rollback()
            return create_api_response(None, False, f"Failed to clear logs: {str(e)}"), 500

# -------------------------------
# REGISTER API ENDPOINTS
# -------------------------------

api.add_resource(UserResource, '/api/user')
api.add_resource(CategoriesResource, '/api/categories')
api.add_resource(ProductsResource, '/api/products')
api.add_resource(ProductResource, '/api/products/<int:product_id>')
api.add_resource(OrdersResource, '/api/orders')
api.add_resource(CartResource, '/api/cart')
api.add_resource(CartItemResource, '/api/cart/<int:item_id>')
api.add_resource(DebugResource, '/api/debug')
api.add_resource(DbLogsResource, '/api/db-logs')

# -------------------------------
# INITIALIZE DATABASE
# -------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Clear cart table on startup
        start_time = time.time()
        cart_items = Cart.query.all()
        item_count = len(cart_items)
        
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        end_time = time.time()
        
        if item_count > 0:
            db_tracker.log_query('DELETE', f"DELETE FROM cart (cleared {item_count} items on startup)", start_time, end_time, item_count)
        
        # Add sample data if not exists or update existing categories with proper icons
        categories_data = [
            ('Fruits & Vegetables', 'fas fa-carrot'),
            ('Dairy & Eggs', 'fas fa-glass-whiskey'),
            ('Meat & Seafood', 'fas fa-drumstick-bite'),
            ('Bakery', 'fas fa-bread-slice'),
            ('Beverages', 'fas fa-coffee'),
            ('Snacks', 'fas fa-cookie-bite')
        ]
        
        if Category.query.count() == 0:
            # Create new categories
            for name, icon in categories_data:
                category = Category(name=name, icon=icon)
                db.session.add(category)
            db.session.commit()
        else:
            # Update existing categories with proper icons
            for name, icon in categories_data:
                start_time = time.time()
                category = Category.query.filter_by(name=name).first()
                end_time = time.time()
                
                db_tracker.log_query('SELECT', f"SELECT * FROM categories WHERE name = '{name}'", start_time, end_time, 1 if category else 0)
                
                if category and category.icon != icon:
                    category.icon = icon
                    
                    start_time = time.time()
                    db.session.commit()
                    end_time = time.time()
                    
                    db_tracker.log_query('UPDATE', f"UPDATE categories SET icon = '{icon}' WHERE name = '{name}'", start_time, end_time, 1)
            
            # Add sample products
            products = [
                Product(name='Fresh Apples', description='Red delicious apples', price=2.99, stock=50, category_id=1, image_url='https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300'),
                Product(name='Bananas', description='Fresh yellow bananas', price=1.49, stock=100, category_id=1, image_url='https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=300'),
                Product(name='Organic Milk', description='Fresh organic milk', price=3.49, stock=30, category_id=2, image_url='https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300'),
                Product(name='Free Range Eggs', description='Dozen free range eggs', price=4.99, stock=25, category_id=2, image_url='https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=300'),
                Product(name='Chicken Breast', description='Fresh chicken breast', price=8.99, stock=20, category_id=3, image_url='https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=300'),
                Product(name='Salmon Fillet', description='Fresh salmon fillet', price=12.99, stock=15, category_id=3, image_url='https://images.unsplash.com/photo-1519708227418-c8c6c49d4ded?w=300'),
                Product(name='Whole Wheat Bread', description='Fresh whole wheat bread', price=2.49, stock=40, category_id=4, image_url='https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300'),
                Product(name='Croissants', description='Buttery croissants', price=5.99, stock=20, category_id=4, image_url='https://images.unsplash.com/photo-1551024506-0bccd828d307?w=300'),
                Product(name='Orange Juice', description='Fresh orange juice', price=3.99, stock=35, category_id=5, image_url='https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=300'),
                Product(name='Potato Chips', description='Crispy potato chips', price=2.99, stock=60, category_id=6, image_url='https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=300')
            ]
            
            for product in products:
                db.session.add(product)
            db.session.commit()
            
            print("Database initialized with sample data!")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 