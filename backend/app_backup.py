from flask import Flask, request, jsonify, session, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from datetime import datetime
import os
import time
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from unified_database_manager import UnifiedDatabaseManager
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://grocery_user:grocery_password@localhost:3306/grocery_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable demo mode for showing database operations
app.config['DEMO_MODE'] = True

db = SQLAlchemy(app)
api = Api(app)

# Configure CORS to allow all content types and methods
CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:4000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Initialize database manager
db_manager = UnifiedDatabaseManager()

# Add request hook to ensure proper content type handling
@app.before_request
def before_request():
    # For OPTIONS requests, return immediately
    if request.method == 'OPTIONS':
        return
    
    # For POST/PUT requests, ensure content type is set
    if request.method in ['POST', 'PUT'] and request.content_type is None:
        # If no content type is set but we have data, assume JSON
        if request.data:
            request.content_type = 'application/json'

# Demo mode: Track database operations
class DatabaseTracker:
    def __init__(self):
        self.enabled = app.config.get('DEMO_MODE', False)
    
    def log_query(self, query_type, query, start_time, end_time, result_count=None, database_type='mysql'):
        if not self.enabled:
            return
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Format the operation string
        operation = f"{query_type}: {str(query)}"
        
        # Debug output
        print(f"📊 Logging {database_type} query: {operation[:100]}...")
        
        # Create and save the log entry
        log_entry = DbLog(
            operation=operation,
            database_type=database_type,
            response_count=result_count or 0,
            time_taken_ms=round(duration, 2)
        )
        
        try:
            # Ensure we have an active Flask app context
            from flask import has_app_context
            if not has_app_context():
                print("❌ No Flask app context for logging")
                return
                
            db.session.add(log_entry)
            db.session.commit()
            print(f"✅ Successfully logged {database_type} query")
        except Exception as e:
            # If we can't log to db, just continue - don't break the app
            db.session.rollback()
            print(f"❌ Failed to log {database_type} query: {e}")
            # Also print more details for debugging
            print(f"   Query: {operation}")
            print(f"   Database type: {database_type}")
            print(f"   Error type: {type(e).__name__}")
    
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
    
    def log_api_call(self, endpoint, method, status_code, start_time, end_time, session_id=None, database_type='mysql'):
        if not self.enabled:
            return
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Debug output
        print(f"🌐 Logging API call: {method} {endpoint} - {status_code} ({duration:.2f}ms)")
        
        # Create and save the API log entry
        log_entry = ApiLog(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            time_taken_ms=round(duration, 2),
            database_type=database_type,
            session_id=session_id
        )
        
        try:
            # Ensure we have an active Flask app context
            from flask import has_app_context
            if not has_app_context():
                print("❌ No Flask app context for API logging")
                return
                
            db.session.add(log_entry)
            db.session.commit()
            print(f"✅ Successfully logged API call")
        except Exception as e:
            # If we can't log to db, just continue - don't break the app
            db.session.rollback()
            print(f"❌ Failed to log API call: {e}")
    
    def get_recent_api_logs(self):
        # Get last 20 API logs from database, most recent first
        try:
            logs = ApiLog.query.order_by(ApiLog.timestamp.desc()).limit(20).all()
            return [log.to_dict() for log in logs]
        except Exception as e:
            print(f"Failed to get recent API logs: {e}")
            return []
    
    def clear_api_logs(self):
        try:
            ApiLog.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Failed to clear API logs: {e}")

# Global tracker instance
db_tracker = DatabaseTracker()

# API timing decorator
import functools

