import json
import customtkinter as ctk
import subprocess
import sys
from database import get_db_connection

# ========== COLOR SCHEME ==========
BG_COLOR = "#6B4E6D"
BUTTON_COLOR = "#FFFFFF"
TEXT_COLOR = "#322F77"
HIGHLIGHT_COLOR = "#4F46E5"

class Cart(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email
        self.title("Your Cart")
        self.geometry("600x500")
        self.configure(fg_color=BG_COLOR)
        self.cart_items = self.load_cart()

        ctk.CTkLabel(self, text="🛒 Your Cart", font=("Arial", 20, "bold"), text_color="white").pack(pady=10)
        self.cart_frame = ctk.CTkScrollableFrame(self, fg_color=BG_COLOR)
        self.cart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.footer_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.footer_frame.pack(fill="x", padx=20, pady=10)

        self.total_price_label = ctk.CTkLabel(self.footer_frame, text="Total: $0.00", font=("Arial", 16, "bold"),
                                              text_color="white")
        self.total_price_label.pack(side="left", padx=10)

        ctk.CTkButton(self.footer_frame, text="⬅ Back", fg_color=BUTTON_COLOR, text_color=TEXT_COLOR,
                      command=self.go_back).pack(side="left", padx=10)

        ctk.CTkButton(self.footer_frame, text="✅ Place Order", fg_color=HIGHLIGHT_COLOR, text_color="white",
                      command=self.place_order).pack(side="right", padx=10)

        self.update_cart_ui()

    def load_cart(self):
        try:
            with open("cart_session.txt", "r") as file:
                data = json.load(file)
                return {str(k): int(v) for k, v in data.get(self.email, {}).items()}
        except Exception as e:
            print(f"[ERROR] Failed to load cart: {e}")
            return {}

    def update_cart_ui(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        if not self.cart_items:
            ctk.CTkLabel(self.cart_frame, text="🛒 Your cart is empty!", text_color="white").pack(pady=10)
            self.total_price_label.configure(text="Total: $0.00")
            return

        total_price = 0
        for product_id, qty in self.cart_items.items():
            info = self.get_product_info(product_id)
            if not info:
                continue
            name, price = info
            total_price += price * qty

            frame = ctk.CTkFrame(self.cart_frame, fg_color=BUTTON_COLOR)
            frame.pack(fill="x", pady=5, padx=10)

            text = f"{name}\n💰 ${price:.2f} x {qty} = ${price * qty:.2f}"
            ctk.CTkLabel(frame, text=text, text_color=TEXT_COLOR).pack(side="left", padx=10)

        self.total_price_label.configure(text=f"Total: ${total_price:.2f}")

    def get_product_info(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, price FROM products WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        conn.close()
        return (result["name"], result["price"]) if result else None

    def place_order(self):
        if not self.cart_items:
            ctk.CTkLabel(self.cart_frame, text="⚠️ Cart is empty!", text_color="red").pack(pady=10)
            return

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user_id from email
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email) = %s", (self.email.lower(),))
        user = cursor.fetchone()

        if not user:
            ctk.CTkLabel(self.cart_frame, text="❌ Error: User not found!", text_color="red").pack(pady=10)
            conn.close()
            return

        user_id = user["user_id"]

        # Build product summary
        product_names = []
        for product_id, quantity in self.cart_items.items():
            cursor.execute("SELECT name FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            if product:
                product_names.append(f"{quantity}x {product['name']}")

        product_summary = ", ".join(product_names)

        # Insert orders and update product quantities
        for product_id, quantity in self.cart_items.items():
            # Check stock availability
            cursor.execute("SELECT quantity FROM products WHERE product_id = %s", (product_id,))
            product_row = cursor.fetchone()
            if not product_row or product_row["quantity"] < quantity:
                ctk.CTkLabel(self.cart_frame, text=f"❌ Not enough stock for product {product_id}!", text_color="red").pack(pady=10)
                conn.rollback()
                conn.close()
                return

            # Insert order
            cursor.execute("""
                INSERT INTO orders (user_id, product_id, quantity, products, status)
                VALUES (%s, %s, %s, %s, 'Pending')
            """, (user_id, product_id, quantity, product_summary))

            # Update stock
            cursor.execute("""
                UPDATE products SET quantity = quantity - %s WHERE product_id = %s
            """, (quantity, product_id))

        conn.commit()
        conn.close()

        # Clear cart session
        try:
            with open("cart_session.txt", "r") as file:
                data = json.load(file)
            data[self.email] = {}
            with open("cart_session.txt", "w") as file:
                json.dump(data, file)
        except Exception as e:
            print(f"[ERROR] Clearing cart: {e}")

        # Show success message and go back
        ctk.CTkLabel(self.cart_frame, text="✅ Order Placed Successfully!\nRedirecting...", text_color="green").pack(pady=10)
        self.after(1500, self.go_back)

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "customer_dashboard.py", self.email])


# Run App
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = Cart(sys.argv[1])
        app.mainloop()
    else:
        print("❌ ERROR: No email provided!")
