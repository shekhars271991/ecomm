from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------
# DATABASE MODELS
# -------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50))
    
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered, cancelled
    delivery_address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='order_items')

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def index():
    categories = Category.query.all()
    featured_products = Product.query.filter_by(is_available=True).limit(8).all()
    return render_template('index.html', categories=categories, featured_products=featured_products)

@app.route('/products')
def products():
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_available=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.all()
    categories = Category.query.all()
    
    return render_template('products.html', products=products, categories=categories, 
                         current_category=int(category_id) if category_id else None)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = {}
    
    cart_items = []
    total = 0
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    product_id_str = str(product_id)
    if product_id_str in session['cart']:
        session['cart'][product_id_str] += quantity
    else:
        session['cart'][product_id_str] = quantity
    
    session.modified = True
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('products'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        product_id_str = str(product_id)
        if product_id_str in session['cart']:
            del session['cart'][product_id_str]
            session.modified = True
            flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' in session:
        product_id_str = str(product_id)
        if quantity > 0:
            session['cart'][product_id_str] = quantity
        else:
            del session['cart'][product_id_str]
        session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout', 'error')
        return redirect(url_for('login'))
    
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    # Calculate total
    total = 0
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * quantity
    
    user = User.query.get(session['user_id'])
    return render_template('checkout.html', total=total, user=user)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    user = User.query.get(session['user_id'])
    delivery_address = request.form.get('delivery_address', user.address)
    
    # Calculate total and create order
    total = 0
    order = Order(user_id=session['user_id'], total_amount=0, delivery_address=delivery_address)
    db.session.add(order)
    db.session.flush()  # Get order ID
    
    for product_id, quantity in session['cart'].items():
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            total += item_total
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )
            db.session.add(order_item)
    
    order.total_amount = total
    db.session.commit()
    
    # Clear cart
    session['cart'] = {}
    session.modified = True
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_confirmation', order_id=order.id))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if 'user_id' not in session or order.user_id != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order)

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(email=email, name=name, address=address, phone=phone)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# -------------------------------
# INITIALIZATION
# -------------------------------

def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample categories
        if not Category.query.first():
            categories = [
                Category(name='Fruits & Vegetables', icon='🥕'),
                Category(name='Dairy & Eggs', icon='🥛'),
                Category(name='Meat & Seafood', icon='🥩'),
                Category(name='Bakery', icon='🍞'),
                Category(name='Beverages', icon='🥤'),
                Category(name='Snacks', icon='🍿')
            ]
            for category in categories:
                db.session.add(category)
            
            # Add sample products
            products = [
                Product(name='Fresh Bananas', description='Ripe yellow bananas', price=2.99, category_id=1, stock=50, image_url='https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=300&h=200&fit=crop'),
                Product(name='Organic Apples', description='Crisp red apples', price=3.49, category_id=1, stock=30, image_url='https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300&h=200&fit=crop'),
                Product(name='Whole Milk', description='Fresh whole milk 1L', price=3.29, category_id=2, stock=20, image_url='https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=200&fit=crop'),
                Product(name='Free Range Eggs', description='Dozen organic eggs', price=4.99, category_id=2, stock=15, image_url='https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=300&h=200&fit=crop'),
                Product(name='Salmon Fillet', description='Fresh Atlantic salmon', price=12.99, category_id=3, stock=10, image_url='https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=300&h=200&fit=crop'),
                Product(name='Chicken Breast', description='Boneless chicken breast', price=8.99, category_id=3, stock=25, image_url='https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=300&h=200&fit=crop'),
                Product(name='Sourdough Bread', description='Artisan sourdough loaf', price=4.49, category_id=4, stock=12, image_url='https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=200&fit=crop'),
                Product(name='Orange Juice', description='Fresh squeezed orange juice', price=4.99, category_id=5, stock=18, image_url='https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=300&h=200&fit=crop'),
                Product(name='Potato Chips', description='Crispy potato chips', price=2.49, category_id=6, stock=40, image_url='https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=300&h=200&fit=crop'),
                Product(name='Greek Yogurt', description='Creamy Greek yogurt', price=1.99, category_id=2, stock=35, image_url='https://images.unsplash.com/photo-1571212515416-8fc82f26c7c2?w=300&h=200&fit=crop')
            ]
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 