def time_api_call(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Get request info
        endpoint = request.path  # Use the actual path instead of endpoint name
        method = request.method
        session_id = request.args.get('session_id')
        
        # Only try to get session_id from JSON for POST/PUT requests
        if method in ['POST', 'PUT'] and request.content_type == 'application/json':
            try:
                json_data = request.get_json(silent=True)
                if json_data and 'session_id' in json_data:
                    session_id = json_data['session_id']
            except:
                pass
        
        try:
            # Execute the original function
            result = f(*args, **kwargs)
            
            # Determine status code
            if isinstance(result, tuple):
                status_code = result[1] if len(result) > 1 else 200
            else:
                status_code = 200
                
        except Exception as e:
            end_time = time.time()
            # Log failed API call
            db_tracker.log_api_call(
                endpoint=endpoint,
                method=method,
                status_code=500,
                start_time=start_time,
                end_time=end_time,
                session_id=session_id,
                database_type=db_manager.get_current_database()
            )
            raise  # Re-raise the exception
        
        end_time = time.time()
        
        # Log successful API call
        db_tracker.log_api_call(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            start_time=start_time,
            end_time=end_time,
            session_id=session_id,
            database_type=db_manager.get_current_database()
        )
        
        return result
    
    return decorated_function

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
    
    db_tracker.log_query(operation_type, query_info, start_time, end_time, result_count, database_type='mysql')
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

def safe_get_json():
    """Safely get JSON data from request, handling content type issues"""
    try:
        # Try to get JSON data directly
        return request.get_json(force=True)
    except Exception as e:
        # If that fails, return None
        return None

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
    database_type = db.Column(db.String(50), nullable=False, default='mysql')  # Track which database was used
    response_count = db.Column(db.Integer, default=0)
    time_taken_ms = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'operation': self.operation,
            'database_type': self.database_type,
            'response_count': self.response_count,
            'time_taken_ms': self.time_taken_ms,
            'timestamp': self.timestamp.strftime('%H:%M:%S')
        }

class ApiLog(db.Model):
    __tablename__ = 'api_logs'
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(200), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    time_taken_ms = db.Column(db.Float, nullable=False)
    database_type = db.Column(db.String(50), nullable=False, default='mysql')
    session_id = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'time_taken_ms': self.time_taken_ms,
            'database_type': self.database_type,
            'session_id': self.session_id,
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
        
        db_tracker.log_query('SELECT', f"SELECT * FROM users WHERE email = '{data['email']}'", start_time, end_time, 1 if existing_user else 0, database_type='mysql')
        
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
            
            db_tracker.log_query('INSERT', f"INSERT INTO users (email, name, ...) VALUES ('{data['email']}', '{data['name']}', ...)", start_time, end_time, 1, database_type='mysql')
            
            user_data = {
                'id': new_user.id,
                'email': new_user.email,
                'name': new_user.name,
                'address': new_user.address,
                'phone': new_user.phone
            }
            
            return create_api_response({'user': user_data}, True, "Registration successful"), 201

class CategoriesResource(Resource):
    @time_api_call
    def get(self):
        categories_data = db_manager.get_all_categories()
        return create_api_response(categories_data)

class ProductsResource(Resource):
    @time_api_call
    def get(self):
        # Get query parameters
        category_id = request.args.get('category')
        search_term = request.args.get('search')
        
        # Convert category_id to int if provided
        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                category_id = None
        else:
            category_id = None
        
        products_data = db_manager.get_all_products(category_id, search_term)
        return create_api_response(products_data)

class ProductResource(Resource):
    def get(self, product_id):
        product_data = db_manager.get_product_by_id(product_id)
        
        if not product_data:
            return create_api_response(None, False, "Product not found"), 404
        
        return create_api_response({'product': product_data})

class CartResource(Resource):
    @time_api_call
    def get(self):
        # Get cart items for current session
        session_id = request.args.get('session_id')
        
        if not session_id:
            return create_api_response(None, False, "Session ID is required"), 400
        
        cart_items = db_manager.get_cart_items(session_id)
        
        processed_cart_items = []
        total = 0
        total_quantity = 0
        
        for cart_item in cart_items:
            processed_cart_items.append(cart_item)
            total += cart_item.get('total', 0)
            total_quantity += cart_item.get('quantity', 0)
        
        # Apply 10% discount if total quantity > 5
        discount_amount = 0
        discount_percentage = 0
        if total_quantity > 5:
            discount_percentage = 10
            discount_amount = total * 0.10
        
        final_total = total - discount_amount
        
        return create_api_response({
            'cart_items': processed_cart_items,
            'subtotal': total,
            'total_quantity': total_quantity,
            'discount_percentage': discount_percentage,
            'discount_amount': discount_amount,
            'total': final_total
        }, True, "Cart retrieved successfully")
    
    @time_api_call
    def post(self):
        # Add item to cart
        data = safe_get_json()
        
        if not data or 'session_id' not in data or 'product_id' not in data:
            return create_api_response(None, False, "Session ID and product ID are required"), 400
        
        session_id = data['session_id']
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        result = db_manager.add_to_cart(session_id, product_id, quantity)
        
        if result['success']:
            return create_api_response({
                'message': result['message'],
                'product': result['product']
            }, True, "Item added to cart successfully")
        else:
            return create_api_response(None, False, result['message']), 400
    
    @time_api_call
    def delete(self):
        # Clear cart for session
        session_id = request.args.get('session_id')
        
        if not session_id:
            return create_api_response(None, False, "Session ID is required"), 400
        
        result = db_manager.clear_cart(session_id)
        
        if result['success']:
            return create_api_response(None, True, "Cart cleared successfully")
        else:
            return create_api_response(None, False, result['message']), 400

