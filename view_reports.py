import customtkinter as ctk
import subprocess
import sys
from database import get_db_connection
from tkinter import BOTH
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class ViewReportsApp(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email
        self.title("Reports - PES Surplus Store")
        self.geometry("1000x700")
        self.configure(fg_color="white")

        ctk.CTkLabel(self, text="📊 Reports Summary", font=("Arial", 20, "bold"),
                     text_color="#6B4E6D").pack(pady=20)

        self.users_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.products_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.orders_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.pending_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.revenue_label = ctk.CTkLabel(self, text="", font=("Arial", 14))

        self.users_label.pack(pady=5)
        self.products_label.pack(pady=5)
        self.orders_label.pack(pady=5)
        self.pending_label.pack(pady=5)
        self.revenue_label.pack(pady=5)

        ctk.CTkButton(self, text="⬅ Back", command=self.go_back).pack(pady=10)

        self.load_summary()
        self.plot_revenue_graph()

    def load_summary(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products")
        products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders")
        orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(p.price * o.quantity) FROM orders o JOIN products p ON o.product_id = p.product_id")
        revenue = cursor.fetchone()[0] or 0.0

        conn.close()

        self.users_label.configure(text=f"👥 Total Users: {users}")
        self.products_label.configure(text=f"🛍 Total Products: {products}")
        self.orders_label.configure(text=f"📦 Total Orders: {orders}")
        self.pending_label.configure(text=f"⏳ Pending Orders: {pending}")
        self.revenue_label.configure(text=f"💰 Total Revenue: ₹{revenue:.2f}")

    def plot_revenue_graph(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT o.order_id, p.price * o.quantity AS revenue
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            ORDER BY o.order_id ASC
        """)
        order_data = cursor.fetchall()
        conn.close()

        # Simulate days
        day_labels = []
        revenue_per_day = []

        if not order_data:
            return

        chunk_size = max(1, len(order_data) // 5)
        for i in range(0, len(order_data), chunk_size):
            chunk = order_data[i:i+chunk_size]
            day_num = len(day_labels) + 1
            day_labels.append(f"Day {day_num}")
            revenue_per_day.append(sum(row[1] for row in chunk))

        # Plot revenue only
        fig, ax = plt.subplots(figsize=(10, 4), dpi=100)
        fig.tight_layout(pad=4)

        ax.bar(day_labels, revenue_per_day, color="#725478")
        ax.set_title("Revenue Over Time (Simulated Days)")
        ax.set_ylabel("₹")
        ax.tick_params(axis='x', rotation=45)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=20, pady=20)

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "admin_dashboard.py", self.email])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = ViewReportsApp(email)
        app.mainloop()
    else:
        print("❌ ERROR: No admin email provided!")
