def create_category_model(db):
    """Factory function to create Category model with initialized db"""
    
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
    
    return Category 