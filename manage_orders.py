import customtkinter as ctk
from tkinter import ttk, messagebox
import subprocess
import sys
from database import get_db_connection

class ManageOrdersApp(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email
        self.title("Manage Orders - PES Surplus Store")
        self.geometry("850x600")
        self.configure(fg_color="#6B4E6D")

        ctk.CTkLabel(self, text="📦 All Orders", font=("Arial", 20, "bold"), text_color="white").pack(pady=20)

        self.tree = ttk.Treeview(
            self,
            columns=("Order ID", "Customer", "Product", "Qty", "Status"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#6B4E6D")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="✏️ Edit Selected Order", command=self.edit_order,
                      fg_color="#2196F3", text_color="white").pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="⬅ Back", width=100, command=self.go_back).pack(side="left", padx=10)

        self.load_orders()

    def load_orders(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                o.order_id,
                CONCAT(u.FirstName, ' ', u.LastName) AS customer_name,
                p.name AS product_name,
                o.quantity,
                o.status
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN products p ON o.product_id = p.product_id
            ORDER BY o.order_id DESC
        """)

        orders = cursor.fetchall()
        conn.close()
        for order in orders:
            self.tree.insert("", "end", values=(
                order["order_id"],
                order["customer_name"],
                order["product_name"],
                order["quantity"],
                order["status"]
            ))

    def edit_order(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Please select an order to edit.")
            return

        values = self.tree.item(selected)["values"]
        order_id, customer_name, product_name, quantity, status = values

        popup = ctk.CTkToplevel(self)
        popup.title("Edit Order")
        popup.geometry("400x400")
        popup.configure(fg_color="#6B4E6D")

        quantity_var = ctk.IntVar(value=quantity)
        status_var = ctk.StringVar(value=status)

        ctk.CTkLabel(popup, text="Edit Order", font=("Arial", 18, "bold"), text_color="white").pack(pady=10)
        ctk.CTkLabel(popup, text=f"Order ID: {order_id}", font=("Arial", 14), text_color="white").pack(pady=(0, 5))
        ctk.CTkLabel(popup, text=f"Customer: {customer_name}", text_color="white").pack(pady=5)
        ctk.CTkLabel(popup, text=f"Product: {product_name}", text_color="white").pack(pady=5)

        ctk.CTkLabel(popup, text="Quantity", text_color="white").pack(pady=(15, 2))
        ctk.CTkEntry(popup, textvariable=quantity_var, width=300).pack()

        ctk.CTkLabel(popup, text="Status", text_color="white").pack(pady=(10, 2))
        ctk.CTkOptionMenu(popup, values=["Pending", "Approved", "Rejected"],
                          variable=status_var, width=300).pack()

        def save_changes():
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE orders SET quantity=%s, status=%s WHERE order_id=%s
                """, (quantity_var.get(), status_var.get(), order_id))
                conn.commit()
                conn.close()
                self.load_orders()
                popup.destroy()
                messagebox.showinfo("Success", "Order updated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update order: {e}")

        ctk.CTkButton(popup, text="Save Changes", command=save_changes,
                      fg_color="white", text_color="black").pack(pady=20)

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "admin_dashboard.py", self.email])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = ManageOrdersApp(email)
        app.mainloop()
    else:
        print("❌ ERROR: No admin email provided!")
