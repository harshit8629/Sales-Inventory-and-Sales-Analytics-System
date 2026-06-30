# 🏪 Sales-Inventory-and-Sales-Analytics-System

A full-stack multi-user Inventory & E-Commerce Management System built using **Flask, SQLite, Pandas, NumPy, and Matplotlib**.

This system simulates a real-world marketplace like Amazon or Flipkart where:

- 👨‍💼 Admin manages the entire platform  
- 🏬 Merchants manage their products & sales  
- 🛒 Customers browse and purchase products  

---

## 🚀 Features

### 👨‍💼 Admin Portal
- View total merchants, customers, products
- Monitor total revenue
- View complete inventory
- View all sales records
- Sales analytics dashboard (charts & insights)
- Manage users

### 🏬 Merchant Portal
- Add, update, delete products
- Restock inventory
- Sell products
- Track personal sales history
- View total revenue & performance

### 🛒 Customer Portal
- Browse available products
- Add products to cart
- Checkout & place orders
- View order history
- Track order status

### 📊 Analytics Dashboard
- Total Revenue
- Total Products Sold
- Best Selling Product
- Average Sale Value
- Daily Revenue Chart
- Top Products Chart

---

## 🏗️ System Architecture

Frontend (HTML, CSS)
        ↓
Flask Backend (Python)
        ↓
SQLite Database
        ↓
Pandas + NumPy + Matplotlib (Analytics)

---

## 🗄️ Database Structure

### Users Table
- user_id
- username
- password
- role (admin / merchant / customer)
- created_at

### Products Table
- product_id
- name
- quantity
- price
- merchant_id

### Sales Table
- sale_id
- product_id
- product_name
- quantity
- price
- total
- merchant_id
- customer_id
- sale_date

### Orders Table
- order_id
- customer_id
- product_id
- product_name
- quantity
- total
- status
- order_date

---

## 🛠️ Technology Stack

Backend:
- Python 3.x
- Flask

Database:
- SQLite

Data Analytics:
- Pandas
- NumPy
- Matplotlib

Frontend:
- HTML5
- CSS3
- Jinja2 Templates

---

## 📂 Project Structure

inventory_project/
│
├── app.py
├── create_db.py
├── inventory.db
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── admin/
│   ├── merchant/
│   └── customer/
│
└── static/
    └── style.css

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

git clone https://github.com/your-username/inventory-system.git  
cd inventory-system  

### 2️⃣ Install Dependencies

pip install flask pandas matplotlib numpy  

### 3️⃣ Create Database

python create_db.py  

### 4️⃣ Run Application

python app.py  

### 5️⃣ Open in Browser

http://127.0.0.1:5000  

---

## 🔐 Default Login Credentials

Admin  
Username: admin  
Password: admin123  

Merchant  
Username: merchant1  
Password: merchant123  

Customer  
Username: customer1  
Password: customer123  

---

## 📈 Real-World Applications

This system can be used by:

- Small businesses
- Multi-vendor marketplaces
- Retail stores
- E-commerce startups
- Inventory management systems
- Educational projects

---

## 🎯 Key Learning Outcomes

- Role-Based Access Control
- Flask Web Development
- SQLite Database Design
- Data Analysis with Pandas
- Data Visualization with Matplotlib
- Session Management
- Shopping Cart Implementation
- Full-stack architecture

---

## 🚧 Challenges Faced

- Managing session-based authentication
- Handling real-time stock updates
- Implementing role restrictions
- Generating charts dynamically
- Designing relational database schema

---

## 🔮 Future Improvements

- Payment Gateway Integration
- Email Notifications
- Advanced Sales Forecasting
- Product Reviews & Ratings
- Export Reports (PDF/Excel)
- REST API Support
- Docker Deployment

---

## 📌 Conclusion

This project demonstrates a real-world implementation of a multi-user inventory and sales management system integrating:

- Backend Development
- Database Management
- Data Analytics
- Visualization
- Web Interface Design

It simulates how modern e-commerce platforms operate at a foundational level.

---

## 👨‍💻 Author

Your Name  
Harshit Khanna

---

⭐ If you like this project, give it a star on GitHub!
