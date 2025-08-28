import customtkinter as ctk
from tkinter import ttk, messagebox
import subprocess
import sys
from database import get_db_connection

class ManageProductsApp(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email
        self.title("Manage Products - PES Surplus Store")
        self.geometry("900x600")
        self.configure(fg_color="#6B4E6D")

        ctk.CTkLabel(self, text="🛍 All Products", font=("Arial", 20, "bold"), text_color="white").pack(pady=20)

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#6B4E6D")
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="➕ Add Product", command=self.add_product_popup,
                      fg_color="#4CAF50", text_color="white").pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="✏️ Update Selected", command=self.edit_product_popup,
                      fg_color="#2196F3", text_color="white").pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="⬅ Back", command=self.go_back,
                      fg_color="#9E9E9E", text_color="white").pack(side="left", padx=10)

        self.load_products()
        self.selected_product_id = None

    def on_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected)["values"]
            self.selected_product_id = values[0]

    def load_products(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT product_id, name, category, price, quantity FROM products")
        products = cursor.fetchall()
        conn.close()
        for p in products:
            self.tree.insert("", "end", values=(p["product_id"], p["name"], p["category"], p["price"], p["quantity"]))

    def add_product_popup(self):
        self.open_product_form(mode="add")

    def edit_product_popup(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product to update.")
            return

        values = self.tree.item(selected)["values"]
        product_data = {
            "product_id": values[0],
            "name": values[1],
            "category": values[2],
            "price": values[3],
            "quantity": values[4]
        }
        self.open_product_form(mode="edit", product=product_data)

    def open_product_form(self, mode="add", product=None):
        form = ctk.CTkToplevel(self)
        form.title("Add Product" if mode == "add" else "Update Product")
        form.geometry("400x500")
        form.configure(fg_color="#6B4E6D")

        name_var = ctk.StringVar(value=product["name"] if product else "")
        category_var = ctk.StringVar(value=product["category"] if product else "")
        price_var = ctk.StringVar(value=str(product["price"]) if product else "")
        qty_var = ctk.StringVar(value=str(product["quantity"]) if product else "")

        # Header
        ctk.CTkLabel(form, text="Add New Product" if mode == "add" else "Update Product",
                     font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

        # Input Fields
        def add_input(label, var):
            ctk.CTkLabel(form, text=label, text_color="white").pack(pady=(10, 2))
            ctk.CTkEntry(form, textvariable=var, width=300).pack()

        add_input("Name", name_var)
        add_input("Category", category_var)
        add_input("Price", price_var)
        add_input("Quantity", qty_var)

        # Buttons
        button_frame = ctk.CTkFrame(form, fg_color="#6B4E6D")
        button_frame.pack(pady=30)

        def submit():
            name = name_var.get()
            category = category_var.get()
            price = price_var.get()
            qty = qty_var.get()

            if not all([name, category, price, qty]):
                messagebox.showwarning("Validation", "All fields are required.")
                return

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                if mode == "add":
                    cursor.execute("""
                        INSERT INTO products (name, category, price, quantity)
                        VALUES (%s, %s, %s, %s)
                    """, (name, category, float(price), int(qty)))
                    messagebox.showinfo("Success", "Product added successfully.")
                else:
                    cursor.execute("""
                        UPDATE products SET name=%s, category=%s, price=%s, quantity=%s
                        WHERE product_id=%s
                    """, (name, category, float(price), int(qty), product["product_id"]))
                    messagebox.showinfo("Success", "Product updated successfully.")
                conn.commit()
                conn.close()
                form.destroy()
                self.load_products()
            except Exception as e:
                messagebox.showerror("Error", f"Database error: {e}")

        ctk.CTkButton(button_frame, text="Submit", command=submit,
                      fg_color="white", text_color="black", width=100).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Back", command=form.destroy,
                      fg_color="white", text_color="black", width=100).pack(side="left", padx=10)

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "admin_dashboard.py", self.email])


# Run
if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = ManageProductsApp(email)
        app.mainloop()
    else:
        print("❌ ERROR: No admin email provided!")
