import customtkinter as ctk
import mysql.connector
import subprocess
from tkinter import messagebox

# Set up window appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

# Initialize SignUp Window
signup_window = ctk.CTk()
signup_window.title("Sign Up - PES Surplus Store")
signup_window.geometry("400x500")
signup_window.resizable(False, False)

# Database Connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="PES_Surplus_Store"
    )

# Function to register user
def register_user():
    first_name = first_name_entry.get().strip()
    last_name = last_name_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    # Validation: Check if any field is empty
    if not first_name or not last_name or not email or not password:
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (FirstName, LastName, email, password, role) 
            VALUES (%s, %s, %s, %s, 'customer')
        """, (first_name, last_name, email, password))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Account created successfully!")
        signup_window.destroy()
        subprocess.run(["python", "login.py"])

    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Email already exists. Try another.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Function to toggle password visibility
def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")
    else:
        password_entry.configure(show="*")

# UI Layout
frame = ctk.CTkFrame(signup_window, width=380, height=480, fg_color="white", corner_radius=15)
frame.place(x=10, y=10)

title_label = ctk.CTkLabel(frame, text="Create an Account", font=("Arial", 18, "bold"), text_color="black")
title_label.place(x=100, y=20)

# First Name
first_name_label = ctk.CTkLabel(frame, text="First Name", font=("Arial", 12), text_color="black")
first_name_label.place(x=20, y=70)

first_name_entry = ctk.CTkEntry(frame, width=320, height=30, corner_radius=8, placeholder_text="Enter your first name")
first_name_entry.place(x=20, y=95)

# Last Name
last_name_label = ctk.CTkLabel(frame, text="Last Name", font=("Arial", 12), text_color="black")
last_name_label.place(x=20, y=130)

last_name_entry = ctk.CTkEntry(frame, width=320, height=30, corner_radius=8, placeholder_text="Enter your last name")
last_name_entry.place(x=20, y=155)

# Email
email_label = ctk.CTkLabel(frame, text="Email", font=("Arial", 12), text_color="black")
email_label.place(x=20, y=190)

email_entry = ctk.CTkEntry(frame, width=320, height=30, corner_radius=8, placeholder_text="Enter your email")
email_entry.place(x=20, y=215)

# Password
password_label = ctk.CTkLabel(frame, text="Password", font=("Arial", 12), text_color="black")
password_label.place(x=20, y=250)

password_entry = ctk.CTkEntry(frame, width=320, height=30, show="*", corner_radius=8, placeholder_text="Enter your password")
password_entry.place(x=20, y=275)

# Show Password Checkbox
show_password_var = ctk.BooleanVar()
show_password_check = ctk.CTkCheckBox(frame, text="Show Password", variable=show_password_var, 
                                      command=toggle_password, text_color="black")
show_password_check.place(x=20, y=310)

# Signup Button
signup_button = ctk.CTkButton(frame, text="Sign Up", width=320, height=35, 
                              font=("Arial", 14, "bold"), fg_color="#6B4E6D",
                              text_color="white", corner_radius=10,
                              hover_color="#A386C6", command=register_user)
signup_button.place(x=20, y=350)

# Back to Login
def open_login():
    signup_window.destroy()
    subprocess.run(["python", "login.py"])

login_label = ctk.CTkLabel(frame, text="Already have an account?", text_color="black", font=("Arial", 11))
login_label.place(x=20, y=400)

login_button = ctk.CTkButton(frame, text="Login →", width=100, height=30,
                             font=("Arial", 12, "bold"), fg_color="#A386C6",
                             text_color="white", corner_radius=10,
                             hover_color="#6B4E6D", command=open_login)
login_button.place(x=200, y=395)

# Run the SignUp Window
signup_window.mainloop()
