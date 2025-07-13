from .user import create_user_resource
from .products import create_product_resources
from .cart import create_cart_resources
from .orders import create_orders_resource
from .debug import create_debug_resources
from .database import create_database_resource


def init_api_resources(db, models, db_manager, utils):
    """Initialize all API resources with dependencies"""
    
    # Extract utils
    db_tracker = utils['db_tracker']
    time_api_call = utils['time_api_call']
    create_api_response = utils['create_api_response']
    safe_get_json = utils['safe_get_json']
    
    # Create all resource classes
    UserResource = create_user_resource(db, models, db_tracker, create_api_response)
    
    CategoriesResource, ProductsResource, ProductResource = create_product_resources(
        db_manager, time_api_call, create_api_response
    )
    
    CartResource, CartItemResource = create_cart_resources(
        db, models, db_manager, db_tracker, time_api_call, create_api_response, safe_get_json
    )
    
    OrdersResource = create_orders_resource(db, models, db_tracker, create_api_response)
    
    DebugResource, DbLogsResource, ApiLogsResource = create_debug_resources(
        db, models, db_tracker, create_api_response
    )
    
    DatabaseSwitchResource = create_database_resource(db_manager, time_api_call, create_api_response)
    
    return {
        'UserResource': UserResource,
        'CategoriesResource': CategoriesResource,
        'ProductsResource': ProductsResource,
        'ProductResource': ProductResource,
        'CartResource': CartResource,
        'CartItemResource': CartItemResource,
        'OrdersResource': OrdersResource,
        'DebugResource': DebugResource,
        'DbLogsResource': DbLogsResource,
        'ApiLogsResource': ApiLogsResource,
        'DatabaseSwitchResource': DatabaseSwitchResource
    }
