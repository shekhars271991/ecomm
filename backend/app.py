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
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True)

# Initialize database manager
db_manager = UnifiedDatabaseManager()

# Add request hook to ensure proper content type handling
@app.before_request
def before_request():
    # For OPTIONS requests, return immediately
    if request.method == 'OPTIONS':
        return
    
    # For POST/PUT requests, ensure content type is set
    if request.method in ['POST', 'PUT'] and request.content_type is None:
        # If no content type is set but we have data, assume JSON
        if request.data:
            request.content_type = 'application/json'

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
    
    # Initialize database functions
    db_functions = init_database_functions(app, db, models, db_manager, utils['db_tracker'])
    
    return models, utils, api_resources, db_functions

if __name__ == '__main__':
    # Parse command line arguments
    force_refresh = '--refresh' in sys.argv or '-r' in sys.argv
    
    # Check for dataloader type parameter
    dataloader_type = 'file'  # Default to CSV file
    if '--dataloader' in sys.argv:
        try:
            dataloader_index = sys.argv.index('--dataloader')
            if dataloader_index + 1 < len(sys.argv):
                dataloader_type = sys.argv[dataloader_index + 1]
        except (IndexError, ValueError):
            dataloader_type = 'file'
    
    # Setup application
    models, utils, api_resources, db_functions = setup_application()
    
    # Initialize and run the application
    app = db_functions['main'](force_refresh, dataloader_type)
    app.run(debug=True, host='0.0.0.0', port=5001) 