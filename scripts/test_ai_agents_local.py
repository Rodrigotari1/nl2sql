"""
Quick local test for AI Database Agents using SQLite
No external database needed!
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_local_demo():
    """Create a local SQLite database for testing"""
    
    # Create database in current directory
    db_path = "demo_business.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 Creating local AI Database Agents demo...")
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            signup_date DATE NOT NULL,
            total_spent DECIMAL(10,2) DEFAULT 0.00,
            country TEXT,
            customer_segment TEXT DEFAULT 'regular'
        );
    """)
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            created_date DATE NOT NULL
        );
    """)
    
    # Create campaigns table
    cursor.execute("""
        CREATE TABLE campaigns (
            campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            channel TEXT NOT NULL,
            budget DECIMAL(10,2) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            conversions INTEGER DEFAULT 0
        );
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            campaign_id INTEGER,
            order_date TIMESTAMP NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'completed',
            shipping_country TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
        );
    """)
    
    # Insert sample data
    customers_data = [
        ('John Smith', 'john@email.com', '2023-01-15', 'USA', 'premium'),
        ('Sarah Johnson', 'sarah@email.com', '2023-02-20', 'Canada', 'regular'),
        ('Mike Chen', 'mike@email.com', '2023-03-10', 'UK', 'premium'),
        ('Emily Davis', 'emily@email.com', '2023-04-05', 'Australia', 'regular'),
        ('David Wilson', 'david@email.com', '2023-05-12', 'Germany', 'premium')
    ]
    
    for name, email, signup, country, segment in customers_data:
        cursor.execute("""
            INSERT INTO customers (name, email, signup_date, country, customer_segment)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, signup, country, segment))
    
    products_data = [
        ('Wireless Headphones', 'Electronics', 99.99, 45.00, 150),
        ('Smart Watch', 'Electronics', 199.99, 120.00, 75),
        ('Coffee Mug', 'Home & Kitchen', 19.99, 8.00, 300),
        ('Laptop Stand', 'Office', 49.99, 25.00, 200),
        ('Phone Case', 'Accessories', 24.99, 12.00, 500)
    ]
    
    for name, category, price, cost, stock in products_data:
        cursor.execute("""
            INSERT INTO products (name, category, price, cost, stock_quantity, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, category, price, cost, stock, '2023-01-01'))
    
    campaigns_data = [
        ('Summer Sale 2024', 'Email', 5000.00, '2024-06-01', '2024-08-31'),
        ('Black Friday', 'Social Media', 10000.00, '2024-11-25', '2024-11-30'),
        ('New Year Promo', 'Google Ads', 7500.00, '2024-01-01', '2024-01-15')
    ]
    
    for name, channel, budget, start, end in campaigns_data:
        cursor.execute("""
            INSERT INTO campaigns (name, channel, budget, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, channel, budget, start, end))
    
    # Generate sample orders
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(50):  # Generate 50 orders
        customer_id = random.randint(1, 5)
        campaign_id = random.randint(1, 3) if random.random() > 0.3 else None
        
        days_ago = random.randint(0, 90)
        order_date = start_date + timedelta(days=days_ago)
        
        total_amount = round(random.uniform(25.00, 500.00), 2)
        countries = ['USA', 'Canada', 'UK', 'Australia', 'Germany']
        shipping_country = random.choice(countries)
        
        cursor.execute("""
            INSERT INTO orders (customer_id, campaign_id, order_date, total_amount, shipping_country)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_id, campaign_id, order_date, total_amount, shipping_country))
    
    # Update customer total_spent
    cursor.execute("""
        UPDATE customers 
        SET total_spent = (
            SELECT COALESCE(SUM(total_amount), 0) 
            FROM orders 
            WHERE orders.customer_id = customers.customer_id
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Local demo database created!")
    print(f"📁 Database file: {os.path.abspath(db_path)}")
    
    return db_path

if __name__ == "__main__":
    print("🤖 AI Database Agents - Local Demo Setup")
    print("=" * 45)
    
    db_path = create_local_demo()
    
    print("\n🎯 Next steps:")
    print("1. Go to http://localhost:8000")
    print("2. Use this connection string:")
    print(f"   sqlite:///{os.path.abspath(db_path)}")
    print("\n💡 Try these AI agent queries:")
    print("   • 'Who are our top customers by total spent?'")
    print("   • 'Which products are in the Electronics category?'")
    print("   • 'Show me recent orders from the last month'")
    print("   • 'What campaigns have the most conversions?'")
    print("   • 'Compare revenue by country'")
    print("\n🤖 Watch the AI agents work their magic!") 