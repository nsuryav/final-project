import customtkinter as ctk
import mysql.connector
import subprocess
import sys
from tkinter import ttk
from database import get_db_connection

# ========== COLORS ==========
BG_COLOR = "#6B4E6D"
BUTTON_COLOR = "#FFFFFF"
TEXT_COLOR = "#6B4E6D"

class OrderTracker(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email
        self.user_id = self.get_user_id_from_email(email)  # ✅ Get user_id based on email

        self.title("Your Orders - PES Surplus Store")
        self.geometry("700x450")
        self.configure(fg_color=BG_COLOR)

        # ========== HEADER ==========
        ctk.CTkLabel(self, text="📦 Your Order History", font=("Arial", 20, "bold"),
                     text_color="white").pack(pady=15)

        # ========== TABLE ==========
        self.tree = ttk.Treeview(self, columns=("Order ID", "Product", "Quantity", "Status"), show="headings")
        self.tree.heading("Order ID", text="Order ID")
        self.tree.heading("Product", text="Product")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # ========== BACK BUTTON ==========
        ctk.CTkButton(self, text="⬅ Back", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR,
                      width=100, command=self.go_back).pack(pady=10)

        self.load_orders()

    def get_user_id_from_email(self, email):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return result['user_id']
            else:
                raise ValueError("User with email not found.")
        except Exception as e:
            print(f"❌ Error fetching user_id from email: {e}")
            self.tree.insert("", "end", values=("Error fetching user info", "", "", ""))
            return None

    def load_orders(self):
        if not self.user_id:
            return  # Stop if user_id could not be fetched

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT o.order_id, p.name AS product_name, o.quantity, o.status
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.user_id = %s
                ORDER BY o.order_id DESC
            """
            cursor.execute(query, (self.user_id,))
            orders = cursor.fetchall()
            conn.close()

            print("✅ Fetched Orders:", orders)  # ✅ Debug print to console

            if not orders:
                self.tree.insert("", "end", values=("No orders yet", "", "", ""))
            else:
                for order in orders:
                    self.tree.insert("", "end", values=(
                        order["order_id"],
                        order["product_name"],
                        order["quantity"],
                        order["status"]
                    ))

        except Exception as e:
            print(f"❌ Error loading orders: {e}")
            self.tree.insert("", "end", values=("Error fetching orders", "", "", ""))

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "customer_dashboard.py", self.email])  # Pass back email


# ✅ RUN
if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = OrderTracker(email)
        app.mainloop()
    else:
        print("❌ ERROR: No email provided!")
