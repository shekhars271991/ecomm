from datetime import datetime

def create_order_models(db):
    """Factory function to create Order and OrderItem models with initialized db"""
    
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
            from models.product import create_product_model
            Product = create_product_model(db)
            product = Product.query.get(self.product_id)
            return {
                'id': self.id,
                'order_id': self.order_id,
                'product_id': self.product_id,
                'quantity': self.quantity,
                'price': float(self.price),
                'product': product.to_dict() if product else None
            }
    
    return Order, OrderItem 