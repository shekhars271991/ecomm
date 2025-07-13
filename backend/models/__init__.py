from .user import create_user_model
from .category import create_category_model
from .product import create_product_model
from .order import create_order_models
from .cart import create_cart_model
from .logs import create_log_models

def init_models(db):
    """Initialize all models with the database instance"""
    
    # Create all models
    User = create_user_model(db)
    Category = create_category_model(db)
    Product = create_product_model(db)
    Order, OrderItem = create_order_models(db)
    Cart = create_cart_model(db)
    DbLog, ApiLog = create_log_models(db)
    
    # Return all models as a dictionary for easy access
    return {
        'User': User,
        'Category': Category,
        'Product': Product,
        'Order': Order,
        'OrderItem': OrderItem,
        'Cart': Cart,
        'DbLog': DbLog,
        'ApiLog': ApiLog
    }
