from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key_here_change_this"

# ============ DATABASE SETUP ============

def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

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

    # Products Table (with merchant_id)
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

    # Orders Table (for customers)
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

    # Create default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password, role, created_at)
            VALUES ('admin', 'admin123', 'admin', ?)
        """, (datetime.now().strftime("%Y-%m-%d"),))

    conn.commit()
    conn.close()

# ============ AUTHENTICATION DECORATORS ============

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function

def merchant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'merchant':
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'customer':
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function

# ============ HOME & AUTH ROUTES ============

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        cursor.execute("SELECT user_id, role FROM users WHERE username = ? AND password = ?",
                       (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[1]

            if user[1] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[1] == 'merchant':
                return redirect(url_for('merchant_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, created_at)
                VALUES (?, ?, ?, ?)
            """, (username, password, role, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists"

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

# ============ ADMIN ROUTES ============

@app.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='merchant'")
    total_merchants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='customer'")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM sales")
    total_revenue = cursor.fetchone()[0] or 0

    conn.close()

    return render_template("admin/dashboard.html",
                           total_merchants=total_merchants,
                           total_customers=total_customers,
                           total_products=total_products,
                           total_revenue=total_revenue)

@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("admin/manage_users.html", users=users)

@app.route("/admin/delete_user/<int:user_id>")
@login_required
@admin_required
def admin_delete_user(user_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('admin_users'))

@app.route("/admin/inventory")
@login_required
@admin_required
def admin_inventory():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, u.username 
        FROM products p 
        LEFT JOIN users u ON p.merchant_id = u.user_id
    """)
    products = cursor.fetchall()

    conn.close()

    return render_template("admin/inventory.html", products=products)

@app.route("/admin/analytics")
@login_required
@admin_required
def admin_analytics():
    conn = sqlite3.connect("inventory.db")

    df = pd.read_sql_query("SELECT * FROM sales", conn)

    if df.empty:
        conn.close()
        return render_template("admin/analytics.html", no_data=True)

    total_revenue = df["total"].sum()
    total_products_sold = df["quantity"].sum()
    
    best_product = df.groupby("product_name")["quantity"].sum().idxmax()
    average_sale = np.mean(df["total"])

    # Daily Sales Chart
    daily_sales = df.groupby("sale_date")["total"].sum()

    plt.figure(figsize=(10, 5))
    daily_sales.plot(kind="line", marker='o', color='green')
    plt.title("Daily Revenue")
    plt.xlabel("Date")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig("static/admin_daily_sales.png")
    plt.close()

    # Product Sales Chart
    product_sales = df.groupby("product_name")["quantity"].sum().head(10)

    plt.figure(figsize=(10, 5))
    product_sales.plot(kind="bar", color='skyblue')
    plt.title("Top 10 Products Sold")
    plt.xlabel("Product")
    plt.ylabel("Quantity Sold")
    plt.tight_layout()
    plt.savefig("static/admin_product_sales.png")
    plt.close()

    conn.close()

    return render_template("admin/analytics.html",
                           total_revenue=total_revenue,
                           total_products_sold=total_products_sold,
                           best_product=best_product,
                           average_sale=average_sale,
                           no_data=False)

@app.route("/admin/all_sales")
@login_required
@admin_required
def admin_all_sales():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, u.username as merchant_name, c.username as customer_name
        FROM sales s
        LEFT JOIN users u ON s.merchant_id = u.user_id
        LEFT JOIN users c ON s.customer_id = c.user_id
        ORDER BY s.sale_date DESC
    """)
    sales = cursor.fetchall()

    conn.close()

    return render_template("admin/all_sales.html", sales=sales)

# ============ MERCHANT ROUTES ============

@app.route("/merchant/dashboard")
@login_required
@merchant_required
def merchant_dashboard():
    merchant_id = session['user_id']
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM products WHERE merchant_id = ?", (merchant_id,))
    my_products = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM sales WHERE merchant_id = ?", (merchant_id,))
    my_revenue = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM sales WHERE merchant_id = ?", (merchant_id,))
    my_sales = cursor.fetchone()[0]

    conn.close()

    return render_template("merchant/dashboard.html",
                           my_products=my_products,
                           my_revenue=my_revenue,
                           my_sales=my_sales)

@app.route("/merchant/inventory")
@login_required
@merchant_required
def merchant_inventory():
    merchant_id = session['user_id']
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE merchant_id = ?", (merchant_id,))
    products = cursor.fetchall()

    conn.close()

    return render_template("merchant/my_inventory.html", products=products)

@app.route("/merchant/add_product", methods=["POST"])
@login_required
@merchant_required
def merchant_add_product():
    merchant_id = session['user_id']
    
    product_id = request.form["product_id"]
    name = request.form["name"]
    quantity = int(request.form["quantity"])
    price = float(request.form["price"])

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?)",
                       (product_id, name, quantity, price, merchant_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect(url_for('merchant_inventory'))

@app.route("/merchant/update_product", methods=["POST"])
@login_required
@merchant_required
def merchant_update_product():
    merchant_id = session['user_id']
    
    product_id = request.form["product_id"]
    price = float(request.form["price"])

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE products SET price = ? WHERE product_id = ? AND merchant_id = ?",
                   (price, product_id, merchant_id))

    conn.commit()
    conn.close()

    return redirect(url_for('merchant_inventory'))

