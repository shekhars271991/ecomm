import csv
import os
import re
import time
from typing import Dict, List, Tuple, Optional
from mysql_manager import MySQLManager
from aerospike_manager import AerospikeManager
from mongo_manager import MongoManager

class CSVDataLoader:
    def __init__(self, mysql_manager: Optional[MySQLManager], aerospike_manager: Optional[AerospikeManager], mongo_manager: Optional[MongoManager] = None):
        self.mysql_manager = mysql_manager
        self.aerospike_manager = aerospike_manager
        self.mongo_manager = mongo_manager
        
    def parse_price(self, price_str: str) -> float:
        """Extract numeric price from price string like '$56.99' or '$99.99'"""
        if not price_str or price_str.strip() == '':
            return 0.0
        
        # Remove currency symbols and whitespace
        price_clean = re.sub(r'[^\d.]', '', price_str.strip())
        
        try:
            return float(price_clean)
        except ValueError:
            return 0.0
    
    def parse_rating(self, rating_str: str) -> Tuple[float, int]:
        """Extract rating value and review count from rating string"""
        if not rating_str or 'No Reviews' in rating_str:
            return 0.0, 0
        
        # Extract rating value (e.g., "4.3" from "Rated 4.3 out of 5 stars")
        rating_match = re.search(r'Rated\s+(\d+\.?\d*)', rating_str)
        rating = float(rating_match.group(1)) if rating_match else 0.0
        
        # Extract review count (e.g., "265" from "based on 265 reviews")
        review_match = re.search(r'based on (\d+) reviews', rating_str)
        review_count = int(review_match.group(1)) if review_match else 0
        
        return rating, review_count
    
    def get_category_icon(self, category_name: str) -> str:
        """Get appropriate FontAwesome icon for a category"""
        category_icons = {
            'bakery & desserts': 'fas fa-birthday-cake',
            'beverages & water': 'fas fa-tint',
            'breakfast': 'fas fa-coffee',
            'candy': 'fas fa-candy-cane',
            'cleaning supplies': 'fas fa-spray-can',
            'coffee': 'fas fa-coffee',
            'deli': 'fas fa-cheese',
            'floral': 'fas fa-flower',
            'gift baskets': 'fas fa-gift',
            'household': 'fas fa-home',
            'kirkland signature grocery': 'fas fa-star',
            'laundry detergent & supplies': 'fas fa-tshirt',
            'meat & seafood': 'fas fa-drumstick-bite',
            'organic': 'fas fa-leaf',
            'pantry & dry goods': 'fas fa-box',
            'paper & plastic products': 'fas fa-toilet-paper',
            'poultry': 'fas fa-feather-alt',
            'seafood': 'fas fa-fish',
            'snacks': 'fas fa-cookie-bite',
            'fruits & vegetables': 'fas fa-carrot',
            'dairy & eggs': 'fas fa-glass-whiskey',
            'frozen': 'fas fa-snowflake',
            'health & beauty': 'fas fa-heart',
            'pharmacy': 'fas fa-pills'
        }
        
        # Convert to lowercase for matching
        category_lower = category_name.lower().strip()
        
        # Return specific icon if found, otherwise return a generic grocery icon
        return category_icons.get(category_lower, 'fas fa-shopping-basket')
    
    def get_category_image_url(self, category_name: str) -> str:
        """Get generic product image URL for a category"""
        category_images = {
            'bakery & desserts': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&h=300&fit=crop&crop=center',
            'beverages & water': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop&crop=center',
            'breakfast': 'https://images.unsplash.com/photo-1525351484163-7529414344d8?w=400&h=300&fit=crop&crop=center',
            'candy': 'https://images.unsplash.com/photo-1519869325930-281384150729?w=400&h=300&fit=crop&crop=center',
            'cleaning supplies': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop&crop=center',
            'coffee': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&h=300&fit=crop&crop=center',
            'deli': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop&crop=center',
            'floral': 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400&h=300&fit=crop&crop=center',
            'gift baskets': 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400&h=300&fit=crop&crop=center',
            'household': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop&crop=center',
            'kirkland signature grocery': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop&crop=center',
            'laundry detergent & supplies': 'https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=400&h=300&fit=crop&crop=center',
            'meat & seafood': 'https://images.unsplash.com/photo-1448907503123-67254d59ca4f?w=400&h=300&fit=crop&crop=center',
            'organic': 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&h=300&fit=crop&crop=center',
            'pantry & dry goods': 'https://images.unsplash.com/photo-1549921296-3b0eb8ddc50a?w=400&h=300&fit=crop&crop=center',
            'paper & plastic products': 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=400&h=300&fit=crop&crop=center',
            'poultry': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=400&h=300&fit=crop&crop=center',
            'seafood': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400&h=300&fit=crop&crop=center',
            'snacks': 'https://images.unsplash.com/photo-1621447504864-d8686e12698c?w=400&h=300&fit=crop&crop=center',
            'fruits & vegetables': 'https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=400&h=300&fit=crop&crop=center',
            'dairy & eggs': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=300&fit=crop&crop=center'
        }
        
        category_lower = category_name.lower().strip()
        return category_images.get(category_lower, 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=300&fit=crop&crop=center')

    def get_category_mapping(self, products: List[Dict]) -> Dict[str, int]:
        """Get unique categories and assign IDs (starting from 1)"""
        unique_categories = set()
        for product in products:
            unique_categories.add(product['category'])
        
        category_mapping = {}
        for i, category in enumerate(sorted(unique_categories), 1):
            category_mapping[category] = i
        
        return category_mapping
    
    def load_csv_data(self, csv_file_path: str) -> List[Dict]:
        """Load and parse CSV data"""
        products = []
        
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        print(f"Loading data from {csv_file_path}...")
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Parse price
                price = self.parse_price(row.get('Price', ''))
                
                # Parse rating and review count
                rating, review_count = self.parse_rating(row.get('Rating', ''))
                
                # Create product dict
                product = {
                    'title': row.get('Title', '').strip(),
                    'category': row.get('Sub Category', '').strip(),
                    'price': price,
                    'rating': rating,
                    'review_count': review_count,
                    'discount': row.get('Discount', '').strip(),
                    'features': row.get('Feature', '').strip(),
                    'description': row.get('Product Description', '').strip()
                }
                
                # Skip products with missing essential data
                if product['title'] and product['category'] and product['price'] > 0:
                    products.append(product)
        
        print(f"Loaded {len(products)} valid products from CSV")
        return products
    
    def truncate_mysql_data(self):
        """Truncate MySQL data using existing models"""
        print("Truncating MySQL data...")
        start_time = time.time()
        
        if not self.mysql_manager or not self.mysql_manager.db:
            print("MySQL manager or db not available")
            return
        
        try:
            # Use raw SQL to handle foreign key constraints properly
            db = self.mysql_manager.db
            
            # Disable foreign key checks temporarily
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # Clear all tables in the right order
            db.session.execute(db.text("DELETE FROM order_items"))  # Clear dependent table first
            db.session.execute(db.text("DELETE FROM orders"))      # Clear orders
            db.session.execute(db.text("DELETE FROM cart"))        # Clear cart
            db.session.execute(db.text("DELETE FROM products"))    # Clear products
            db.session.execute(db.text("DELETE FROM categories"))  # Clear categories
            
            # Reset auto-increment counters
            db.session.execute(db.text("ALTER TABLE order_items AUTO_INCREMENT = 1"))
            db.session.execute(db.text("ALTER TABLE orders AUTO_INCREMENT = 1"))
            db.session.execute(db.text("ALTER TABLE cart AUTO_INCREMENT = 1"))
            db.session.execute(db.text("ALTER TABLE products AUTO_INCREMENT = 1"))
            db.session.execute(db.text("ALTER TABLE categories AUTO_INCREMENT = 1"))
            
            # Re-enable foreign key checks
            db.session.execute(db.text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # Commit all changes
            db.session.commit()
            
            end_time = time.time()
            truncate_time = end_time - start_time
            print(f"MySQL data truncated successfully in {truncate_time:.3f} seconds")
            
        except Exception as e:
            end_time = time.time()
            truncate_time = end_time - start_time
            print(f"Error truncating MySQL data after {truncate_time:.3f} seconds: {e}")
            if self.mysql_manager.db:
                # Re-enable foreign key checks even if there's an error
                try:
                    self.mysql_manager.db.session.execute(self.mysql_manager.db.text("SET FOREIGN_KEY_CHECKS = 1"))
                except:
                    pass
                self.mysql_manager.db.session.rollback()
    
    def truncate_aerospike_data(self):
        """Truncate Aerospike data using ASDM truncate commands"""
        print("Truncating Aerospike data...")
        start_time = time.time()
        
        if not self.aerospike_manager or not self.aerospike_manager.aerospike_client:
            print("Aerospike client not available")
            return
        
        try:
            # Truncate old categories set (for cleanup)
            info_string = 'truncate:namespace=grocery;set=categories'
            self.aerospike_manager.aerospike_client.info_all(info_string)
            print("Old categories set truncated")
            
            # Truncate meta set (contains all_categories)
            info_string = 'truncate:namespace=grocery;set=meta'
            self.aerospike_manager.aerospike_client.info_all(info_string)
            print("Meta set truncated")
            
            # Truncate products set
            info_string = 'truncate:namespace=grocery;set=products'
            self.aerospike_manager.aerospike_client.info_all(info_string)
            print("Products set truncated")
            
            # Truncate cart set
            info_string = 'truncate:namespace=grocery;set=cart'
            self.aerospike_manager.aerospike_client.info_all(info_string)
            print("Cart set truncated")
            
            end_time = time.time()
            truncate_time = end_time - start_time
            print(f"Aerospike data truncated successfully in {truncate_time:.3f} seconds")
            
        except Exception as e:
            end_time = time.time()
            truncate_time = end_time - start_time
            print(f"Error truncating Aerospike data after {truncate_time:.3f} seconds: {e}")
    
    def truncate_mongodb_data(self):
        """Truncate MongoDB data by dropping collections"""
        print("Truncating MongoDB data...")
        start_time = time.time()
        
        if not self.mongo_manager or self.mongo_manager.database is None:
            print("MongoDB not available")
            return
        
        try:
            # Drop all collections
            self.mongo_manager.database.categories.drop()
            print("Categories collection dropped")
            
            self.mongo_manager.database.meta.drop()
            print("Meta collection dropped")
            
            self.mongo_manager.database.products.drop()
            print("Products collection dropped")
            
            self.mongo_manager.database.cart.drop()
            print("Cart collection dropped")
            
            end_time = time.time()
            truncate_time = end_time - start_time
            print(f"MongoDB data truncated successfully in {truncate_time:.3f} seconds")
            
        except Exception as e:
            end_time = time.time()
            truncate_time = end_time - start_time
            print(f"Error truncating MongoDB data after {truncate_time:.3f} seconds: {e}")
    
    def create_mysql_category(self, category_name: str, category_id: int):
        """Create a category in MySQL"""
        if not self.mysql_manager or not self.mysql_manager.Category or not self.mysql_manager.db:
            return
        
        try:
            # Check if category already exists
            existing_category = self.mysql_manager.Category.query.filter_by(name=category_name).first()
            if existing_category:
                return  # Skip if already exists
            
            # Create new category with proper icon
            category = self.mysql_manager.Category(
                name=category_name,
                icon=self.get_category_icon(category_name)
            )
            
            self.mysql_manager.db.session.add(category)
            self.mysql_manager.db.session.commit()
            
        except Exception as e:
            print(f"Error creating MySQL category {category_name}: {e}")
            if self.mysql_manager.db:
                self.mysql_manager.db.session.rollback()
    
    def create_mysql_product(self, product_data: Dict):
        """Create a product in MySQL"""
        if not self.mysql_manager or not self.mysql_manager.Product or not self.mysql_manager.db:
            return
        
        try:
            # Check if product already exists
            existing_product = self.mysql_manager.Product.query.filter_by(name=product_data['name']).first()
            if existing_product:
                return  # Skip if already exists
            
            # Create new product with category-based image
            product = self.mysql_manager.Product(
                name=product_data['name'],
                description=product_data.get('description', ''),
                price=product_data['price'],
                category_id=product_data['category_id'],
                stock=product_data.get('stock_quantity', 100),
                is_available=True,
                image_url=product_data.get('image_url', '')
            )
            
            self.mysql_manager.db.session.add(product)
            self.mysql_manager.db.session.commit()
            
        except Exception as e:
            print(f"Error creating MySQL product {product_data['name']}: {e}")
            if self.mysql_manager.db:
                self.mysql_manager.db.session.rollback()
    
    def create_aerospike_categories(self, category_mapping: Dict[str, int]):
        """Create all categories in Aerospike as a single record"""
        if not self.aerospike_manager or not self.aerospike_manager.aerospike_client:
            return
        
        try:
            key = ('grocery', 'meta', 'all_categories')
            
            # Build categories list
            categories_list = []
            for category_name, category_id in category_mapping.items():
                categories_list.append({
                    'id': category_id,
                    'name': category_name,
                    'icon': self.get_category_icon(category_name)
                })
            
            # Sort by id for consistent ordering
            categories_list.sort(key=lambda x: x['id'])
            
            bins = {
                'categories': categories_list
            }
            
            self.aerospike_manager.aerospike_client.put(key, bins)
            print(f"Stored {len(categories_list)} categories in Aerospike meta record")
            
        except Exception as e:
            print(f"Error creating Aerospike categories: {e}")
    
    def create_aerospike_product(self, product_data: Dict, product_id: int):
        """Create a product in Aerospike"""
        if not self.aerospike_manager or not self.aerospike_manager.aerospike_client:
            return
        
        try:
            key = ('grocery', 'products', str(product_id))
            
            # Check if product already exists
            try:
                existing_key, existing_metadata, existing_record = self.aerospike_manager.aerospike_client.get(key)
                if existing_record:
                    return  # Skip if already exists
            except:
                pass  # Key doesn't exist, proceed to create
            
            bins = {
                'id': product_id,
                'name': product_data['name'],
                'description': product_data.get('description', ''),
                'price': product_data['price'],
                'category_id': product_data['category_id'],
                'stock': product_data.get('stock_quantity', 100),
                'is_available': True,
                'image_url': product_data.get('image_url', '')
            }
            
            self.aerospike_manager.aerospike_client.put(key, bins)
            
        except Exception as e:
            print(f"Error creating Aerospike product {product_data['name']}: {e}")
    
    def create_mongodb_categories(self, category_mapping: Dict[str, int]):
        """Create categories in MongoDB (both individual docs and meta doc)"""
        if not self.mongo_manager or self.mongo_manager.database is None:
            return
        
        try:
            categories_list = []
            for category_name, category_id in category_mapping.items():
                category_doc = {
                    'id': category_id,
                    'name': category_name,
                    'icon': self.get_category_icon(category_name)
                }
                categories_list.append(category_doc)
            
            # Insert individual category documents
            if categories_list:
                # Check if categories already exist (for skip_duplicates mode)
                existing_count = self.mongo_manager.database.categories.count_documents({})
                if existing_count == 0:
                    self.mongo_manager.database.categories.insert_many(categories_list)
                    print(f"Created {len(categories_list)} categories in MongoDB")
                else:
                    print(f"Skipped categories creation - {existing_count} already exist")
            
            # Create meta document with all categories (like Aerospike)
            existing_meta = self.mongo_manager.database.meta.find_one({'_id': 'all_categories'})
            if not existing_meta:
                meta_doc = {
                    '_id': 'all_categories',
                    'categories': categories_list
                }
                self.mongo_manager.database.meta.insert_one(meta_doc)
                print("Created categories meta document in MongoDB")
            else:
                print("Skipped meta document creation - already exists")
                
        except Exception as e:
            print(f"Error creating MongoDB categories: {e}")
    
    def create_mongodb_product(self, product_data: Dict, product_id: int):
        """Create a product in MongoDB"""
        if not self.mongo_manager or self.mongo_manager.database is None:
            return
        
        try:
            # Check if product already exists
            existing_product = self.mongo_manager.database.products.find_one({'id': product_id})
            if existing_product:
                return  # Skip if already exists
            
            product_doc = {
                'id': product_id,
                'name': product_data['name'],
                'description': product_data.get('description', ''),
                'price': product_data['price'],
                'category_id': product_data['category_id'],
                'stock': product_data.get('stock_quantity', 100),
                'is_available': True,
                'image_url': product_data.get('image_url', '')
            }
            
            self.mongo_manager.database.products.insert_one(product_doc)
            
        except Exception as e:
            print(f"Error creating MongoDB product {product_data['name']}: {e}")
    
    def load_data_to_mysql(self, products: List[Dict], category_mapping: Dict[str, int], skip_duplicates: bool = False):
        """Load data into MySQL database"""
        print("Loading data into MySQL...")
        start_time = time.time()
        
        # Insert categories
        categories_inserted = 0
        for category_name, category_id in category_mapping.items():
            if skip_duplicates:
                # Check if category exists before inserting
                if self.mysql_manager and self.mysql_manager.Category:
                    existing = self.mysql_manager.Category.query.filter_by(name=category_name).first()
                    if existing:
                        continue
            
            self.create_mysql_category(category_name, category_id)
            categories_inserted += 1
        
        if skip_duplicates:
            print(f"Inserted {categories_inserted} new categories into MySQL")
        
        # Insert products
        products_inserted = 0
        for i, product in enumerate(products, 1):
            category_id = category_mapping[product['category']]
            
            # Create product with category-based fallback image
            product_data = {
                'name': product['title'],
                'description': product['description'][:500] if product['description'] else '',
                'price': product['price'],
                'category_id': category_id,
                'stock_quantity': 100,
                'rating': product['rating'],
                'review_count': product['review_count'],
                'image_url': self.get_category_image_url(product['category'])
            }
            
            if skip_duplicates:
                # Check if product exists before inserting
                if self.mysql_manager and self.mysql_manager.Product:
                    existing = self.mysql_manager.Product.query.filter_by(name=product_data['name']).first()
                    if existing:
                        continue
            
            self.create_mysql_product(product_data)
            products_inserted += 1
            
            if i % 100 == 0:
                if skip_duplicates:
                    print(f"Processed {i} products, inserted {products_inserted} new products into MySQL...")
                else:
                    print(f"Inserted {i} products into MySQL...")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        if skip_duplicates:
            print(f"Successfully processed {len(products)} products, inserted {products_inserted} new products into MySQL in {load_time:.3f} seconds")
        else:
            print(f"Successfully loaded {len(products)} products into MySQL in {load_time:.3f} seconds")
    
    def load_data_to_aerospike(self, products: List[Dict], category_mapping: Dict[str, int], skip_duplicates: bool = False):
        """Load data into Aerospike database"""
        print("Loading data into Aerospike...")
        start_time = time.time()
        
        # Insert all categories as a single record
        if skip_duplicates:
            # Check if categories already exist
            key = ('grocery', 'meta', 'all_categories')
            try:
                if self.aerospike_manager and self.aerospike_manager.aerospike_client:
                    existing_key, existing_metadata, existing_record = self.aerospike_manager.aerospike_client.get(key)
                    if existing_record:
                        print("Categories already exist in Aerospike - skipping")
                    else:
                        self.create_aerospike_categories(category_mapping)
            except:
                # Key doesn't exist, proceed to create
                self.create_aerospike_categories(category_mapping)
        else:
            self.create_aerospike_categories(category_mapping)
        
        # Insert products
        products_inserted = 0
        for i, product in enumerate(products, 1):
            category_id = category_mapping[product['category']]
            
            # Create product with category-based fallback image
            product_data = {
                'name': product['title'],
                'description': product['description'][:500] if product['description'] else '',
                'price': product['price'],
                'category_id': category_id,
                'stock_quantity': 100,
                'rating': product['rating'],
                'review_count': product['review_count'],
                'image_url': self.get_category_image_url(product['category'])
            }
            
            if skip_duplicates:
                # Check if product exists before inserting
                key = ('grocery', 'products', str(i))
                try:
                    if self.aerospike_manager and self.aerospike_manager.aerospike_client:
                        existing_key, existing_metadata, existing_record = self.aerospike_manager.aerospike_client.get(key)
                        if existing_record:
                            continue
                except:
                    pass  # Key doesn't exist, proceed to create
            
            self.create_aerospike_product(product_data, i)
            products_inserted += 1
            
            if i % 100 == 0:
                if skip_duplicates:
                    print(f"Processed {i} products, inserted {products_inserted} new products into Aerospike...")
                else:
                    print(f"Inserted {i} products into Aerospike...")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        if skip_duplicates:
            print(f"Successfully processed {len(products)} products, inserted {products_inserted} new products into Aerospike in {load_time:.3f} seconds")
        else:
            print(f"Successfully loaded {len(products)} products into Aerospike in {load_time:.3f} seconds")
    
    def load_data_to_mongodb(self, products: List[Dict], category_mapping: Dict[str, int], skip_duplicates: bool = False):
        """Load data into MongoDB database"""
        print("Loading data into MongoDB...")
        start_time = time.time()
        
        # Insert categories
        if skip_duplicates:
            # Check if categories already exist
            if self.mongo_manager and self.mongo_manager.database is not None:
                existing_count = self.mongo_manager.database.categories.count_documents({})
                if existing_count > 0:
                    print("Categories already exist in MongoDB - skipping")
                else:
                    self.create_mongodb_categories(category_mapping)
        else:
            self.create_mongodb_categories(category_mapping)
        
        # Insert products
        products_inserted = 0
        for i, product in enumerate(products, 1):
            category_id = category_mapping[product['category']]
            
            # Create product with category-based fallback image
            product_data = {
                'name': product['title'],  # Use 'title' from CSV data
                'description': product.get('description', ''),
                'price': product['price'],
                'category_id': category_id,
                'stock_quantity': product.get('stock_quantity', 100),
                'image_url': product.get('image_url', self.get_category_image_url(product['category']))
            }
            
            # Check if product already exists (for skip_duplicates mode)
            if skip_duplicates:
                if self.mongo_manager and self.mongo_manager.database is not None:
                    existing_product = self.mongo_manager.database.products.find_one({'id': i})
                    if not existing_product:
                        self.create_mongodb_product(product_data, i)
                        products_inserted += 1
            else:
                self.create_mongodb_product(product_data, i)
                products_inserted += 1
            
            # Progress update
            if i % 100 == 0:
                if skip_duplicates:
                    print(f"Processed {i} products, inserted {products_inserted} new products into MongoDB...")
                else:
                    print(f"Inserted {i} products into MongoDB...")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        if skip_duplicates:
            print(f"Successfully processed {len(products)} products, inserted {products_inserted} new products into MongoDB in {load_time:.3f} seconds")
        else:
            print(f"Successfully loaded {len(products)} products into MongoDB in {load_time:.3f} seconds")
    
    def load_all_data(self, csv_file_path: str, skip_truncate: bool = False):
        """Complete data loading process"""
        print("🚀 Starting complete data loading process...")
        overall_start_time = time.time()
        
        try:
            # Step 1: Load CSV data
            csv_start_time = time.time()
            products = self.load_csv_data(csv_file_path)
            csv_end_time = time.time()
            csv_load_time = csv_end_time - csv_start_time
            print(f"📄 CSV data loaded in {csv_load_time:.3f} seconds")
            
            # Step 2: Create category mapping
            category_mapping = self.get_category_mapping(products)
            print(f"Found {len(category_mapping)} unique categories")
            
            # Step 3: Truncate existing data (optional)
            if not skip_truncate:
                print("🔄 Truncating all existing data...")
                self.truncate_mysql_data()
                self.truncate_aerospike_data()
                self.truncate_mongodb_data()
            else:
                print("⏭️  Skipping truncation - will skip duplicates during insertion")
            
            # Step 4: Load data into all databases
            self.load_data_to_mysql(products, category_mapping, skip_duplicates=skip_truncate)
            self.load_data_to_aerospike(products, category_mapping, skip_duplicates=skip_truncate)
            self.load_data_to_mongodb(products, category_mapping, skip_duplicates=skip_truncate)
            
            overall_end_time = time.time()
            total_time = overall_end_time - overall_start_time
            
            print("✅ Data loading completed successfully!")
            print(f"📊 Total products processed: {len(products)}")
            print(f"📊 Total categories: {len(category_mapping)}")
            print(f"⏱️  Total time: {total_time:.3f} seconds")
            
        except Exception as e:
            overall_end_time = time.time()
            total_time = overall_end_time - overall_start_time
            print(f"❌ Error during data loading after {total_time:.3f} seconds: {e}")
            raise 