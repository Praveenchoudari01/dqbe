import sqlite3
from faker import Faker
import random

# Initialize Faker for generating random data
fake = Faker()

# Connect to SQLite DB (creates file if it doesn't exist)
conn = sqlite3.connect('sales.db')
cursor = conn.cursor()

# Create Table (your structure)
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    product TEXT,
    amount INTEGER,
    order_date DATE,
    region TEXT
);
''')

# Sample product and region lists
products = ['Widget A', 'Widget B', 'Widget C', 'Widget D']
regions = ['North', 'South', 'East', 'West']

# Generate 100 sample records (with possible name repeats)
sales_data = []
for _ in range(100):
    customer_name = fake.first_name()
    product = random.choice(products)
    amount = random.randint(50, 500)
    order_date = fake.date_between(start_date='-1y', end_date='today').isoformat()
    region = random.choice(regions)
    sales_data.append((customer_name, product, amount, order_date, region))

# Insert data
cursor.executemany('''
INSERT INTO sales (customer_name, product, amount, order_date, region)
VALUES (?, ?, ?, ?, ?)
''', sales_data)

# Commit & Close
conn.commit()
conn.close()

# Create Customers Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    region TEXT
);
''')

# Create Products Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    category TEXT,
    price INTEGER
);
''')

# Insert Sample Customers (same names from sales + random ones)
customer_names = list(set([row[0] for row in sales_data]))
for name in customer_names:
    email = fake.email()
    phone = fake.phone_number()
    region = random.choice(regions)
    cursor.execute('''
    INSERT INTO customers (customer_name, email, phone, region)
    VALUES (?, ?, ?, ?)
    ''', (name, email, phone, region))

# Insert Sample Products (same products as in sales)
product_categories = ['Electronics', 'Appliances', 'Toys', 'Furniture']
for product in products:
    category = random.choice(product_categories)
    price = random.randint(100, 2000)
    cursor.execute('''
    INSERT INTO products (product_name, category, price)
    VALUES (?, ?, ?)
    ''', (product, category, price))

# Commit & Close
conn.commit()
conn.close()

print("Customers and Products tables created with sample data.")

print("Database 'sales.db' created with 100 sample sales records.")
