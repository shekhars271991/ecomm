import time
from datetime import datetime
from flask import request
from flask_restful import Resource


def create_cart_resources(db, models, db_manager, db_tracker, time_api_call, create_api_response, safe_get_json):
    """Factory function to create cart-related resources with initialized dependencies"""
    
    Cart = models['Cart']
    
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
    
    return CartResource, CartItemResource 