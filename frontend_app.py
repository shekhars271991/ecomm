from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Backend API URL
API_BASE_URL = 'http://localhost:5001/api'

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def make_api_request(endpoint, method='GET', data=None, params=None):
    """Make API request to backend"""
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        
        if response.status_code in [200, 201]:
            return response.json(), True
        else:
            return response.json(), False
    except Exception as e:
        return {'error': str(e)}, False

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def index():
    # Get categories
    categories_data, success = make_api_request('categories')
    categories = categories_data.get('data', []) if success else []
    
    # Get featured products
    products_data, success = make_api_request('products')
    featured_products = products_data.get('data', [])[:8] if success else []
    
    return render_template('index.html', categories=categories, featured_products=featured_products)

@app.route('/products')
def products():
    category_id = request.args.get('category')
    search = request.args.get('search', '')
    
    params = {}
    if category_id:
        params['category'] = category_id
    if search:
        params['search'] = search
    
    products_data, success = make_api_request('products', params=params)
    products = products_data.get('data', []) if success else []
    
    categories_data, success = make_api_request('categories')
    categories = categories_data.get('data', []) if success else []
    
    return render_template('products.html', products=products, categories=categories, 
                         current_category=int(category_id) if category_id else None)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product_data, success = make_api_request(f'products/{product_id}')
    
    if not success:
        flash('Product not found', 'error')
        return redirect(url_for('products'))
    
    product = product_data.get('product')
    return render_template('product_detail.html', product=product)

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = {}
    
    # Convert cart to API format
    cart_items = []
    for product_id, quantity in session['cart'].items():
        cart_items.append({
            'product_id': int(product_id),
            'quantity': quantity
        })
    
    if cart_items:
        cart_data, success = make_api_request('cart', method='POST', data={'cart_items': cart_items})
        if success:
            cart_items = cart_data.get('cart_items', [])
            total = cart_data.get('total', 0)
        else:
            cart_items = []
            total = 0
    else:
        cart_items = []
        total = 0
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {}
    
    product_id_str = str(product_id)
    if product_id_str in session['cart']:
        session['cart'][product_id_str] += quantity
    else:
        session['cart'][product_id_str] = quantity
    
    session.modified = True
    
    # Get product name for flash message
    product_data, success = make_api_request(f'products/{product_id}')
    if success and product_data:
        product = product_data.get('product', {})
        product_name = product.get('name', 'Product') if product else 'Product'
        flash(f'{product_name} added to cart!', 'success')
    
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
    
    # Calculate total using cart API
    cart_items = []
    for product_id, quantity in session['cart'].items():
        cart_items.append({
            'product_id': int(product_id),
            'quantity': quantity
        })
    
    cart_data, success = make_api_request('cart', method='POST', data={'cart_items': cart_items})
    total = cart_data.get('total', 0) if success else 0
    
    user = session.get('user_data', {})
    return render_template('checkout.html', total=total, user=user)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    user = session.get('user_data', {})
    delivery_address = request.form.get('delivery_address', user.get('address', ''))
    
    # Prepare order data
    cart_items = []
    for product_id, quantity in session['cart'].items():
        cart_items.append({
            'product_id': int(product_id),
            'quantity': quantity
        })
    
    # Get cart total and items with prices
    cart_data, success = make_api_request('cart', method='POST', data={'cart_items': cart_items})
    if not success:
        flash('Error processing cart', 'error')
        return redirect(url_for('cart'))
    
    # Prepare order items for API
    order_items = []
    for item in cart_data.get('cart_items', []):
        order_items.append({
            'product_id': item['product']['id'],
            'quantity': item['quantity'],
            'price': item['product']['price']
        })
    
    order_data = {
        'user_id': session['user_id'],
        'total_amount': cart_data.get('total', 0) + 2.99,  # Add delivery fee
        'delivery_address': delivery_address,
        'items': order_items
    }
    
    # Create order via API
    result, success = make_api_request('orders', method='POST', data=order_data)
    
    if success:
        # Clear cart
        session['cart'] = {}
        session.modified = True
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation', order_id=result['order']['id']))
    else:
        flash('Error placing order', 'error')
        return redirect(url_for('checkout'))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'user_id' not in session:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    order_data, success = make_api_request(f'orders/{order_id}')
    
    if not success:
        flash('Order not found', 'error')
        return redirect(url_for('orders'))
    
    order = order_data.get('order')
    if order['user_id'] != session['user_id']:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order)

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    orders_data, success = make_api_request('orders', params={'user_id': session['user_id']})
    user_orders = orders_data.get('orders', []) if success else []
    
    return render_template('orders.html', orders=user_orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_data = {
            'action': 'login',
            'email': email,
            'password': password
        }
        
        result, success = make_api_request('user', method='POST', data=user_data)
        
        if success:
            user = result.get('user')
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_data'] = user
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash(result.get('error', 'Login failed'), 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            'action': 'register',
            'email': request.form['email'],
            'password': request.form['password'],
            'name': request.form['name'],
            'address': request.form['address'],
            'phone': request.form['phone']
        }
        
        result, success = make_api_request('user', method='POST', data=user_data)
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result.get('error', 'Registration failed'), 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000) 