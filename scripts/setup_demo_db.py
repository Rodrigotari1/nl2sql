#!/usr/bin/env python3
"""
Demo database setup script
Creates sample tables and data for testing the natural language SQL tool
"""

import psycopg2
from datetime import datetime, timedelta
import random

def create_demo_database(database_url: str):
    """Create demo database with sample data"""
    
    with psycopg2.connect(database_url) as conn:
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute("""
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS users;
        """)
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(50) NOT NULL
            );
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                total DECIMAL(10,2) NOT NULL,
                order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE order_items (
                order_id INTEGER NOT NULL REFERENCES orders(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL,
                PRIMARY KEY (order_id, product_id)
            );
        """)
        
        # Create indexes for performance optimization
        print("📊 Creating performance indexes...")
        
        # Foreign key indexes (CRITICAL - always index foreign keys)
        cursor.execute("CREATE INDEX idx_orders_user_id ON orders(user_id);")
        cursor.execute("CREATE INDEX idx_order_items_order_id ON order_items(order_id);")
        cursor.execute("CREATE INDEX idx_order_items_product_id ON order_items(product_id);")
        
        # Frequently searched columns
        cursor.execute("CREATE INDEX idx_users_email ON users(email);")  # Email lookups
        cursor.execute("CREATE INDEX idx_products_category ON products(category);")  # Category filtering
        cursor.execute("CREATE INDEX idx_orders_order_date ON orders(order_date);")  # Date range queries
        
        # Composite indexes for complex queries
        cursor.execute("CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);")  # User's orders by date
        cursor.execute("CREATE INDEX idx_products_category_price ON products(category, price);")  # Category + price filtering
        
        # Functional indexes for search
        cursor.execute("CREATE INDEX idx_users_name_lower ON users(LOWER(name));")  # Case-insensitive name search
        cursor.execute("CREATE INDEX idx_products_name_lower ON products(LOWER(name));")  # Case-insensitive product search
        
        print("✅ Indexes created successfully!")
        
        # Insert sample users
        users_data = [
            ('Alice Johnson', 'alice@example.com'),
            ('Bob Smith', 'bob@example.com'),
            ('Carol Williams', 'carol@example.com'),
            ('David Brown', 'david@example.com'),
            ('Eva Davis', 'eva@example.com'),
            ('Frank Miller', 'frank@example.com'),
            ('Grace Wilson', 'grace@example.com'),
            ('Henry Moore', 'henry@example.com'),
            ('Ivy Taylor', 'ivy@example.com'),
            ('Jack Anderson', 'jack@example.com'),
        ]
        
        for name, email in users_data:
            # Random creation date in the last year
            days_ago = random.randint(0, 365)
            created_at = datetime.now() - timedelta(days=days_ago)
            cursor.execute(
                "INSERT INTO users (name, email, created_at) VALUES (%s, %s, %s)",
                (name, email, created_at)
            )
        
        # Insert sample products
        products_data = [
            ('iPhone 15', 999.99, 'Electronics'),
            ('MacBook Air', 1199.99, 'Electronics'),
            ('Nike Air Max', 129.99, 'Shoes'),
            ('Adidas Ultraboost', 179.99, 'Shoes'),
            ('Coffee Mug', 12.99, 'Home'),
            ('Wireless Headphones', 199.99, 'Electronics'),
            ('Running Shorts', 39.99, 'Clothing'),
            ('Yoga Mat', 49.99, 'Sports'),
            ('Water Bottle', 24.99, 'Home'),
            ('Backpack', 79.99, 'Accessories'),
            ('Laptop Stand', 89.99, 'Electronics'),
            ('Desk Lamp', 45.99, 'Home'),
            ('Bluetooth Speaker', 149.99, 'Electronics'),
            ('Kitchen Scale', 34.99, 'Home'),
            ('Protein Powder', 59.99, 'Health'),
        ]
        
        for name, price, category in products_data:
            cursor.execute(
                "INSERT INTO products (name, price, category) VALUES (%s, %s, %s)",
                (name, price, category)
            )
        
        # Get user and product IDs for creating orders
        cursor.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id, price FROM products")
        products = cursor.fetchall()
        
        # Insert sample orders
        for user_id in user_ids:
            # Each user gets 0-5 orders
            num_orders = random.randint(0, 5)
            
            for _ in range(num_orders):
                # Random order date in the last 6 months
                days_ago = random.randint(0, 180)
                order_date = datetime.now() - timedelta(days=days_ago)
                
                # Select 1-4 random products for this order
                num_items = random.randint(1, 4)
                selected_products = random.sample(products, num_items)
                
                # Calculate total
                total = 0
                order_items = []
                
                for product_id, price in selected_products:
                    quantity = random.randint(1, 3)
                    total += float(price) * quantity
                    order_items.append((product_id, quantity))
                
                # Insert order
                cursor.execute(
                    "INSERT INTO orders (user_id, total, order_date) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, total, order_date)
                )
                order_id = cursor.fetchone()[0]
                
                # Insert order items
                for product_id, quantity in order_items:
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (order_id, product_id, quantity)
                    )
        
        conn.commit()
        print("✅ Demo database created successfully!")
        
        # Print some stats
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM order_items")
        item_count = cursor.fetchone()[0]
        
        print(f"📊 Database Stats:")
        print(f"   Users: {user_count}")
        print(f"   Products: {product_count}")
        print(f"   Orders: {order_count}")
        print(f"   Order Items: {item_count}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python setup_demo_db.py <database_url>")
        print("Example: python setup_demo_db.py 'postgresql://user:pass@localhost:5432/demo_db'")
        sys.exit(1)
    
    database_url = sys.argv[1]
    
    try:
        create_demo_database(database_url)
    except Exception as e:
        print(f"❌ Error creating demo database: {e}")
        sys.exit(1) 