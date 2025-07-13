from datetime import datetime

def create_product_model(db):
    """Factory function to create Product model with initialized db"""
    
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
    
    return Product 