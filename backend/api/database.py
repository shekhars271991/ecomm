from flask import request
from flask_restful import Resource


def create_database_resource(db_manager, time_api_call, create_api_response):
    """Factory function to create DatabaseSwitchResource with initialized dependencies"""
    
    class DatabaseSwitchResource(Resource):
        @time_api_call
        def get(self):
            """Get current database type"""
            current_db = db_manager.get_current_database()
            return create_api_response({
                'current_database': current_db,
                'available_databases': ['mysql', 'aerospike']
            })
        
        @time_api_call
        def post(self):
            """Switch database type"""
            data = request.get_json()
            
            if not data or 'database' not in data:
                return create_api_response(None, False, "Database type is required"), 400
            
            db_type = data['database']
            
            if db_type not in ['mysql', 'aerospike']:
                return create_api_response(None, False, "Invalid database type. Must be 'mysql' or 'aerospike'"), 400
            
            try:
                db_manager.set_database(db_type)
                
                # Note: Sample data initialization removed to preserve CSV data
                # Sample data can be manually initialized if needed
                
                return create_api_response({
                    'current_database': db_type,
                    'message': f'Successfully switched to {db_type} database'
                }, True, f"Database switched to {db_type}")
            except Exception as e:
                return create_api_response(None, False, f"Failed to switch database: {str(e)}"), 500
    
    return DatabaseSwitchResource 