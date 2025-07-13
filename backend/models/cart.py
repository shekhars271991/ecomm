from datetime import datetime

def create_cart_model(db):
    """Factory function to create Cart model with initialized db"""
    
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
    
    return Cart 