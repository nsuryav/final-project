# update_user_form.py

import customtkinter as ctk
from tkinter import messagebox
import sys
import subprocess
from database import get_db_connection

SIDEBAR_COLOR = "#6B4E6D"

class UpdateUserForm(ctk.CTk):
    def __init__(self, admin_email, user_id, first_name, last_name, email, role):
        super().__init__()
        self.title("Update User")
        self.geometry("400x550")
        self.configure(fg_color=SIDEBAR_COLOR)

        self.admin_email = admin_email
        self.user_id = user_id

        # Form variables
        self.first_name_var = ctk.StringVar(value=first_name)
        self.last_name_var = ctk.StringVar(value=last_name)
        self.email_var = ctk.StringVar(value=email)
        self.role_var = ctk.StringVar(value=role)

        self.build_form()

    def build_form(self):
        ctk.CTkLabel(self, text="Update User", font=("Arial", 18, "bold"), text_color="white").pack(pady=10)

        self.add_entry("First Name", self.first_name_var)
        self.add_entry("Last Name", self.last_name_var)
        self.add_entry("Email", self.email_var)

        ctk.CTkLabel(self, text="Role", text_color="white").pack(pady=(10, 2))
        ctk.CTkOptionMenu(self, values=["admin", "customer"], variable=self.role_var, width=300).pack()

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR)
        btn_frame.pack(pady=30)

        ctk.CTkButton(btn_frame, text="Update", command=self.update_user,
                      fg_color="white", text_color="black", width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Back", command=self.go_back,
                      fg_color="white", text_color="black", width=100).pack(side="left", padx=10)

    def add_entry(self, label_text, var):
        ctk.CTkLabel(self, text=label_text, text_color="white").pack(pady=(10, 2))
        ctk.CTkEntry(self, textvariable=var, width=300).pack()

    def update_user(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET FirstName=%s, LastName=%s, email=%s, role=%s WHERE user_id=%s
            """, (
                self.first_name_var.get(),
                self.last_name_var.get(),
                self.email_var.get(),
                self.role_var.get(),
                self.user_id
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User updated successfully.")
            self.go_back()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {e}")

    def go_back(self):
        self.destroy()
        subprocess.Popen(["python", "manage_users.py", self.admin_email])


# Run standalone
if __name__ == "__main__":
    if len(sys.argv) == 7:
        _, email, user_id, first_name, last_name, user_email, role = sys.argv
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = UpdateUserForm(email, int(user_id), first_name, last_name, user_email, role)
        app.mainloop()
    else:
        print("❌ ERROR: Missing arguments to open update user form!")
