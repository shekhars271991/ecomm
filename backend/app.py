import sys
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_cors import CORS
from unified_database_manager import UnifiedDatabaseManager

# Import the new modules
from models import init_models
from utils import init_utils
from api import init_api_resources
from database import init_database_functions

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://grocery_user:grocery_password@localhost:3306/grocery_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable demo mode for showing database operations
app.config['DEMO_MODE'] = True

db = SQLAlchemy(app)
api = Api(app)

# Configure CORS to allow all content types and methods
CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:4000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-Database', 'X-Suppress-Logging'],
     supports_credentials=True)

# Initialize database manager
db_manager = UnifiedDatabaseManager()

# Add request hook to ensure proper content type handling
@app.before_request
def before_request():
    # For OPTIONS requests, return immediately
    if request.method == 'OPTIONS':
        return
    
    # Handle database switching via X-Database header
    database_header = request.headers.get('X-Database')
    if database_header and database_header in ['mysql', 'aerospike', 'mongodb']:
        db_manager.set_database(database_header)
    
    # Check for suppress logging header
    suppress_logging = request.headers.get('X-Suppress-Logging')
    if suppress_logging == '1':
        # Temporarily disable logging for load tests
        if hasattr(db_manager, 'mysql_manager') and db_manager.mysql_manager.db_tracker:
            db_manager.mysql_manager.db_tracker.enabled = False
        if hasattr(db_manager, 'aerospike_manager') and db_manager.aerospike_manager.db_tracker:
            db_manager.aerospike_manager.db_tracker.enabled = False
        if hasattr(db_manager, 'mongo_manager') and db_manager.mongo_manager.db_tracker:
            db_manager.mongo_manager.db_tracker.enabled = False
    
    # For POST/PUT requests, ensure content type is set
    if request.method in ['POST', 'PUT'] and request.content_type is None:
        # If no content type is set but we have data, assume JSON
        if request.data:
            request.content_type = 'application/json'

@app.after_request
def after_request(response):
    # Re-enable logging after request completes
    if hasattr(db_manager, 'mysql_manager') and db_manager.mysql_manager.db_tracker:
        db_manager.mysql_manager.db_tracker.enabled = True
    if hasattr(db_manager, 'aerospike_manager') and db_manager.aerospike_manager.db_tracker:
        db_manager.aerospike_manager.db_tracker.enabled = True
    if hasattr(db_manager, 'mongo_manager') and db_manager.mongo_manager.db_tracker:
        db_manager.mongo_manager.db_tracker.enabled = True
    return response

def setup_application():
    """Initialize all components of the application"""
    
    # Initialize models
    models = init_models(db)
    
    # Initialize utils
    utils = init_utils(app, db, models, db_manager)
    
    # Initialize API resources
    api_resources = init_api_resources(db, models, db_manager, utils)
    
    # Register API endpoints
    api.add_resource(api_resources['UserResource'], '/api/user')
    api.add_resource(api_resources['CategoriesResource'], '/api/categories')
    api.add_resource(api_resources['ProductsResource'], '/api/products')
    api.add_resource(api_resources['ProductResource'], '/api/products/<int:product_id>')
    api.add_resource(api_resources['OrdersResource'], '/api/orders')
    api.add_resource(api_resources['CartResource'], '/api/cart')
    api.add_resource(api_resources['CartItemResource'], '/api/cart/<int:item_id>')
    api.add_resource(api_resources['DebugResource'], '/api/debug')
    api.add_resource(api_resources['DbLogsResource'], '/api/db-logs')
    api.add_resource(api_resources['ApiLogsResource'], '/api/api-logs')
    api.add_resource(api_resources['DatabaseSwitchResource'], '/api/database-switch')
    api.add_resource(api_resources['LoadTestResource'], '/api/load-test')
    api.add_resource(api_resources['LoadTestResultsResource'], '/api/load-test/results/<string:test_id>')
    api.add_resource(api_resources['LoadTestStatusResource'], '/api/load-test/status', '/api/load-test/status/<string:test_id>')
    api.add_resource(api_resources['LoadTestControlResource'], '/api/load-test/<string:action>')
    api.add_resource(api_resources['LoadTestExportResource'], '/api/load-test/export/<string:test_id>')
    
    # Initialize database functions
    db_functions = init_database_functions(app, db, models, db_manager, utils['db_tracker'])
    
    return models, utils, api_resources, db_functions

if __name__ == '__main__':
    models, utils, api_resources, db_functions = setup_application()
    
    # Initialize database within Flask application context
    with app.app_context():
        db_functions['initialize_database']()
    
    print("🚀 Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5001) 