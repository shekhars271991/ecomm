from typing import Dict, List, Optional, Any
from mysql_manager import MySQLManager
from aerospike_manager import AerospikeManager


class UnifiedDatabaseManager:
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.current_db = 'mysql'  # Default to MySQL
        self.mysql_manager = MySQLManager(app, db)
        self.aerospike_manager = AerospikeManager(app)
        
    def initialize(self, app, db, db_tracker, models=None):
        """Initialize both database managers"""
        self.app = app
        self.db = db
        
        # Initialize both managers
        self.mysql_manager.initialize(app, db, db_tracker, models)
        self.aerospike_manager.initialize(app, db_tracker)
        
        # Initialize Aerospike data if needed
        if self.aerospike_manager.is_available():
            self.aerospike_manager.init_sample_data()
        
        print("Unified Database Manager initialized successfully")
    
    def set_database(self, db_type: str):
        """Switch between MySQL and Aerospike"""
        if db_type in ['mysql', 'aerospike']:
            self.current_db = db_type
            print(f"Switched to {db_type} database")
        else:
            raise ValueError("Database type must be 'mysql' or 'aerospike'")
    
    def get_current_database(self):
        """Get current database type"""
        return self.current_db
    
    def get_current_manager(self):
        """Get the current active database manager"""
        if self.current_db == 'mysql':
            return self.mysql_manager
        else:
            return self.aerospike_manager
    
    # Category operations
    def get_all_categories(self) -> List[Dict]:
        """Get all categories from current database"""
        return self.get_current_manager().get_all_categories()
    
    # Product operations
    def get_all_products(self, category_id: Optional[int] = None, search_term: Optional[str] = None) -> List[Dict]:
        """Get products from current database"""
        return self.get_current_manager().get_all_products(category_id, search_term)
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific product by ID from current database"""
        return self.get_current_manager().get_product_by_id(product_id)
    
    # Cart operations
    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get cart items from current database"""
        return self.get_current_manager().get_cart_items(session_id)
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart in current database"""
        return self.get_current_manager().add_to_cart(session_id, product_id, quantity)
    
    def clear_cart(self, session_id: str) -> Dict:
        """Clear cart in current database"""
        return self.get_current_manager().clear_cart(session_id)
    
    # Utility methods
    def is_available(self) -> bool:
        """Check if current database is available"""
        return self.get_current_manager().is_available()
    
    def close(self):
        """Close database connections"""
        if hasattr(self.aerospike_manager, 'close'):
            self.aerospike_manager.close()
        print("Database connections closed")
    
    # Legacy compatibility methods (for backward compatibility)
    def log_query(self, operation_type: str, query_description: str, start_time: float, end_time: float, result_count: int = 0):
        """Log database operations - delegates to current manager"""
        return self.get_current_manager().log_query(operation_type, query_description, start_time, end_time, result_count)
    
    def init_sample_data(self):
        """Initialize sample data in Aerospike"""
        if self.aerospike_manager.is_available():
            self.aerospike_manager.init_sample_data() 