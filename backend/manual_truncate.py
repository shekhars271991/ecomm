#!/usr/bin/env python3
"""
Manual Database Truncation Script
Run this to manually clear all data from MySQL database.
"""

import pymysql
import sys

def truncate_mysql_database():
    """Manually truncate MySQL database"""
    try:
        # Connect to MySQL
        connection = pymysql.connect(
            host='localhost',
            user='grocery_user',
            password='grocery_password',
            database='grocery_db',
            charset='utf8mb4'
        )
        
        print("Connected to MySQL database")
        
        with connection.cursor() as cursor:
            print("Executing truncation commands...")
            
            # Disable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Clear all data in the right order
            tables_to_clear = [
                'db_logs',
                'order_items', 
                'orders',
                'cart',
                'products',
                'categories'
            ]
            
            for table in tables_to_clear:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    print(f"✅ Cleared {table}")
                except Exception as e:
                    print(f"⚠️  Warning clearing {table}: {e}")
            
            # Reset auto-increment counters
            for table in tables_to_clear:
                try:
                    cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                    print(f"✅ Reset {table} auto-increment")
                except Exception as e:
                    print(f"⚠️  Warning resetting {table}: {e}")
            
            # Re-enable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            # Commit changes
            connection.commit()
            
            print("🎉 Database truncation completed successfully!")
            
            # Check that tables are empty
            print("\nVerifying truncation:")
            for table in ['categories', 'products', 'orders', 'cart']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  {table}: {count} rows")
                except Exception as e:
                    print(f"  {table}: Error checking - {e}")
                    
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure MySQL container is running and credentials are correct")
        sys.exit(1)
        
    finally:
        if 'connection' in locals():
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    print("🗑️  Manual Database Truncation")
    print("=" * 40)
    
    response = input("Are you sure you want to delete ALL data from the database? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        truncate_mysql_database()
    else:
        print("Truncation cancelled") 