from tkinter import messagebox
import customtkinter as ctk
import subprocess
from PIL import Image, ImageTk, ImageDraw
from database import get_db_connection 


# Initialize the Login Window
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("Login - PES Surplus Store")
root.geometry("800x450")
root.resizable(False, False)

# Create Main Frame with Dark Purple Background
main_frame = ctk.CTkFrame(root, width=800, height=450, fg_color="#6B4E6D")
main_frame.place(x=0, y=0)

# Function to reshape and mask the image (Rounded Effect)
def make_round_image(image_path, size=(350, 350)):
    img = Image.open(image_path).resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

# Load and display a rounded image on the left side
try:
    round_img = make_round_image("assets/login.png", size=(350, 350))  # Change the file name as needed
    img_tk = ImageTk.PhotoImage(round_img)
    image_label = ctk.CTkLabel(main_frame, image=img_tk, text="")
    image_label.place(x=50, y=85)
except Exception as e:
    print("Image not found. Ensure 'secure_login.png' exists in the directory.")

# Right Login Frame (White Background)
login_frame = ctk.CTkFrame(main_frame, width=340, height=380, fg_color="white", corner_radius=15)
login_frame.place(x=420, y=35)

# Login Title
title_label = ctk.CTkLabel(login_frame, text="Please, Login", font=("Arial", 18, "bold"), text_color="black")
title_label.place(x=120, y=20)

# Email Label & Entry
email_label = ctk.CTkLabel(login_frame, text="📧 Email", font=("Arial", 12), text_color="black")
email_label.place(x=20, y=70)

email_entry = ctk.CTkEntry(login_frame, width=280, height=30, corner_radius=8, placeholder_text="Enter your email")
email_entry.place(x=20, y=95)

# Password Label & Entry
password_label = ctk.CTkLabel(login_frame, text="🔒 Password", font=("Arial", 12), text_color="black")
password_label.place(x=20, y=135)

password_entry = ctk.CTkEntry(login_frame, width=280, height=30, show="*", corner_radius=8, placeholder_text="Enter your password")
password_entry.place(x=20, y=160)

# Function to toggle password visibility
def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")
    else:
        password_entry.configure(show="*")

# Show Password Checkbox
show_password_var = ctk.BooleanVar()
show_password_check = ctk.CTkCheckBox(login_frame, text="Show Password", variable=show_password_var, 
                                      command=toggle_password, text_color="black")
show_password_check.place(x=20, y=200)

# Forgot Password Label (Clickable)
forgot_password = ctk.CTkLabel(login_frame, text="Forgot password?", text_color="blue", cursor="hand2")
forgot_password.place(x=220, y=200)

# Function to handle login (Placeholder)
from database import get_db_connection  # Make sure this import is at the top

def login():
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if not email or not password:
        messagebox.showerror("Error", "Please enter your email and password!")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Case-insensitive email match
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = %s AND password = %s", (email.lower(), password))
        user = cursor.fetchone()

        conn.close()

        if user:
            # ✅ Valid login — proceed to dashboard
            role = user.get("role", "customer")

            root.destroy()
            if role == "admin":
                subprocess.run(["python", "admin_dashboard.py", email])  # optional if you have admin flow
            else:
                subprocess.run(["python", "customer_dashboard.py", email])
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    except Exception as e:
        messagebox.showerror("Database Error", f"Something went wrong!\n{e}")


# Login Button
login_button = ctk.CTkButton(login_frame, text="Login", width=280, height=35, 
                             font=("Arial", 14, "bold"), fg_color="#6B4E6D",
                             text_color="white", corner_radius=10,
                             hover_color="#A386C6", command=login)
login_button.place(x=20, y=240)

# Navigate to SignUp
def open_signup():
    root.destroy()
    subprocess.run(["python", "signup.py"])

# SignUp Label & Button
signup_label = ctk.CTkLabel(login_frame, text="New User Signup Here", text_color="black", font=("Arial", 11))
signup_label.place(x=20, y=290)

signup_button = ctk.CTkButton(login_frame, text="SignUp →", width=100, height=30,
                              font=("Arial", 12, "bold"), fg_color="#A386C6",
                              text_color="white", corner_radius=10,
                              hover_color="#6B4E6D", command=open_signup)
signup_button.place(x=200, y=285)

# Run Application
root.mainloop()
