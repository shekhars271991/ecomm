from .init import create_database_init_functions

def init_database_functions(app, db, models, db_manager, db_tracker):
    """Initialize database initialization functions with dependencies"""
    
    functions = create_database_init_functions(app, db, models, db_manager, db_tracker)
    
    return functions
