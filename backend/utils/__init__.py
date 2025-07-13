from .database_tracker import create_database_tracker
from .helpers import (
    create_time_api_call_decorator,
    create_track_db_operation,
    create_api_response_helper,
    safe_get_json
)

def init_utils(app, db, models, db_manager):
    """Initialize all utility functions and classes with dependencies"""
    
    # Create database tracker
    db_tracker = create_database_tracker(app, db, models)
    
    # Create helper functions
    time_api_call = create_time_api_call_decorator(db_tracker, db_manager)
    track_db_operation = create_track_db_operation(db_tracker)
    create_api_response = create_api_response_helper(db_tracker)
    
    return {
        'db_tracker': db_tracker,
        'time_api_call': time_api_call,
        'track_db_operation': track_db_operation,
        'create_api_response': create_api_response,
        'safe_get_json': safe_get_json
    }
