import mysql.connector

# Configuration for MySQL connection
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",       # Change if needed
    "password": "root",   # Change if needed
    "database": "PES_Surplus_Store"
}

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Initial connection to MySQL (no DB selected yet)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root"
)
cursor = conn.cursor()

# Create the database if not exists
cursor.execute("USE PES_Surplus_Store")

# ========== USERS ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'customer') DEFAULT 'customer',
    CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
)
""")

# ========== PRODUCTS ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    quantity INT NOT NULL CHECK (quantity >= 0),
    description TEXT,
    image_url VARCHAR(255)
)
""")

# ========== ORDERS ==========
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    products TEXT,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
""")

# ========== DEFAULT ADMIN ==========
cursor.execute("""
INSERT INTO users (FirstName, LastName, email, password, role)
VALUES ('Admin', 'User', 'admin@pes.edu', 'admin123', 'admin')
ON DUPLICATE KEY UPDATE email = email
""")

# ========== DEFAULT PRODUCTS ==========
default_products = [
    ("Bose Headphones", "Electronics", 199.99, 10, "Noise-canceling wireless headphones", "assets/headphones.png"),
    ("MacBook Air", "Electronics", 999.99, 5, "Apple MacBook Air M1 chip", "assets/macbook.jpeg"),
    ("Office Chair", "Furniture", 149.99, 8, "Ergonomic office chair", "assets/office-chair.png"),
    ("Smart TV", "Electronics", 499.99, 7, "55-inch 4K Smart TV", "assets/smarttv.png"),
    ("Sofa Set", "Furniture", 799.99, 3, "Luxury 3-seater sofa", "assets/sofaset.png"),
    ("Wireless Mouse", "Accessories", 29.99, 15, "Bluetooth ergonomic mouse", "assets/wirelessmouse.jpg")
]

cursor.executemany("""
INSERT INTO products (name, category, price, quantity, description, image_url)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE name = name
""", default_products)

# Finalize changes
conn.commit()
conn.close()
