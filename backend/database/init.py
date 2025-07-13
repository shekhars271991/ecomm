import time
import os
import sys


def create_database_init_functions(app, db, models, db_manager, db_tracker):
    """Factory function to create database initialization functions with initialized dependencies"""
    
    Category = models['Category']
    Product = models['Product']
    Cart = models['Cart']
    
    def initialize_database(force_refresh=False, dataloader_type='file'):
        """Initialize database with optional force refresh and dataloader type"""
        try:
            # Try to create tables
            db.create_all()
            print("✅ Database tables created/verified successfully")
            
            # Add database_type column to db_logs table if it doesn't exist
            try:
                # Check if column exists by trying to query it
                db.session.execute(db.text("SELECT database_type FROM db_logs LIMIT 1"))
            except Exception:
                # Column doesn't exist, add it
                try:
                    db.session.execute(db.text("ALTER TABLE db_logs ADD COLUMN database_type VARCHAR(50) NOT NULL DEFAULT 'mysql'"))
                    db.session.commit()
                    print("✅ Added database_type column to db_logs table")
                except Exception as e:
                    db.session.rollback()
                    print(f"⚠️  Failed to add database_type column: {e}")
            
            # Check if api_logs table exists, if not it will be created by db.create_all()
            try:
                db.session.execute(db.text("SELECT COUNT(*) FROM api_logs"))
                print("✅ API logs table exists")
            except Exception:
                print("ℹ️  API logs table will be created")
            
            # Initialize database manager
            models_dict = {
                'Category': Category,
                'Product': Product,
                'Cart': Cart
            }
            db_manager.initialize(app, db, db_tracker, models_dict)
            
            # Clear cart table on startup
            clear_cart_on_startup()
            
            # Check if we need to load data
            should_load_data = force_refresh or should_load_initial_data()
            
            if should_load_data:
                if dataloader_type == 'default':
                    # Load sample data for Aerospike
                    if db_manager.aerospike_manager.is_available():
                        db_manager.aerospike_manager.init_sample_data()
                        print("✅ Sample data loaded successfully!")
                    else:
                        print("⚠️  Aerospike not available for sample data")
                else:
                    # Load CSV data (default behavior)
                    load_initial_data(force_refresh)
            else:
                print(f"✅ Database already contains {Category.query.count()} categories and {Product.query.count()} products - skipping data load")
                
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("⚠️  This might be due to:")
            print("   - MySQL container not running (run: docker-compose up -d)")
            print("   - Database credentials incorrect")
            print("   - Network connection issues")
            return False

    def clear_cart_on_startup():
        """Clear cart table on startup"""
        try:
            start_time = time.time()
            cart_items = Cart.query.all()
            item_count = len(cart_items)
            
            for item in cart_items:
                db.session.delete(item)
            
            db.session.commit()
            end_time = time.time()
            
            if item_count > 0:
                db_tracker.log_query('DELETE', f"DELETE FROM cart (cleared {item_count} items on startup)", start_time, end_time, item_count, database_type='mysql')
                print(f"✅ Cleared {item_count} cart items on startup")
            
        except Exception as e:
            print(f"⚠️  Failed to clear cart on startup: {e}")
            if db:
                db.session.rollback()

    def should_load_initial_data():
        """Check if we should load initial data"""
        try:
            category_count = Category.query.count()
            product_count = Product.query.count()
            
            # Load data if either table is empty
            if category_count == 0 or product_count == 0:
                print(f"📊 Database check: {category_count} categories, {product_count} products")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  Failed to check database state: {e}")
            return True  # Default to loading if we can't check

    def load_initial_data(force_refresh=False):
        """Load initial data from CSV"""
        try:
            if force_refresh:
                print("🔄 Force refresh requested - loading fresh data...")
            else:
                print("📦 Database is empty, loading data from CSV file...")
            
            from csv_data_loader import CSVDataLoader
            
            # Get the individual managers from the unified manager
            mysql_manager = db_manager.mysql_manager
            aerospike_manager = db_manager.aerospike_manager
            mongo_manager = db_manager.mongo_manager
            
            # Create CSV loader with all three managers
            csv_loader = CSVDataLoader(mysql_manager, aerospike_manager, mongo_manager)
            
            # Load data from CSV
            csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'GroceryDataset.csv')
            
            if not os.path.exists(csv_file_path):
                print(f"❌ CSV file not found: {csv_file_path}")
                return False
            
            # Skip truncation if not force refresh and data already exists
            skip_truncate = not force_refresh and not should_load_initial_data()
            
            csv_loader.load_all_data(csv_file_path, skip_truncate=skip_truncate)
            
            print("✅ Data loaded successfully from CSV file!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data from CSV: {e}")
            print("⚠️  CSV data loading failed - check that CSV file exists and is readable")
            return False

    def main(force_refresh=False, dataloader_type='file'):
        """Main application entry point"""
        if force_refresh:
            if dataloader_type == 'default':
                print("🔄 Force refresh mode enabled with sample data")
            else:
                print("🔄 Force refresh mode enabled with CSV data")
        else:
            if dataloader_type == 'default':
                print("🚀 Starting with sample data")
            else:
                print("🚀 Starting with CSV data")
        
        with app.app_context():
            # Initialize database
            if not initialize_database(force_refresh, dataloader_type):
                print("❌ Failed to initialize database. Application cannot start.")
                sys.exit(1)
            
            print("✅ Database initialization complete")
        
        print("🚀 Starting Flask application...")
        return app

    return {
        'initialize_database': initialize_database,
        'clear_cart_on_startup': clear_cart_on_startup,
        'should_load_initial_data': should_load_initial_data,
        'load_initial_data': load_initial_data,
        'main': main
    } 