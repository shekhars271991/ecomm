import time
import functools
from flask import request


def create_time_api_call_decorator(db_tracker, db_manager):
    """Factory function to create time_api_call decorator with initialized dependencies"""
    
    def time_api_call(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Get request info
            endpoint = request.path  # Use the actual path instead of endpoint name
            method = request.method
            session_id = request.args.get('session_id')
            
            # Only try to get session_id from JSON for POST/PUT requests
            if method in ['POST', 'PUT'] and request.content_type == 'application/json':
                try:
                    json_data = request.get_json(silent=True)
                    if json_data and 'session_id' in json_data:
                        session_id = json_data['session_id']
                except:
                    pass
            
            try:
                # Execute the original function
                result = f(*args, **kwargs)
                
                # Determine status code
                if isinstance(result, tuple):
                    status_code = result[1] if len(result) > 1 else 200
                else:
                    status_code = 200
                    
            except Exception as e:
                end_time = time.time()
                # Log failed API call
                db_tracker.log_api_call(
                    endpoint=endpoint,
                    method=method,
                    status_code=500,
                    start_time=start_time,
                    end_time=end_time,
                    session_id=session_id,
                    database_type=db_manager.get_current_database()
                )
                raise  # Re-raise the exception
            
            end_time = time.time()
            
            # Log successful API call
            db_tracker.log_api_call(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                start_time=start_time,
                end_time=end_time,
                session_id=session_id,
                database_type=db_manager.get_current_database()
            )
            
            return result
        
        return decorated_function
    
    return time_api_call


def create_track_db_operation(db_tracker):
    """Factory function to create track_db_operation with initialized dependencies"""
    
    def track_db_operation(operation_type, operation_func, *args, **kwargs):
        if not db_tracker.enabled:
            return operation_func(*args, **kwargs)
        
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        
        # Extract query information
        query_info = "Database operation"
        result_count = None
        
        if hasattr(result, 'count'):
            try:
                result_count = result.count()
            except:
                pass
        elif isinstance(result, list):
            result_count = len(result)
        
        db_tracker.log_query(operation_type, query_info, start_time, end_time, result_count, database_type='mysql')
        return result
    
    return track_db_operation


def create_api_response_helper(db_tracker):
    """Factory function to create create_api_response helper with initialized dependencies"""
    
    def create_api_response(data, success=True, message="Success"):
        response = {
            'success': success,
            'message': message,
            'data': data
        }
        
        if db_tracker.enabled:
            response['debug'] = {
                'recent_queries': db_tracker.get_recent_queries(),
                'demo_mode': True
            }
        
        return response
    
    return create_api_response


def safe_get_json():
    """Safely get JSON data from request, handling content type issues"""
    try:
        # Try to get JSON data directly
        return request.get_json(force=True)
    except Exception as e:
        # If that fails, return None
        return None 