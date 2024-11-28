import sqlite3
from datetime import datetime

def create_database():
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            stock_quantity INTEGER NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # Create Order_Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            price_at_time DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    # Insert sample products
    sample_products = [
        ('Hammer', 'Standard claw hammer', 19.99, 50, 'Tools'),
        ('Screwdriver Set', 'Set of 6 screwdrivers', 24.99, 30, 'Tools'),
        ('Paint Brush', 'High-quality paint brush', 9.99, 100, 'Painting'),
        ('Wood Screws', 'Box of 100 wood screws', 8.99, 200, 'Hardware'),
        ('Power Drill', 'Cordless power drill', 129.99, 20, 'Power Tools')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO products (name, description, price, stock_quantity, category)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_products)

    conn.commit()
    conn.close()

def register_user():
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()
    
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        email = input("Enter email: ")
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', (username, password, email))
            conn.commit()
            print("Registration successful!")
            break
        except sqlite3.IntegrityError:
            print("Username or email already exists. Please try again.")
    
    conn.close()

def login():
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()
    
    while True:
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        cursor.execute('''
            SELECT user_id FROM users
            WHERE username = ? AND password = ?
        ''', (username, password))
        
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            conn.close()
            return user[0]
        else:
            print("Invalid credentials. Please try again.")
            retry = input("Try again? (y/n): ")
            if retry.lower() != 'y':
                conn.close()
                return None

def display_products():
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM products
    ''')
    
    products = cursor.fetchall()
    print("\nAvailable Products:")
    print("ID | Name | Description | Price | Stock | Category")
    print("-" * 60)
    for product in products:
        print(f"{product[0]} | {product[1]} | {product[2]} | ${product[3]} | {product[4]} | {product[5]}")
    
    conn.close()

def place_order(user_id):
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()
    
    cart = []
    total_amount = 0
    
    while True:
        display_products()
        product_id = input("\nEnter product ID to add to cart (or 'done' to finish): ")
        
        if product_id.lower() == 'done':
            break
            
        try:
            product_id = int(product_id)
            quantity = int(input("Enter quantity: "))
            
            cursor.execute('''
                SELECT price, stock_quantity FROM products
                WHERE product_id = ?
            ''', (product_id,))
            
            product = cursor.fetchone()
            if product and product[1] >= quantity:
                cart.append((product_id, quantity, product[0]))
                total_amount += product[0] * quantity
                print(f"Added to cart. Current total: ${total_amount:.2f}")
            else:
                print("Invalid product ID or insufficient stock.")
        except ValueError:
            print("Please enter valid numbers.")
    
    if cart:
        cursor.execute('''
            INSERT INTO orders (user_id, total_amount)
            VALUES (?, ?)
        ''', (user_id, total_amount))
        
        order_id = cursor.lastrowid
        
        for product_id, quantity, price in cart:
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price_at_time)
                VALUES (?, ?, ?, ?)
            ''', (order_id, product_id, quantity, price))
            
            cursor.execute('''
                UPDATE products
                SET stock_quantity = stock_quantity - ?
                WHERE product_id = ?
            ''', (quantity, product_id))
        
        conn.commit()
        print(f"\nOrder placed successfully! Total amount: ${total_amount:.2f}")
    
    conn.close()

def view_orders(user_id):
    conn = sqlite3.connect('hardware_store.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT order_id, order_date, total_amount, status
        FROM orders
        WHERE user_id = ?
        ORDER BY order_date DESC
    ''', (user_id,))
    
    orders = cursor.fetchall()
    if orders:
        print("\nYour Orders:")
        print("Order ID | Date | Total Amount | Status")
        print("-" * 50)
        for order in orders:
            print(f"{order[0]} | {order[1]} | ${order[2]} | {order[3]}")
            
            cursor.execute('''
                SELECT p.name, oi.quantity, oi.price_at_time
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = ?
            ''', (order[0],))
            
            items = cursor.fetchall()
            print("\nItems:")
            for item in items:
                print(f"- {item[0]}: {item[1]} x ${item[2]}")
            print()
    else:
        print("\nNo orders found.")
    
    conn.close()

def main_menu():
    create_database()
    user_id = None
    
    while True:
        if user_id is None:
            print("\n=== Hardware Store Menu ===")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == '1':
                register_user()
            elif choice == '2':
                user_id = login()
            elif choice == '3':
                print("Thank you for visiting! Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        else:
            print("\n=== Hardware Store Menu ===")
            print("1. View Products")
            print("2. Place Order")
            print("3. View My Orders")
            print("4. Logout")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                display_products()
            elif choice == '2':
                place_order(user_id)
            elif choice == '3':
                view_orders(user_id)
            elif choice == '4':
                user_id = None
                print("Logged out successfully!")
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
