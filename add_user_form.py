# add_user_form.py

import customtkinter as ctk
from tkinter import messagebox
from database import get_db_connection
import subprocess
import sys

SIDEBAR_COLOR = "#6B4E6D"

class AddUserForm(ctk.CTk):
    def __init__(self, admin_email):
        super().__init__()
        self.admin_email = admin_email
        self.title("Add New User")
        self.geometry("400x550")
        self.configure(fg_color=SIDEBAR_COLOR)

        # Variables
        self.email_var = ctk.StringVar()
        self.first_name = ctk.StringVar()
        self.last_name = ctk.StringVar()
        self.password = ctk.StringVar()
        self.confirm_password = ctk.StringVar()
        self.role = ctk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Add New User", font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

        self.add_entry("Email", self.email_var)
        self.add_entry("First Name", self.first_name)
        self.add_entry("Last Name", self.last_name)
        self.add_entry("Password", self.password, show="*")
        self.add_entry("Confirm Password", self.confirm_password, show="*")
        self.add_entry("Role", self.role)

        btn_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR)
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Add", command=self.submit_user, fg_color="white", text_color="black").grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="Back", command=self.go_back, fg_color="white", text_color="black").grid(row=0, column=1, padx=10)

    def add_entry(self, label_text, variable, show=None):
        ctk.CTkLabel(self, text=label_text, text_color="white").pack(pady=(10, 2))
        ctk.CTkEntry(self, textvariable=variable, show=show, width=300).pack()

    def submit_user(self):
        if not all([self.email_var.get(), self.first_name.get(), self.last_name.get(), self.password.get(), self.role.get()]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        if self.password.get() != self.confirm_password.get():
            messagebox.showerror("Error", "Passwords do not match.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (FirstName, LastName, email, password, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.first_name.get(),
                self.last_name.get(),
                self.email_var.get(),
                self.password.get(),
                self.role.get()
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User added successfully.")
            self.go_back()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {e}")

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "manage_users.py", self.admin_email])


# Run standalone
if __name__ == "__main__":
    if len(sys.argv) > 1:
        admin_email = sys.argv[1]
        ctk.set_appearance_mode("light")
        app = AddUserForm(admin_email)
        app.mainloop()
    else:
        print("❌ ERROR: No admin email provided!")
