"""
Setup demo data in Supabase for testing AI Database Agents
Run this script to create sample business data
"""

import psycopg2
import random
from datetime import datetime, timedelta

# Example Supabase connection string format:
# postgresql://postgres.your_project_ref:your_password@aws-0-us-west-1.pooler.supabase.com:6543/postgres

def setup_demo_data(connection_string):
    """Create demo business data for testing AI agents"""
    
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    try:
        print("🚀 Setting up AI Database Agents demo data...")
        
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS order_items CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS orders CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS products CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS customers CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS campaigns CASCADE;")
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                signup_date DATE NOT NULL,
                total_spent DECIMAL(10,2) DEFAULT 0.00,
                country VARCHAR(50),
                customer_segment VARCHAR(20) DEFAULT 'regular'
            );
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                cost DECIMAL(10,2) NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                created_date DATE NOT NULL
            );
        """)
        
        # Create campaigns table
        cursor.execute("""
            CREATE TABLE campaigns (
                campaign_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                channel VARCHAR(50) NOT NULL,
                budget DECIMAL(10,2) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                conversions INTEGER DEFAULT 0
            );
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(customer_id),
                campaign_id INTEGER REFERENCES campaigns(campaign_id),
                order_date TIMESTAMP NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'completed',
                shipping_country VARCHAR(50)
            );
        """)
        
        # Create order_items table
        cursor.execute("""
            CREATE TABLE order_items (
                item_id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                product_id INTEGER REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL
            );
        """)
        
        print("✅ Tables created successfully!")
        
        # Insert sample customers
        customers_data = [
            ('John Smith', 'john@email.com', '2023-01-15', 'USA', 'premium'),
            ('Sarah Johnson', 'sarah@email.com', '2023-02-20', 'Canada', 'regular'),
            ('Mike Chen', 'mike@email.com', '2023-03-10', 'UK', 'premium'),
            ('Emily Davis', 'emily@email.com', '2023-04-05', 'Australia', 'regular'),
            ('David Wilson', 'david@email.com', '2023-05-12', 'Germany', 'premium'),
            ('Lisa Brown', 'lisa@email.com', '2023-06-08', 'France', 'regular'),
            ('Tom Anderson', 'tom@email.com', '2023-07-15', 'USA', 'premium'),
            ('Anna Martinez', 'anna@email.com', '2023-08-20', 'Spain', 'regular'),
            ('Chris Taylor', 'chris@email.com', '2023-09-10', 'UK', 'premium'),
            ('Jennifer Lee', 'jennifer@email.com', '2023-10-05', 'Canada', 'regular')
        ]
        
        for name, email, signup, country, segment in customers_data:
            cursor.execute("""
                INSERT INTO customers (name, email, signup_date, country, customer_segment)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, signup, country, segment))
        
        print("✅ Customers inserted!")
        
        # Insert sample products
        products_data = [
            ('Wireless Headphones', 'Electronics', 99.99, 45.00, 150),
            ('Smart Watch', 'Electronics', 199.99, 120.00, 75),
            ('Coffee Mug', 'Home & Kitchen', 19.99, 8.00, 300),
            ('Laptop Stand', 'Office', 49.99, 25.00, 200),
            ('Phone Case', 'Accessories', 24.99, 12.00, 500),
            ('Bluetooth Speaker', 'Electronics', 79.99, 40.00, 120),
            ('Desk Lamp', 'Office', 34.99, 18.00, 180),
            ('Water Bottle', 'Sports', 29.99, 15.00, 250),
            ('Notebook Set', 'Office', 14.99, 7.00, 400),
            ('Wireless Charger', 'Electronics', 39.99, 20.00, 160)
        ]
        
        for name, category, price, cost, stock in products_data:
            cursor.execute("""
                INSERT INTO products (name, category, price, cost, stock_quantity, created_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, category, price, cost, stock, '2023-01-01'))
        
        print("✅ Products inserted!")
        
        # Insert sample campaigns
        campaigns_data = [
            ('Summer Sale 2024', 'Email', 5000.00, '2024-06-01', '2024-08-31'),
            ('Black Friday', 'Social Media', 10000.00, '2024-11-25', '2024-11-30'),
            ('New Year Promo', 'Google Ads', 7500.00, '2024-01-01', '2024-01-15'),
            ('Spring Launch', 'Instagram', 3000.00, '2024-03-01', '2024-04-30'),
            ('Holiday Special', 'Facebook', 6000.00, '2024-12-01', '2024-12-25')
        ]
        
        for name, channel, budget, start, end in campaigns_data:
            cursor.execute("""
                INSERT INTO campaigns (name, channel, budget, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, channel, budget, start, end))
        
        print("✅ Campaigns inserted!")
        
        # Generate sample orders (last 6 months)
        print("📦 Generating sample orders...")
        
        start_date = datetime.now() - timedelta(days=180)
        
        for i in range(250):  # Generate 250 orders
            # Random customer and campaign
            customer_id = random.randint(1, 10)
            campaign_id = random.randint(1, 5) if random.random() > 0.3 else None
            
            # Random order date
            days_ago = random.randint(0, 180)
            order_date = start_date + timedelta(days=days_ago)
            
            # Random country (bias towards customer's country)
            countries = ['USA', 'Canada', 'UK', 'Australia', 'Germany', 'France', 'Spain']
            shipping_country = random.choice(countries)
            
            # Calculate total (will update after items)
            cursor.execute("""
                INSERT INTO orders (customer_id, campaign_id, order_date, total_amount, shipping_country)
                VALUES (%s, %s, %s, %s, %s) RETURNING order_id
            """, (customer_id, campaign_id, order_date, 0.00, shipping_country))
            
            order_id = cursor.fetchone()[0]
            
            # Add 1-4 items per order
            num_items = random.randint(1, 4)
            total_amount = 0
            
            for _ in range(num_items):
                product_id = random.randint(1, 10)
                quantity = random.randint(1, 3)
                
                # Get product price
                cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
                unit_price = cursor.fetchone()[0]
                
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, product_id, quantity, unit_price))
                
                total_amount += unit_price * quantity
            
            # Update order total
            cursor.execute("""
                UPDATE orders SET total_amount = %s WHERE order_id = %s
            """, (total_amount, order_id))
        
        # Update customer total_spent
        cursor.execute("""
            UPDATE customers 
            SET total_spent = (
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM orders 
                WHERE orders.customer_id = customers.customer_id
            )
        """)
        
        # Update campaign conversions
        cursor.execute("""
            UPDATE campaigns 
            SET conversions = (
                SELECT COUNT(*) 
                FROM orders 
                WHERE orders.campaign_id = campaigns.campaign_id
            )
        """)
        
        conn.commit()
        print("✅ Sample orders and items generated!")
        print("🎉 Demo data setup complete!")
        print("\n📊 Summary:")
        
        # Show summary stats
        cursor.execute("SELECT COUNT(*) FROM customers")
        print(f"   • {cursor.fetchone()[0]} customers")
        
        cursor.execute("SELECT COUNT(*) FROM products") 
        print(f"   • {cursor.fetchone()[0]} products")
        
        cursor.execute("SELECT COUNT(*) FROM campaigns")
        print(f"   • {cursor.fetchone()[0]} campaigns")
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        print(f"   • {cursor.fetchone()[0]} orders")
        
        cursor.execute("SELECT COUNT(*) FROM order_items")
        print(f"   • {cursor.fetchone()[0]} order items")
        
        cursor.execute("SELECT SUM(total_amount) FROM orders")
        total_revenue = cursor.fetchone()[0]
        print(f"   • ${total_revenue:.2f} total revenue")
        
        print("\n🤖 Your AI Database Agents can now analyze:")
        print("   • Customer behavior and segmentation")
        print("   • Product performance and profitability")
        print("   • Campaign effectiveness and ROI")
        print("   • Sales trends and patterns")
        print("   • Geographic distribution")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 AI Database Agents - Supabase Demo Setup")
    print("=" * 50)
    
    # You'll need to replace this with your actual Supabase connection string
    connection_string = input("Enter your Supabase PostgreSQL connection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided!")
        print("\n📝 How to get your Supabase connection string:")
        print("1. Go to your Supabase project dashboard")
        print("2. Go to Settings > Database")
        print("3. Copy the connection string (URI format)")
        print("4. Replace the password placeholder with your actual password")
        print("\nExample format:")
        print("postgresql://postgres.xxxxx:your_password@aws-0-us-west-1.pooler.supabase.com:6543/postgres")
        exit(1)
    
    try:
        setup_demo_data(connection_string)
        print(f"\n🎯 Next steps:")
        print(f"1. Go to http://localhost:8000")
        print(f"2. Connect using your Supabase connection string")
        print(f"3. Try these AI agent queries:")
        print(f"   • 'Who are our top customers by revenue?'")
        print(f"   • 'Which marketing campaigns are most effective?'")
        print(f"   • 'What products have the highest profit margins?'")
        print(f"   • 'Show me sales trends over the last 6 months'")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("• Make sure your Supabase project is active")
        print("• Check your connection string format")
        print("• Verify your password is correct")
        print("• Ensure your IP is allowed (or use connection pooler)") 