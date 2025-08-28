import customtkinter as ctk
import subprocess
import sys
from PIL import Image
from database import get_db_connection

# ========== COLORS ==========
SIDEBAR_COLOR = "#6B4E6D"
MAIN_BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#FFFFFF"
BUTTON_BG = "#6B4E6D"

class AdminApp(ctk.CTk):
    def __init__(self, email):
        super().__init__()
        self.email = email

        self.title("Admin Dashboard - PES Surplus Store")
        self.geometry("850x550")
        self.configure(fg_color=MAIN_BG_COLOR)

        self.dashboard = AdminDashboard(self)
        self.dashboard.pack(fill="both", expand=True)

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=MAIN_BG_COLOR)
        self.master = master
        self.email = master.email

        # ========== Sidebar ==========
        sidebar = ctk.CTkFrame(self, width=200, fg_color=SIDEBAR_COLOR, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(sidebar, text="Admin Panel", font=("Arial", 18, "bold"), text_color="white").pack(pady=(30, 10))
        ctk.CTkLabel(sidebar, text=self.email, font=("Arial", 12), text_color="white").pack(pady=(0, 30))

        ctk.CTkButton(sidebar, text="🔒 Logout", fg_color="white", text_color=SIDEBAR_COLOR,
              command=self.logout).pack(side="bottom", pady=20)

        # ========== Main Area ==========
        main_area = ctk.CTkFrame(self, fg_color=MAIN_BG_COLOR)
        main_area.pack(side="left", fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(main_area, text="Welcome Admin!", font=("Arial", 20, "bold"),
                     text_color=BUTTON_BG).pack(pady=(0, 20))

        # Load icons
        user_icon = self.load_icon("assets/user.png")
        order_icon = self.load_icon("assets/order.png")
        product_icon = self.load_icon("assets/product.png")
        report_icon = self.load_icon("assets/report.png")  # 📊 Add report icon

        # Buttons with images
        ctk.CTkButton(main_area, text="  Manage Users", image=user_icon, compound="left",
                      width=220, height=50, fg_color=BUTTON_BG, text_color=TEXT_COLOR,
                      command=self.manage_users).pack(pady=10)

        ctk.CTkButton(main_area, text="  Manage Orders", image=order_icon, compound="left",
                      width=220, height=50, fg_color=BUTTON_BG, text_color=TEXT_COLOR,
                      command=self.manage_orders).pack(pady=10)

        ctk.CTkButton(main_area, text="  Manage Products", image=product_icon, compound="left",
                      width=220, height=50, fg_color=BUTTON_BG, text_color=TEXT_COLOR,
                      command=self.manage_products).pack(pady=10)

        ctk.CTkButton(main_area, text="  View Reports", image=report_icon, compound="left",
                      width=220, height=50, fg_color=BUTTON_BG, text_color=TEXT_COLOR,
                      command=self.view_reports).pack(pady=10)

    def load_icon(self, path):
        try:
            img = Image.open(path).resize((20, 20))
            return ctk.CTkImage(light_image=img, size=(20, 20))
        except Exception as e:
            print(f"⚠️ Failed to load image: {path} — {e}")
            return None

    def logout(self):
        self.master.destroy()
        subprocess.Popen(["python", "login.py"])

    def manage_users(self):
        self.master.destroy()
        subprocess.Popen(["python", "manage_users.py", self.email])

    def manage_orders(self):
        self.master.destroy()
        subprocess.Popen(["python", "manage_orders.py", self.email])

    def manage_products(self):
        self.master.destroy()
        subprocess.Popen(["python", "manage_products.py", self.email])

    def view_reports(self):
        self.master.destroy()
        subprocess.Popen(["python", "view_reports.py", self.email])  # 🔍 Add this script

# ========== RUN ==========
if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        app = AdminApp(email)
        app.mainloop()
    else:
        print("❌ ERROR: No admin email provided!")