class CartItemResource(Resource):
    def delete(self, item_id):
        # Remove specific item from cart
        start_time = time.time()
        cart_item = Cart.query.get(item_id)
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM cart WHERE id = {item_id}", start_time, end_time, 1 if cart_item else 0, database_type='mysql')
        
        if not cart_item:
            return create_api_response(None, False, "Cart item not found"), 404
        
        product_name = cart_item.product.name if cart_item.product else "Unknown"
        
        start_time = time.time()
        db.session.delete(cart_item)
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('DELETE', f"DELETE FROM cart WHERE id = {item_id}", start_time, end_time, 1, database_type='mysql')
        
        return create_api_response({
            'message': f'{product_name} removed from cart'
        }, True, "Item removed from cart successfully")
    
    def put(self, item_id):
        # Update cart item quantity
        data = safe_get_json()
        
        if not data or 'quantity' not in data:
            return create_api_response(None, False, "Quantity is required"), 400
        
        quantity = data['quantity']
        
        if quantity <= 0:
            return create_api_response(None, False, "Quantity must be greater than 0"), 400
        
        start_time = time.time()
        cart_item = Cart.query.get(item_id)
        end_time = time.time()
        
        db_tracker.log_query('SELECT', f"SELECT * FROM cart WHERE id = {item_id}", start_time, end_time, 1 if cart_item else 0, database_type='mysql')
        
        if not cart_item:
            return create_api_response(None, False, "Cart item not found"), 404
        
        cart_item.quantity = quantity
        cart_item.updated_at = datetime.utcnow()
        
        start_time = time.time()
        db.session.commit()
        end_time = time.time()
        
        db_tracker.log_query('UPDATE', f"UPDATE cart SET quantity = {quantity} WHERE id = {item_id}", start_time, end_time, 1, database_type='mysql')
        
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
            
            db_tracker.log_query('SELECT', f"SELECT * FROM products WHERE id = {item['product_id']}", start_time, end_time, 1 if product else 0, database_type='mysql')
            
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
        
        db_tracker.log_query('INSERT', f"INSERT INTO orders (user_id, total_amount, ...) VALUES ({data['user_id']}, {total_amount}, ...)", start_time, end_time, 1, database_type='mysql')
        
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
        
        db_tracker.log_query('INSERT', 'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (...)', start_time, end_time, len(data['items']), database_type='mysql')
        
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
        
        db_tracker.log_query('SELECT', f'SELECT * FROM orders WHERE user_id = {user_id}', start_time, end_time, len(orders), database_type='mysql')
        
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
            # Get database type filter from query parameters
            database_type = request.args.get('database_type')
            
            # Start with base query
            query = DbLog.query
            
            # Apply database type filter if provided
            if database_type and database_type in ['mysql', 'aerospike']:
                query = query.filter_by(database_type=database_type)
            
            # Get logs ordered by timestamp desc
            logs = query.order_by(DbLog.timestamp.desc()).all()
            logs_data = [log.to_dict() for log in logs]
            
            return create_api_response({
                'logs': logs_data,
                'count': len(logs_data),
                'database_type_filter': database_type
            })
        except Exception as e:
            return create_api_response(None, False, f"Failed to get logs: {str(e)}"), 500
    
    def delete(self):
        try:
            # Get database type filter from query parameters
            database_type = request.args.get('database_type')
            
            # Start with base query
            query = DbLog.query
            
            # Apply database type filter if provided
            if database_type and database_type in ['mysql', 'aerospike']:
                query = query.filter_by(database_type=database_type)
            
            # Delete filtered logs
            deleted_count = query.delete()
            db.session.commit()
            
            filter_msg = f" for {database_type} database" if database_type else ""
            return create_api_response(
                {'deleted_count': deleted_count}, 
                True, 
                f"Logs cleared{filter_msg}"
            )
        except Exception as e:
            db.session.rollback()
            return create_api_response(None, False, f"Failed to clear logs: {str(e)}"), 500

