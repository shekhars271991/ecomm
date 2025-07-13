from flask import request
from flask_restful import Resource


def create_debug_resources(db, models, db_tracker, create_api_response):
    """Factory function to create debug-related resources with initialized dependencies"""
    
    DbLog = models['DbLog']
    ApiLog = models['ApiLog']
    
    class DebugResource(Resource):
        def get(self):
            if not db_tracker.enabled:
                return create_api_response(None, False, "Demo mode is not enabled"), 404
            
            recent_queries = db_tracker.get_recent_queries()
            return create_api_response({
                'all_queries': recent_queries,
                'recent_queries': recent_queries,
                'demo_mode': True
            })
        
        def delete(self):
            if not db_tracker.enabled:
                return create_api_response(None, False, "Demo mode is not enabled"), 404
            
            db_tracker.clear_queries()
            return create_api_response(None, True, "Query history cleared")

    class DbLogsResource(Resource):
        def get(self):
            try:
                # Get database type filter from query parameters
                database_type = request.args.get('database_type')
                
                # Start with base query
                query = DbLog.query
                
                # Apply database type filter if provided
                if database_type and database_type in ['mysql', 'aerospike', 'mongodb']:
                    query = query.filter_by(database_type=database_type)
                
                # Get logs ordered by timestamp desc
                logs = query.order_by(DbLog.timestamp.desc()).all()
                logs_data = [log.to_dict() for log in logs]
                
                return create_api_response({
                    'logs': logs_data,
                    'count': len(logs_data),
                    'database_type_filter': database_type
                })
            except Exception as e:
                return create_api_response(None, False, f"Failed to get logs: {str(e)}"), 500
        
        def delete(self):
            try:
                # Get database type filter from query parameters
                database_type = request.args.get('database_type')
                
                # Start with base query
                query = DbLog.query
                
                # Apply database type filter if provided
                if database_type and database_type in ['mysql', 'aerospike', 'mongodb']:
                    query = query.filter_by(database_type=database_type)
                
                # Delete filtered logs
                deleted_count = query.delete()
                db.session.commit()
                
                filter_msg = f" for {database_type} database" if database_type else ""
                return create_api_response(
                    {'deleted_count': deleted_count}, 
                    True, 
                    f"Logs cleared{filter_msg}"
                )
            except Exception as e:
                db.session.rollback()
                return create_api_response(None, False, f"Failed to clear logs: {str(e)}"), 500

    class ApiLogsResource(Resource):
        def get(self):
            try:
                # Get database type filter from query parameters
                database_type = request.args.get('database_type')
                
                # Start with base query
                query = ApiLog.query
                
                # Apply database type filter if provided
                if database_type and database_type in ['mysql', 'aerospike', 'mongodb']:
                    query = query.filter_by(database_type=database_type)
                
                # Get logs ordered by timestamp desc
                logs = query.order_by(ApiLog.timestamp.desc()).all()
                logs_data = [log.to_dict() for log in logs]
                
                return create_api_response({
                    'logs': logs_data,
                    'count': len(logs_data),
                    'database_type_filter': database_type
                })
            except Exception as e:
                return create_api_response(None, False, f"Failed to get API logs: {str(e)}"), 500
        
        def delete(self):
            try:
                # Get database type filter from query parameters
                database_type = request.args.get('database_type')
                
                # Start with base query
                query = ApiLog.query
                
                # Apply database type filter if provided
                if database_type and database_type in ['mysql', 'aerospike', 'mongodb']:
                    query = query.filter_by(database_type=database_type)
                
                # Delete filtered logs
                deleted_count = query.delete()
                db.session.commit()
                
                filter_msg = f" for {database_type} database" if database_type else ""
                return create_api_response(
                    {'deleted_count': deleted_count}, 
                    True, 
                    f"API logs cleared{filter_msg}"
                )
            except Exception as e:
                db.session.rollback()
                return create_api_response(None, False, f"Failed to clear API logs: {str(e)}"), 500
    
    return DebugResource, DbLogsResource, ApiLogsResource 