from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def create_user_model(db):
    """Factory function to create User model with initialized db"""
    
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
    
    return User 