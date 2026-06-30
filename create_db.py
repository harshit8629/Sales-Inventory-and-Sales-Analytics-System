import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # ============ CREATE TABLES ============

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TEXT
    )
    """)

    # Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        merchant_id INTEGER,
        FOREIGN KEY (merchant_id) REFERENCES users(user_id)
    )
    """)

    # Sales Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id TEXT,
        product_name TEXT,
        quantity INTEGER,
        price REAL,
        total REAL,
        merchant_id INTEGER,
        customer_id INTEGER,
        sale_date TEXT,
        FOREIGN KEY (merchant_id) REFERENCES users(user_id),
        FOREIGN KEY (customer_id) REFERENCES users(user_id)
    )
    """)

    # Orders Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id TEXT,
        product_name TEXT,
        quantity INTEGER,
        total REAL,
        status TEXT,
        order_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES users(user_id)
    )
    """)

    # ============ INSERT DEFAULT DATA ============

    date = datetime.now().strftime("%Y-%m-%d")

    # Default Admin
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, role, created_at)
        VALUES ('admin', 'admin123', 'admin', ?)
    """, (date,))

    # Default Merchant
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, role, created_at)
        VALUES ('merchant1', 'merchant123', 'merchant', ?)
    """, (date,))

    # Default Customer
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, role, created_at)
        VALUES ('customer1', 'customer123', 'customer', ?)
    """, (date,))

    # Default Products for merchant1 (user_id = 2)
    cursor.execute("""
        INSERT OR IGNORE INTO products (product_id, name, quantity, price, merchant_id)
        VALUES ('P001', 'Laptop', 10, 50000, 2)
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO products (product_id, name, quantity, price, merchant_id)
        VALUES ('P002', 'Mouse', 50, 500, 2)
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO products (product_id, name, quantity, price, merchant_id)
        VALUES ('P003', 'Keyboard', 30, 1500, 2)
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO products (product_id, name, quantity, price, merchant_id)
        VALUES ('P004', 'Monitor', 15, 12000, 2)
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO products (product_id, name, quantity, price, merchant_id)
        VALUES ('P005', 'Headphones', 40, 2000, 2)
    """)

    # Sample Sales Data
    cursor.execute("""
        INSERT OR IGNORE INTO sales (product_id, product_name, quantity, price, total, merchant_id, customer_id, sale_date)
        VALUES ('P001', 'Laptop', 2, 50000, 100000, 2, 3, '2024-01-15')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO sales (product_id, product_name, quantity, price, total, merchant_id, customer_id, sale_date)
        VALUES ('P002', 'Mouse', 5, 500, 2500, 2, 3, '2024-01-16')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO sales (product_id, product_name, quantity, price, total, merchant_id, customer_id, sale_date)
        VALUES ('P003', 'Keyboard', 3, 1500, 4500, 2, 3, '2024-01-17')
    """)

    conn.commit()
    conn.close()

    print("✅ Database created successfully!")
    print("\n📌 Default Login Credentials:")
    print("=" * 50)
    print("Admin    → Username: admin      Password: admin123")
    print("Merchant → Username: merchant1  Password: merchant123")
    print("Customer → Username: customer1  Password: customer123")
    print("=" * 50)

if __name__ == "__main__":
    create_database()