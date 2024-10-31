import tkinter as tk  # Importing the tkinter library for GUI
import customtkinter  # Importing a custom tkinter module
from PIL import ImageTk, Image  # Importing modules for image handling
import sqlite3  # Importing SQLite for database operations
import hashlib  # Importing hashlib for password hashing
from subprocess import call  # Importing call for subprocess management
from tkinter import messagebox  # Importing messagebox for displaying messages

# Set appearance mode to dark mode and green color theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

class LoginPage:
    def __init__(self, root):
        # Initialize the login page with a root window
        self.root = root
        self.root.title('Login')
        self.conn = sqlite3.connect("userdata.db")  # Connect to the SQLite database
        self.cursor = self.conn.cursor()  # Create a cursor for database operations
        self.create_table()  # Create the necessary table in the database
        self.create_ui()  # Create the graphical user interface
        
    def create_table(self):
        # Create the logininfo table if it doesn't exist in the database
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logininfo (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                salt TEXT,
                email TEXT,
                user_logged_in BOOLEAN
            )
        ''')
        self.conn.commit()  # Commit the changes
        
    def create_ui(self):
        # Create the graphical user interface for the login page
        self.create_background_image()  # Set the background image
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Get the screen height
        
        # Create and place labels, buttons, and entry fields on the UI
        l1 = customtkinter.CTkLabel(master=self.root, text="Welcome To The Portfolio Planner!", font=("Century Gothic", int(screen_width/80), "bold"), text_color="white", bg_color="transparent")
        l1.place(relx=0.5, rely=screen_height*0.1/screen_height, anchor=tk.CENTER)
        
        frame = customtkinter.CTkFrame(master=self.root, width=int(screen_width*0.167), height=int(screen_height*0.350), corner_radius=int(screen_width/128), border_width=int(screen_width/853), border_color="gray")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        l2 = customtkinter.CTkLabel(master=frame, text="Log into your Account", font=('Century Gothic', int(screen_width/80)))
        l2.place(relx=0.5, rely=0.13, anchor=tk.CENTER)
        
        self.username = customtkinter.CTkEntry(master=frame, width=int(screen_width*0.115), placeholder_text='Username')
        self.username.place(relx=0.5, rely=0.25, anchor=tk.CENTER)
        
        self.password = customtkinter.CTkEntry(master=frame, width=int(screen_width*0.115), placeholder_text='Password', show="*")
        self.password.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
        
        self.show_password = False
        show_password_button = customtkinter.CTkButton(master=frame, width=int(screen_width/170), text="👁", command=self.toggle_password_visibility)
        show_password_button.place(relx=0.95, rely=0.35, anchor=tk.E)
        
        button1 = customtkinter.CTkButton(master=frame, width=int(screen_width*0.115), text="Login", command=self.login_button_function, corner_radius=int(screen_width/128))
        button1.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
        
        close_button = customtkinter.CTkButton(master=frame, width=int(screen_width/205), text="X", text_color="white", command=self.close_program, corner_radius=int(screen_width/85))
        close_button.place(relx=0.92, rely=0.05, anchor=tk.CENTER)  
        
        l3 = customtkinter.CTkLabel(master=frame, text="Don't have an account?\nCreate one by clicking the Register button", font=("Century Gothic", int(screen_width/150), "bold"))
        l3.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        
        button2 = customtkinter.CTkButton(master=frame, width=int(screen_width*0.115), text="Register", corner_radius=int(screen_width/128), command=self.open_registration_page)
        button2.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
        
        forgotten_password_label = customtkinter.CTkLabel(master=frame, text="Forgotten Password?", font=("Century Gothic", int(screen_width/140), "underline", "bold"), text_color="red", cursor="hand2")
        forgotten_password_label.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        forgotten_password_label.bind("<Button-1>", self.forgotten_password_link_clicked)
        
    def create_background_image(self):
        # Load and display the background image for the login page
        image_path = "Background.jpg"
        original_image = Image.open(image_path)
        new_width, new_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        resized_image = original_image.resize((new_width, new_height))
        resized_img1 = ImageTk.PhotoImage(resized_image)
        label = tk.Label(self.root, image=resized_img1)
        label.image = resized_img1
        label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
    def open_registration_page(self):
        # Close the current login page and open the registration page
        self.root.destroy()
        call(["python", "Register.py"])
        
    def login_button_function(self):
        # Process the login attempt when the login button is clicked
        username = self.username.get().strip()  # Get the entered username
        password = self.password.get().strip()  # Get the entered password
        
        if not username or not password:
            # Show error message if any field is empty
            messagebox.showerror("Input Error", "Please enter all fields")
            return

        if username and password:
            try:
                # Update the database to mark all other users as logged out
                self.cursor.execute("UPDATE logininfo SET user_logged_in = 0 WHERE username != ?", (username,))
                self.conn.commit()

                # Retrieve salt and hashed password from the database
                self.cursor.execute("SELECT salt, password_hash FROM logininfo WHERE username=?", (username,))
                result = self.cursor.fetchone()

                if result:
                    salt, stored_password_hash = result
                    # Hash the entered password with the retrieved salt
                    hashed_password_with_salt = hashlib.sha3_512((password + salt).encode()).hexdigest()

                    if hashed_password_with_salt == stored_password_hash:
                        # If password matches, mark user as logged in and open the dashboard
                        self.cursor.execute("UPDATE logininfo SET user_logged_in = 1 WHERE username = ?", (username,))
                        self.conn.commit()

                        messagebox.showinfo("Login Successful", "Welcome, " + username)
                        self.root.destroy()
                        call(["python", "Dashboard.py"])
                    else:
                        # Show error message for incorrect credentials
                        messagebox.showerror("Login Failed", "Invalid username or password")
                else:
                    # Show error message if username doesn't exist
                    messagebox.showerror("Login Failed", "Invalid username or password")
            except Exception as e:
                print("An error occurred:", str(e))
                # Show error message for any exceptions during login
                messagebox.showerror("Login Failed", "An error occurred while logging in")
        else:
            # Show error message if username or password is empty
            messagebox.showerror("Login Failed", "Please enter a username and password")

    def toggle_password_visibility(self):
        # Toggle the visibility of the password when the eye button is clicked
        self.show_password = not self.show_password
        self.password.configure(show="" if self.show_password else "*")
    
    def close_program(self):
        # Close the program when the close button is clicked
        self.root.destroy()

    def forgotten_password_link_clicked(self, event):
        # Close the current login page and open the forgotten password page
        self.root.destroy()
        call(["python", "forgottenpass.py"])

if __name__ == "__main__":
    # Create the root window for the login page
    root = customtkinter.CTk()
    login_page = LoginPage(root)  # Initialize the login page
    root.mainloop() 