@app.route("/merchant/delete_product/<product_id>")
@login_required
@merchant_required
def merchant_delete_product(product_id):
    merchant_id = session['user_id']
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE product_id = ? AND merchant_id = ?",
                   (product_id, merchant_id))

    conn.commit()
    conn.close()

    return redirect(url_for('merchant_inventory'))

@app.route("/merchant/restock", methods=["POST"])
@login_required
@merchant_required
def merchant_restock():
    merchant_id = session['user_id']
    
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE products SET quantity = quantity + ? WHERE product_id = ? AND merchant_id = ?",
                   (quantity, product_id, merchant_id))

    conn.commit()
    conn.close()

    return redirect(url_for('merchant_inventory'))

@app.route("/merchant/sell")
@login_required
@merchant_required
def merchant_sell_page():
    merchant_id = session['user_id']
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE merchant_id = ?", (merchant_id,))
    products = cursor.fetchall()

    conn.close()

    return render_template("merchant/sell.html", products=products)

@app.route("/merchant/sell_product", methods=["POST"])
@login_required
@merchant_required
def merchant_sell_product():
    merchant_id = session['user_id']
    
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])
    customer_name = request.form.get("customer_name", "Walk-in")

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, quantity, price FROM products WHERE product_id = ? AND merchant_id = ?",
                   (product_id, merchant_id))
    product = cursor.fetchone()

    if product:
        name, stock, price = product

        if stock >= quantity:
            total = price * quantity

            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
                           (quantity, product_id))

            date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO sales (product_id, product_name, quantity, price, total, merchant_id, sale_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, name, quantity, price, total, merchant_id, date))

            conn.commit()

    conn.close()
    return redirect(url_for('merchant_sell_page'))

@app.route("/merchant/my_sales")
@login_required
@merchant_required
def merchant_my_sales():
    merchant_id = session['user_id']
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales WHERE merchant_id = ? ORDER BY sale_date DESC", (merchant_id,))
    sales = cursor.fetchall()

    conn.close()

    return render_template("merchant/my_sales.html", sales=sales)

# ============ CUSTOMER ROUTES ============

@app.route("/customer/dashboard")
@login_required
@customer_required
def customer_dashboard():
    return render_template("customer/dashboard.html")

@app.route("/customer/products")
@login_required
@customer_required
def customer_products():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, u.username as merchant_name 
        FROM products p 
        LEFT JOIN users u ON p.merchant_id = u.user_id
        WHERE p.quantity > 0
    """)
    products = cursor.fetchall()

    conn.close()

    return render_template("customer/products.html", products=products)

@app.route("/customer/add_to_cart", methods=["POST"])
@login_required
@customer_required
def customer_add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, price, merchant_id FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()

    if product:
        name, price, merchant_id = product
        
        cart = session['cart']
        cart.append({
            'product_id': product_id,
            'name': name,
            'price': price,
            'quantity': quantity,
            'merchant_id': merchant_id
        })
        session['cart'] = cart

    return redirect(url_for('customer_products'))

@app.route("/customer/cart")
@login_required
@customer_required
def customer_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template("customer/cart.html", cart=cart, total=total)

@app.route("/customer/checkout", methods=["POST"])
@login_required
@customer_required
def customer_checkout():
    customer_id = session['user_id']
    cart = session.get('cart', [])

    if not cart:
        return redirect(url_for('customer_cart'))

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    for item in cart:
        # Check stock
        cursor.execute("SELECT quantity FROM products WHERE product_id = ?", (item['product_id'],))
        stock = cursor.fetchone()[0]

        if stock >= item['quantity']:
            # Reduce stock
            cursor.execute("UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
                           (item['quantity'], item['product_id']))

            # Create order
            total = item['price'] * item['quantity']
            cursor.execute("""
                INSERT INTO orders (customer_id, product_id, product_name, quantity, total, status, order_date)
                VALUES (?, ?, ?, ?, ?, 'Confirmed', ?)
            """, (customer_id, item['product_id'], item['name'], item['quantity'], total, date))

            # Record sale
            cursor.execute("""
                INSERT INTO sales (product_id, product_name, quantity, price, total, merchant_id, customer_id, sale_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (item['product_id'], item['name'], item['quantity'], item['price'], total, item['merchant_id'], customer_id, date))

    conn.commit()
    conn.close()

    # Clear cart
    session['cart'] = []

    return redirect(url_for('customer_my_orders'))

@app.route("/customer/clear_cart")
@login_required
@customer_required
def customer_clear_cart():
    session['cart'] = []
    return redirect(url_for('customer_cart'))

@app.route("/customer/my_orders")
@login_required
@customer_required
def customer_my_orders():
    customer_id = session['user_id']
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC", (customer_id,))
    orders = cursor.fetchall()

    conn.close()

    return render_template("customer/my_orders.html", orders=orders)

# ============ RUN APP ============

if __name__ == "__main__":
    init_db()
    app.run(debug=True)