# API Logs endpoint for widget
class ApiLogsResource(Resource):
    def get(self):
        try:
            # Get database type filter from query parameters
            database_type = request.args.get('database_type')
            
            # Start with base query
            query = ApiLog.query
            
            # Apply database type filter if provided
            if database_type and database_type in ['mysql', 'aerospike']:
                query = query.filter_by(database_type=database_type)
            
            # Get logs ordered by timestamp desc
            logs = query.order_by(ApiLog.timestamp.desc()).all()
            logs_data = [log.to_dict() for log in logs]
            
            return create_api_response({
                'logs': logs_data,
                'count': len(logs_data),
                'database_type_filter': database_type
            })
        except Exception as e:
            return create_api_response(None, False, f"Failed to get API logs: {str(e)}"), 500
    
    def delete(self):
        try:
            # Get database type filter from query parameters
            database_type = request.args.get('database_type')
            
            # Start with base query
            query = ApiLog.query
            
            # Apply database type filter if provided
            if database_type and database_type in ['mysql', 'aerospike']:
                query = query.filter_by(database_type=database_type)
            
            # Delete filtered logs
            deleted_count = query.delete()
            db.session.commit()
            
            filter_msg = f" for {database_type} database" if database_type else ""
            return create_api_response(
                {'deleted_count': deleted_count}, 
                True, 
                f"API logs cleared{filter_msg}"
            )
        except Exception as e:
            db.session.rollback()
            return create_api_response(None, False, f"Failed to clear API logs: {str(e)}"), 500

# Database switching endpoint
class DatabaseSwitchResource(Resource):
    @time_api_call
    def get(self):
        """Get current database type"""
        current_db = db_manager.get_current_database()
        return create_api_response({
            'current_database': current_db,
            'available_databases': ['mysql', 'aerospike']
        })
    
    @time_api_call
    def post(self):
        """Switch database type"""
        data = request.get_json()
        
        if not data or 'database' not in data:
            return create_api_response(None, False, "Database type is required"), 400
        
        db_type = data['database']
        
        if db_type not in ['mysql', 'aerospike']:
            return create_api_response(None, False, "Invalid database type. Must be 'mysql' or 'aerospike'"), 400
        
        try:
            db_manager.set_database(db_type)
            
            # Note: Sample data initialization removed to preserve CSV data
            # Sample data can be manually initialized if needed
            
            return create_api_response({
                'current_database': db_type,
                'message': f'Successfully switched to {db_type} database'
            }, True, f"Database switched to {db_type}")
        except Exception as e:
            return create_api_response(None, False, f"Failed to switch database: {str(e)}"), 500

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
api.add_resource(ApiLogsResource, '/api/api-logs')
api.add_resource(DatabaseSwitchResource, '/api/database-switch')

# -------------------------------
# INITIALIZE DATABASE
# -------------------------------

def initialize_database(force_refresh=False, dataloader_type='file'):
    """Initialize database with optional force refresh and dataloader type"""
    try:
        # Try to create tables
        db.create_all()
        print("✅ Database tables created/verified successfully")
        
        # Add database_type column to db_logs table if it doesn't exist
        try:
            # Check if column exists by trying to query it
            db.session.execute(db.text("SELECT database_type FROM db_logs LIMIT 1"))
        except Exception:
            # Column doesn't exist, add it
            try:
                db.session.execute(db.text("ALTER TABLE db_logs ADD COLUMN database_type VARCHAR(50) NOT NULL DEFAULT 'mysql'"))
                db.session.commit()
                print("✅ Added database_type column to db_logs table")
            except Exception as e:
                db.session.rollback()
                print(f"⚠️  Failed to add database_type column: {e}")
        
        # Check if api_logs table exists, if not it will be created by db.create_all()
        try:
            db.session.execute(db.text("SELECT COUNT(*) FROM api_logs"))
            print("✅ API logs table exists")
        except Exception:
            print("ℹ️  API logs table will be created")
        
        # Initialize database manager
        models = {
            'Category': Category,
            'Product': Product,
            'Cart': Cart
        }
        db_manager.initialize(app, db, db_tracker, models)
        
        # Clear cart table on startup
        clear_cart_on_startup()
        
        # Check if we need to load data
        should_load_data = force_refresh or should_load_initial_data()
        
        if should_load_data:
            if dataloader_type == 'default':
                # Load sample data for Aerospike
                if db_manager.aerospike_manager.is_available():
                    db_manager.aerospike_manager.init_sample_data()
                    print("✅ Sample data loaded successfully!")
                else:
                    print("⚠️  Aerospike not available for sample data")
            else:
                # Load CSV data (default behavior)
                load_initial_data(force_refresh)
        else:
            print(f"✅ Database already contains {Category.query.count()} categories and {Product.query.count()} products - skipping data load")
            
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  This might be due to:")
        print("   - MySQL container not running (run: docker-compose up -d)")
        print("   - Database credentials incorrect")
        print("   - Network connection issues")
        return False

