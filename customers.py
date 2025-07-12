import sqlite3
from faker import Faker
import random

# Connect to DB
conn = sqlite3.connect('sales.db')
cursor = conn.cursor()

# Initialize Faker
fake = Faker()
regions = ['North', 'South', 'East', 'West']

# ✅ Step 1: Create Customers Table (if not exists)
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    region TEXT
);
''')

# ✅ Step 2: Fetch DISTINCT customer names from sales table
cursor.execute("SELECT DISTINCT customer_name FROM sales")
customer_names = [row[0] for row in cursor.fetchall()]

# ✅ Step 3: Insert customer names into customers table with fake data
for name in customer_names:
    email = fake.email()
    phone = fake.phone_number()
    region = random.choice(regions)
    
    cursor.execute('''
    INSERT INTO customers (customer_name, email, phone, region)
    VALUES (?, ?, ?, ?)
    ''', (name, email, phone, region))

# ✅ Commit and close
conn.commit()
conn.close()

print("Customer names from sales table inserted into customers table successfully.")
