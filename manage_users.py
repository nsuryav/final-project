import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import subprocess
from database import get_db_connection

SIDEBAR_COLOR = "#6B4E6D"
MAIN_BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#322F77"

class ManageUsersApp(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.admin_email = email
        self.title("Manage Users - PES Surplus Store")
        self.geometry("850x550")
        self.configure(fg_color=MAIN_BG_COLOR)

        # Form variables
        self.first_name = ctk.StringVar()
        self.last_name = ctk.StringVar()
        self.email_var = ctk.StringVar()
        self.password = ctk.StringVar()
        self.role = ctk.StringVar(value="customer")

        self.create_layout()
        self.load_users()

    def create_layout(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, fg_color=SIDEBAR_COLOR, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="👤 Users", font=("Arial", 16, "bold"), text_color="white").pack(pady=(30, 20))

        ctk.CTkButton(sidebar, text="➕ Add User", fg_color="white", text_color=SIDEBAR_COLOR,
                      command=self.show_add_user_form).pack(pady=10)

        ctk.CTkButton(sidebar, text="⬅ Back", fg_color="#9E9E9E", text_color="white",
                      command=self.go_back).pack(side="bottom", pady=20)

        # Main area
        main_area = ctk.CTkFrame(self, fg_color=MAIN_BG_COLOR)
        main_area.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main_area, text="All Users", font=("Arial", 20, "bold"), text_color=TEXT_COLOR).pack(pady=(0, 10))

        self.tree = ttk.Treeview(main_area, columns=("ID", "First Name", "Last Name", "Email", "Role"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.fill_form_from_selection)

        ctk.CTkButton(main_area, text="✏️ Update Selected User", fg_color="#2196F3", text_color="white",
                      command=self.update_user).pack(pady=10)

    def load_users(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, FirstName, LastName, email, role FROM users")
        users = cursor.fetchall()
        conn.close()
        for user in users:
            self.tree.insert("", "end", values=(user["user_id"], user["FirstName"], user["LastName"], user["email"], user["role"]))

    def show_add_user_form(self):
        self.destroy()
        subprocess.Popen(["python", "add_user_form.py", self.admin_email])

    def update_user(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select User", "Please select a user to update.")
            return

        values = self.tree.item(selected)["values"]
        user_id, first_name, last_name, email, role = values

        self.destroy()
        subprocess.Popen([
            "python", "update_user_form.py", self.admin_email,
            str(user_id), first_name, last_name, email, role
        ])

    def fill_form_from_selection(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected)["values"]
            self.first_name.set(values[1])
            self.last_name.set(values[2])
            self.email_var.set(values[3])
            self.role.set(values[4])

    def clear_form(self):
        self.first_name.set("")
        self.last_name.set("")
        self.email_var.set("")
        self.password.set("")
        self.role.set("customer")

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "admin_dashboard.py", self.admin_email])


# Run the app
if __name__ == "__main__":
    if len(sys.argv) > 1:
        admin_email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = ManageUsersApp(admin_email)
        app.mainloop()
    else:
        print("❌ ERROR: No admin email provided!")
