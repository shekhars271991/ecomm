import time
from flask import request
from flask_restful import Resource


def create_orders_resource(db, models, db_tracker, create_api_response):
    """Factory function to create OrdersResource with initialized dependencies"""
    
    Order = models['Order']
    OrderItem = models['OrderItem']
    Product = models['Product']
    
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
    
    return OrdersResource 