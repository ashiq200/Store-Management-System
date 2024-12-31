import tkinter as tk
from tkinter import messagebox
import sqlite3


class StoreManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Store Management System")
        self.db_connection = sqlite3.connect("store_management.db")
        self.db_cursor = self.db_connection.cursor()

        # Create necessary tables if they don't exist
        self.create_tables()

        # Call the login screen initially
        self.login_screen()

    def create_tables(self):
        # Create Users table
        self.db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
        ''')

        # Create Products table
        self.db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT,
            price REAL,
            stock INTEGER
        )
        ''')

        # Create Cart table
        self.db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            username TEXT,
            product_id TEXT,
            quantity INTEGER,
            FOREIGN KEY(username) REFERENCES users(username),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
        ''')

        self.db_connection.commit()

    def login_screen(self):
        self.clear_frame()

        tk.Label(self.root, text="Login", font=("Arial", 16), fg="blue").pack(pady=10)
        tk.Label(self.root, text="Username:").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack()

        def authenticate():
            username = username_entry.get()
            password = password_entry.get()

            # Hardcoded admin credentials
            admin_username = "admin"
            admin_password = "admin123"

            if username == admin_username and password == admin_password:
                messagebox.showinfo("Login Successful", "Welcome, Admin!")
                self.main_screen(admin=True)
            else:
                self.db_cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                user = self.db_cursor.fetchone()
                if user:
                    messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                    self.current_username = username  # Store current username
                    self.main_screen(admin=False)
                else:
                    messagebox.showerror("Login Failed", "Invalid credentials!")

        def register_user():
            self.register_screen()

        tk.Button(self.root, text="Login", command=authenticate, bg="green", fg="white").pack(pady=10)
        tk.Button(self.root, text="Register", command=register_user, bg="orange", fg="white").pack(pady=5)

    def register_screen(self):
        self.clear_frame()

        tk.Label(self.root, text="Register", font=("Arial", 16), fg="blue").pack(pady=10)
        tk.Label(self.root, text="New Username:").pack()
        username_entry = tk.Entry(self.root)
        username_entry.pack()

        tk.Label(self.root, text="New Password:").pack()
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack()

        def register():
            username = username_entry.get()
            password = password_entry.get()

            if username and password:
                try:
                    self.db_cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    self.db_connection.commit()
                    messagebox.showinfo("Success", "Registration successful!")
                    self.login_screen()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showerror("Error", "Fields cannot be empty!")

        tk.Button(self.root, text="Register", command=register, bg="green", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.login_screen, bg="red", fg="white").pack()

    def main_screen(self, admin, username=None):
        self.clear_frame()

        tk.Label(self.root, text="Welcome to the Store", font=("Arial", 16), fg="blue").pack(pady=10)

        if admin:
            tk.Button(self.root, text="Add Product", command=self.add_product_screen, bg="green", fg="white", width=20).pack(pady=5)
            tk.Button(self.root, text="View Products", command=self.view_products_screen_admin, bg="blue", fg="white", width=20).pack(pady=5)
            tk.Button(self.root, text="Delete Product", command=self.delete_product_screen , bg="red", fg="white", width=20).pack(pady=5)
        else:
            tk.Button(self.root, text="View Products", command=self.view_products_screen_user, bg="blue", fg="white", width=20).pack(pady=5)
            tk.Button(self.root, text="View Cart", command=self.view_cart_screen, bg="orange", fg="white", width=20).pack(pady=5)
            tk.Button(self.root, text="Add to Cart", command=self.add_to_cart_screen, bg="green", fg="white", width=20).pack(pady=5)

        tk.Button(self.root, text="Logout", command=self.login_screen, bg="purple", fg="white", width=20).pack(pady=5)

    def add_to_cart_screen(self):
        self.clear_frame()

        tk.Label(self.root, text="Add to Cart", font=("Arial", 16), fg="blue").pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        product_id_entry = tk.Entry(self.root)
        product_id_entry.pack()

        tk.Label(self.root, text="Quantity:").pack()
        quantity_entry = tk.Entry(self.root)
        quantity_entry.pack()

        def calculate_total():
            product_id = product_id_entry.get()
            quantity = quantity_entry.get()

            if product_id and quantity.isdigit():
                self.db_cursor.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
                product = self.db_cursor.fetchone()
                if product:
                    total_price = product[0] * int(quantity)
                    messagebox.showinfo("Total Price", f"Total Price: ${total_price:.2f}")
                else:
                    messagebox.showerror("Error", "Product not found!")
            else:
                messagebox.showerror("Error", "Please enter valid Product ID and Quantity!")

        def add_to_cart():
            product_id = product_id_entry.get()
            quantity = quantity_entry.get()

            if product_id and quantity.isdigit():
                self.db_cursor.execute("SELECT stock FROM products WHERE product_id = ?", (product_id,))
                product = self.db_cursor.fetchone()
                if product and int(quantity) <= product[0]:
                    self.db_cursor.execute("INSERT INTO cart (username, product_id, quantity) VALUES (?, ?, ?)",
                                            (self.current_username, product_id, int(quantity)))
                    self.db_connection.commit()
                    messagebox.showinfo("Success", "Product added to cart!")
                else:
                    messagebox.showerror("Error", "Insufficient stock or product not found!")
            else:
                messagebox.showerror("Error", "Please enter valid Product ID and Quantity!")

        tk.Button(self.root, text="Calculate Total", command=calculate_total, bg="blue", fg="white").pack(pady=5)
        tk.Button(self.root, text="Add to Cart", command=add_to_cart, bg="green", fg="white").pack(pady=5)
        tk.Button(self.root, text="Back", command=lambda: self.main_screen(admin=False), bg="red", fg="white").pack()

    def add_product_screen(self):
        self.clear_frame()

        tk.Label(self.root, text="Add Product", font=("Arial", 16), fg="blue").pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        product_id_entry = tk.Entry(self.root)
        product_id_entry.pack()

        tk.Label(self.root, text="Product Name:").pack()
        product_name_entry = tk.Entry(self.root)
        product_name_entry.pack()

        tk.Label(self.root, text="Price:").pack()
        price_entry = tk.Entry(self.root)
        price_entry.pack()

        tk.Label(self.root, text="Stock:").pack()
        stock_entry = tk.Entry(self.root)
        stock_entry.pack()

        def add_product():
            product_id = product_id_entry.get()
            product_name = product_name_entry.get()
            price = price_entry.get()
            stock = stock_entry.get()

            if product_id and product_name and price and stock:
                try:
                    self.db_cursor.execute("INSERT INTO products (product_id, name, price, stock) VALUES (?, ?, ?, ?)",
                                            (product_id, product_name, float(price), int(stock)))
                    self.db_connection.commit()
                    messagebox.showinfo("Success", "Product added successfully!")
                    self.main_screen(admin=True)
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Product ID already exists!")
            else:
                messagebox.showerror("Error", "All fields are required!")

        tk.Button(self.root, text="Add Product", command=add_product, bg="green", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=lambda: self.main_screen(admin=True), bg="red", fg="white").pack()

    def delete_product_screen(self):
        self.clear_frame()

        tk.Label(self.root, text="Delete Product", font=("Arial", 16), fg="blue").pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        product_id_entry = tk.Entry(self.root)
        product_id_entry.pack()

        def delete_product():
            product_id = product_id_entry.get()

            if product_id:
                self.db_cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
                if self.db_cursor.rowcount == 0:
                    messagebox.showerror("Error", "Product not found!")
                else:
                    self.db_connection.commit()
                    messagebox.showinfo("Success", "Product deleted successfully!")
            else:
                messagebox.showerror("Error", "Product ID cannot be empty!")

        tk.Button(self.root, text="Delete Product", command=delete_product, bg="red", fg="white").pack(pady=10)
        tk.Button(self.root, text="Back", command=lambda: self.main_screen(admin=True), bg="orange", fg="white").pack()

    def view_products_screen_admin(self):
        self.clear_frame()

        tk.Label(self.root, text="Products List", font=("Arial", 16), fg="blue").pack(pady=10)

        self.db_cursor.execute("SELECT * FROM products")
        products = self.db_cursor.fetchall()

        for product in products:
            tk.Label(self.root, text=f"ID: {product[0]}, Name: {product[1]}, Price: ${product[2]:.2f}, Stock: {product[3]}").pack()

        tk.Button(self.root, text="Back", command=lambda: self.main_screen(admin=True), bg="red", fg="white").pack()

    def view_products_screen_user(self):
        self.clear_frame()

        tk.Label(self.root, text="Products List", font=("Arial", 16), fg="blue").pack(pady=10)

        self.db_cursor.execute("SELECT * FROM products")
        products = self.db_cursor.fetchall()

        for product in products:
            tk.Label(self.root, text=f"ID: {product[0]}, Name: {product[1]}, Price: ${product[2]:.2f}, Stock: {product[3]}").pack()

        tk.Button(self.root, text="Back", command=lambda: self.main_screen(admin=False), bg="red", fg="white").pack()

    def view_cart_screen(self):
        self.clear_frame()

        tk.Label(self.root, text="Your Cart", font=("Arial", 16), fg="blue").pack(pady=10)

        self.db_cursor.execute("SELECT * FROM cart WHERE username = ?", (self.current_username,))
        cart_items = self.db_cursor.fetchall()

        total_bill = 0

        if cart_items:
            for item in cart_items:
                self.db_cursor.execute("SELECT * FROM products WHERE product_id = ?", (item[1],))
                product = self.db_cursor.fetchone()
                subtotal = product[2] * item[2]  # Price * Quantity
                total_bill += subtotal
                tk.Label(self.root, text=f"Product: {product[1]}, Quantity: {item[2]}, Subtotal: ${subtotal:.2f}").pack()

            tk.Label(self.root, text=f"Total Bill: ${total_bill:.2f}", font=("Arial", 14, "bold")).pack()
        else:
            tk.Label(self.root, text="Your cart is empty.").pack()

        tk.Button(self.root, text="Back", command=lambda: self.main_screen(admin=False), bg="red", fg="white").pack()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = StoreManagementApp(root)
    app.run()
