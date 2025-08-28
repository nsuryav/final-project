import customtkinter as ctk
import subprocess
from PIL import Image, ImageTk, ImageDraw

# Initialize main window
ctk.set_appearance_mode("light")  # Light mode
ctk.set_default_color_theme("dark-blue")  # Dark blue theme

root = ctk.CTk()
root.title("PES Surplus Store")
root.geometry("900x550")
root.resizable(False, False)  # Disable window resizing

# Left-side frame with dark purple background
left_frame = ctk.CTkFrame(root, width=400, height=550, fg_color="#6B4E6D", corner_radius=20)
left_frame.pack(side="left", fill="y")

# Heading label
title_label = ctk.CTkLabel(left_frame, text="Welcome to PES Surplus Store",
                           font=("Arial", 18, "bold"), text_color="white")
title_label.place(x=50, y=50)

# Description label
desc_label = ctk.CTkLabel(left_frame, text="PES Surplus Store is a digital marketplace for\n"
                                           "buying and selling university surplus items\n"
                                           "like electronics, furniture, and equipment.\n"
                                           "Easily browse available products, make\n"
                                           "purchases, and schedule pickups.",
                          font=("Arial", 14), text_color="white", justify="left")
desc_label.place(x=50, y=100)

# Function to navigate to Login
def open_login():
    root.destroy()
    subprocess.run(["python", "login.py"])

# Function to navigate to Signup
def open_signup():
    root.destroy()
    subprocess.run(["python", "signup.py"])

# Custom Buttons with Arrows
login_button = ctk.CTkButton(left_frame, text="Login →", width=200, height=40,
                             font=("Arial", 14), fg_color="white",
                             text_color="black", hover_color="#d1c4e9",
                             corner_radius=20, command=open_login)
login_button.place(x=100, y=300)

signup_button = ctk.CTkButton(left_frame, text="SignUp →", width=200, height=40,
                              font=("Arial", 14), fg_color="white",
                              text_color="black", hover_color="#d1c4e9",
                              corner_radius=20, command=open_signup)
signup_button.place(x=100, y=360)

# Function to make the image circular
def make_round_image(image_path, size=(400, 500)):
    img = Image.open(image_path).resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

# Load and display a rounded image on the right side
try:
    round_img = make_round_image("assets/home.png", size=(420, 520))
    img_tk = ImageTk.PhotoImage(round_img)
    image_label = ctk.CTkLabel(root, image=img_tk, text="")
    image_label.place(x=480, y=50)
except Exception as e:
    print("Image not found. Ensure 'shopping_image.png' exists in the directory.")

# Run the application
root.mainloop()
