-- Create database and use it
USE grocery_db;

-- Create tables
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    icon VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(200),
    stock INT DEFAULT 0,
    category_id INT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    delivery_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert sample categories
INSERT INTO categories (name, icon) VALUES
('Fruits & Vegetables', '🥕'),
('Dairy & Eggs', '🥛'),
('Meat & Seafood', '🥩'),
('Bakery', '🍞'),
('Beverages', '🥤'),
('Snacks', '🍿');

-- Insert sample products
INSERT INTO products (name, description, price, category_id, stock, image_url) VALUES
('Fresh Bananas', 'Ripe yellow bananas', 2.99, 1, 50, 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=300&h=200&fit=crop'),
('Organic Apples', 'Crisp red apples', 3.49, 1, 30, 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=300&h=200&fit=crop'),
('Whole Milk', 'Fresh whole milk 1L', 3.29, 2, 20, 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=200&fit=crop'),
('Free Range Eggs', 'Dozen organic eggs', 4.99, 2, 15, 'https://images.unsplash.com/photo-1518569656558-1f25e69d93d7?w=300&h=200&fit=crop'),
('Salmon Fillet', 'Fresh Atlantic salmon', 12.99, 3, 10, 'https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=300&h=200&fit=crop'),
('Chicken Breast', 'Boneless chicken breast', 8.99, 3, 25, 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=300&h=200&fit=crop'),
('Sourdough Bread', 'Artisan sourdough loaf', 4.49, 4, 12, 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=200&fit=crop'),
('Orange Juice', 'Fresh squeezed orange juice', 4.99, 5, 18, 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=300&h=200&fit=crop'),
('Potato Chips', 'Crispy potato chips', 2.49, 6, 40, 'https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=300&h=200&fit=crop'),
('Greek Yogurt', 'Creamy Greek yogurt', 1.99, 2, 35, 'https://images.unsplash.com/photo-1571212515416-8fc82f26c7c2?w=300&h=200&fit=crop'); 