def clear_cart_on_startup():
    """Clear cart table on startup"""
    try:
        start_time = time.time()
        cart_items = Cart.query.all()
        item_count = len(cart_items)
        
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        end_time = time.time()
        
        if item_count > 0:
            db_tracker.log_query('DELETE', f"DELETE FROM cart (cleared {item_count} items on startup)", start_time, end_time, item_count, database_type='mysql')
            print(f"✅ Cleared {item_count} cart items on startup")
        
    except Exception as e:
        print(f"⚠️  Failed to clear cart on startup: {e}")
        if db:
            db.session.rollback()

def should_load_initial_data():
    """Check if we should load initial data"""
    try:
        category_count = Category.query.count()
        product_count = Product.query.count()
        
        # Load data if either table is empty
        if category_count == 0 or product_count == 0:
            print(f"📊 Database check: {category_count} categories, {product_count} products")
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Failed to check database state: {e}")
        return True  # Default to loading if we can't check

def load_initial_data(force_refresh=False):
    """Load initial data from CSV"""
    try:
        if force_refresh:
            print("🔄 Force refresh requested - loading fresh data...")
        else:
            print("📦 Database is empty, loading data from CSV file...")
        
        from csv_data_loader import CSVDataLoader
        
        # Get the individual managers from the unified manager
        mysql_manager = db_manager.mysql_manager
        aerospike_manager = db_manager.aerospike_manager
        mongo_manager = db_manager.mongo_manager
        
        # Create CSV loader with all three managers
        csv_loader = CSVDataLoader(mysql_manager, aerospike_manager, mongo_manager)
        
        # Load data from CSV
        csv_file_path = os.path.join(os.path.dirname(__file__), 'datasets', 'GroceryDataset.csv')
        
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV file not found: {csv_file_path}")
            return False
        
        # Skip truncation if not force refresh and data already exists
        skip_truncate = not force_refresh and not should_load_initial_data()
        
        csv_loader.load_all_data(csv_file_path, skip_truncate=skip_truncate)
        
        print("✅ Data loaded successfully from CSV file!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading data from CSV: {e}")
        print("⚠️  CSV data loading failed - check that CSV file exists and is readable")
        return False

if __name__ == '__main__':
    # Check for command line parameters
    force_refresh = '--refresh' in sys.argv or '-r' in sys.argv
    
    # Check for dataloader type parameter
    dataloader_type = 'file'  # Default to CSV file
    if '--dataloader' in sys.argv:
        try:
            dataloader_index = sys.argv.index('--dataloader')
            if dataloader_index + 1 < len(sys.argv):
                dataloader_type = sys.argv[dataloader_index + 1]
        except (IndexError, ValueError):
            dataloader_type = 'file'
    
    if force_refresh:
        if dataloader_type == 'default':
            print("🔄 Force refresh mode enabled with sample data")
        else:
            print("🔄 Force refresh mode enabled with CSV data")
    else:
        if dataloader_type == 'default':
            print("🚀 Starting with sample data")
        else:
            print("🚀 Starting with CSV data")
    
    with app.app_context():
        # Initialize database
        if not initialize_database(force_refresh, dataloader_type):
            print("❌ Failed to initialize database. Application cannot start.")
            sys.exit(1)
        
        print("✅ Database initialization complete")
    
    print("🚀 Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5001) 