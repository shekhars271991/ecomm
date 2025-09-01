from typing import Dict, List, Optional, Any
from mysql_manager import MySQLManager
from aerospike_manager import AerospikeManager
from mongo_manager import MongoManager


class UnifiedDatabaseManager:
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.current_db = 'mysql'  # Default to MySQL
        self.mysql_manager = MySQLManager(app, db)
        self.aerospike_manager = AerospikeManager(app)
        self.mongo_manager = MongoManager(app)
        
    def initialize(self, app, db, db_tracker, models=None):
        """Initialize all database managers"""
        self.app = app
        self.db = db
        
        # Initialize all managers
        self.mysql_manager.initialize(app, db, db_tracker, models)
        self.aerospike_manager.initialize(app, db_tracker)
        self.mongo_manager.initialize(app, db_tracker)
        
        # Note: Sample data initialization removed to prevent overriding CSV data
        # Sample data will only be initialized when explicitly switching to databases
        
        print("Unified Database Manager initialized successfully")
    
    def set_database(self, db_type: str):
        """Switch between MySQL, Aerospike, and MongoDB"""
        if db_type in ['mysql', 'aerospike', 'mongodb']:
            self.current_db = db_type
            print(f"Switched to {db_type} database")
        else:
            raise ValueError("Database type must be 'mysql', 'aerospike', or 'mongodb'")
    
    def get_current_database(self):
        """Get current database type"""
        return self.current_db
    
    def get_current_manager(self):
        """Get the current active database manager"""
        if self.current_db == 'mysql':
            return self.mysql_manager
        elif self.current_db == 'aerospike':
            return self.aerospike_manager
        else:  # mongodb
            return self.mongo_manager
    
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
        """Get cart items for a session from current database"""
        return self.get_current_manager().get_cart_items(session_id)
    
    def add_to_cart(self, session_id: str, product_id: int, quantity: int = 1) -> Dict:
        """Add item to cart in current database"""
        return self.get_current_manager().add_to_cart(session_id, product_id, quantity)
    
    def clear_cart(self, session_id: str) -> Dict:
        """Clear cart for a session in current database"""
        return self.get_current_manager().clear_cart(session_id)
    
    # Utility methods
    def is_available(self) -> bool:
        """Check if current database is available"""
        return self.get_current_manager().is_available()
    
    def close(self):
        """Close connections to all databases"""
        if hasattr(self.mysql_manager, 'close'):
            self.mysql_manager.close()
        if hasattr(self.aerospike_manager, 'close'):
            self.aerospike_manager.close()
        if hasattr(self.mongo_manager, 'close'):
            self.mongo_manager.close()
    
    def init_sample_data(self):
        """Initialize sample data in current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'init_sample_data'):
            manager.init_sample_data()
        else:
            print(f"Sample data initialization not supported for {self.current_db}")
    
    # Filter operations - delegate to current database manager
    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """Get products within a specific price range from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_by_price_range'):
            return manager.get_products_by_price_range(min_price, max_price)
        else:
            print(f"Price range filtering not supported for {self.current_db}")
            return []
    
    def get_products_by_rating(self, min_rating: float) -> List[Dict]:
        """Get products with minimum rating from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_by_rating'):
            return manager.get_products_by_rating(min_rating)
        else:
            print(f"Rating filtering not supported for {self.current_db}")
            return []
    
    def get_products_by_discount_status(self, has_discount: bool = True) -> List[Dict]:
        """Get products by discount status from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_by_discount_status'):
            return manager.get_products_by_discount_status(has_discount)
        else:
            print(f"Discount status filtering not supported for {self.current_db}")
            return []
    
    def get_products_by_feature(self, feature_keyword: str) -> List[Dict]:
        """Get products containing specific features from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_by_feature'):
            return manager.get_products_by_feature(feature_keyword)
        else:
            print(f"Feature filtering not supported for {self.current_db}")
            return []
    
    def get_products_by_stock_level(self, min_stock: int = 0) -> List[Dict]:
        """Get products with minimum stock level from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_by_stock_level'):
            return manager.get_products_by_stock_level(min_stock)
        else:
            print(f"Stock level filtering not supported for {self.current_db}")
            return []
    
    def get_products_by_availability(self, is_available: bool = True) -> List[Dict]:
        """Get products by availability status from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_by_availability'):
            return manager.get_products_by_availability(is_available)
        else:
            print(f"Availability filtering not supported for {self.current_db}")
            return []
    
    def get_products_advanced_filter(self, 
                                    min_price: Optional[float] = None,
                                    max_price: Optional[float] = None,
                                    min_rating: Optional[float] = None,
                                    category_id: Optional[int] = None,
                                    has_discount: Optional[bool] = None,
                                    feature_keyword: Optional[str] = None,
                                    min_stock: Optional[int] = None,
                                    is_available: Optional[bool] = None,
                                    search_term: Optional[str] = None) -> List[Dict]:
        """Advanced product filtering with multiple criteria from current database"""
        manager = self.get_current_manager()
        if hasattr(manager, 'get_products_advanced_filter'):
            return manager.get_products_advanced_filter(
                min_price=min_price,
                max_price=max_price,
                min_rating=min_rating,
                category_id=category_id,
                has_discount=has_discount,
                feature_keyword=feature_keyword,
                min_stock=min_stock,
                is_available=is_available,
                search_term=search_term
            )
        else:
            print(f"Advanced filtering not supported for {self.current_db}")
            return []
    
    def log_query(self, operation_type: str, query_description: str, start_time: float, end_time: float, result_count: int = 0):
        """Legacy method - now delegated to individual managers"""
        self.get_current_manager().log_query(operation_type, query_description, start_time, end_time, result_count) 