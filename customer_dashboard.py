import json
import subprocess
import customtkinter as ctk
from tkinter import StringVar, IntVar
from PIL import Image
import sys
from database import get_db_connection

# ========== COLORS ==========
BG_COLOR = "#6B4E6D"
BUTTON_COLOR = "#FFFFFF"
TEXT_COLOR = "#322F77"
HIGHLIGHT_COLOR = "#6B4E6D"

class CustomerApp(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email
        self.cart = {}

        self.title("Customer Dashboard - PES Surplus Store")
        self.geometry("850x650")
        self.configure(fg_color=BG_COLOR)

        self.dashboard = CustomerDashboard(self)
        self.dashboard.pack(fill="both", expand=True)

class CustomerDashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.email = master.email
        self.cart = master.cart

        # Top Buttons (Logout & Track Orders)
        top_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        top_frame.pack(fill="x", pady=(10, 5), padx=20)

        ctk.CTkButton(top_frame, text="📦 Track Orders", width=130, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR,
                      command=self.track_orders).pack(side="left", padx=5)

        ctk.CTkButton(top_frame, text="🔒 Logout", width=100, fg_color=BUTTON_COLOR, text_color=TEXT_COLOR,
                      command=self.logout).pack(side="right", padx=5)

        # Welcome Label
        ctk.CTkLabel(self, text=f"Welcome, {self.email}", font=("Arial", 20, "bold"),
                     text_color="white").pack(pady=10)
        # Cart Button
        self.cart_count = IntVar(value=0)
        self.cart_button = ctk.CTkButton(self, text="🛒 Cart (0)", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR,
                                         command=self.go_to_cart)
        self.cart_button.pack(pady=5)

        # Product Display Area
        self.product_frame = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR, width=800, height=480)
        self.product_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self.product_frame.grid_columnconfigure(0, weight=1)
        self.product_frame.grid_columnconfigure(1, weight=1)

        self.load_products()
    def logout(self):
        self.master.destroy()  # ✅ Closes current window
        subprocess.Popen(["python", "login.py"])

    def track_orders(self):
        self.master.destroy()  # ✅ Closes current window
        subprocess.Popen(["python", "customer_orders.py", self.email])

    def load_products(self):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        self.products = cursor.fetchall()
        conn.close()
        self.display_products(self.products)

    def display_products(self, products):
        for widget in self.product_frame.winfo_children():
            widget.destroy()
        for index, product in enumerate(products):
            row = index // 2
            col = index % 2
            self.create_product_card(product, row, col)

    def create_product_card(self, product, row, col):
        frame = ctk.CTkFrame(self.product_frame, fg_color=BUTTON_COLOR, corner_radius=10, width=360, height=220)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="n")

        try:
            img = Image.open(product["image_url"]).resize((100, 100))
            img = ctk.CTkImage(light_image=img, size=(100, 100))
        except Exception as e:
            print(f"⚠️ Image load failed for {product['name']}: {e}")
            img = None

        ctk.CTkLabel(frame, image=img, text="").pack(side="left", padx=10, pady=10)
        details = f"{product['name']}\n💰 ${product['price']}\n📦 Stock: {product['quantity']}"
        ctk.CTkLabel(frame, text=details, font=("Arial", 12), text_color=TEXT_COLOR).pack(side="left", padx=10)

        button_frame = ctk.CTkFrame(frame, fg_color=BUTTON_COLOR)
        product_id = str(product["product_id"])
        quantity_var = IntVar(value=0)

        def update_ui():
            if quantity_var.get() == 0:
                add_button.pack(side="right", padx=10)
                button_frame.pack_forget()
            else:
                add_button.pack_forget()
                button_frame.pack(side="right", padx=10)
            self.update_cart(product_id, quantity_var.get())

        def increase(): quantity_var.set(quantity_var.get() + 1); update_ui()
        def decrease(): quantity_var.set(max(0, quantity_var.get() - 1)); update_ui()

        ctk.CTkButton(button_frame, text="➖", command=decrease, width=30).pack(side="left")
        ctk.CTkLabel(button_frame, textvariable=quantity_var).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="➕", command=increase, width=30).pack(side="left")

        add_button = ctk.CTkButton(frame, text="🛒 Add to Cart", fg_color=HIGHLIGHT_COLOR, text_color="white", command=increase)
        add_button.pack(side="right", padx=10)
        update_ui()

    def update_cart(self, product_id, quantity):
        if quantity > 0:
            self.cart[product_id] = quantity
        else:
            self.cart.pop(product_id, None)
        total_items = sum(self.cart.values())
        self.cart_count.set(total_items)
        self.cart_button.configure(text=f"🛒 Cart ({total_items})")

    def go_to_cart(self):
        try:
            with open("cart_session.txt", "r") as file:
                cart_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            cart_data = {}
        cart_data[self.email] = self.cart
        with open("cart_session.txt", "w") as file:
            json.dump(cart_data, file)
        self.master.destroy()
        subprocess.Popen(["python", "cart.py", self.email])


# Run App
if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = CustomerApp(user_email)
        app.mainloop()
    else:
        print("❌ ERROR: No user email provided!")
