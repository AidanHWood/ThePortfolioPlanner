# Required python imports
import os  # Module providing a portable way of using operating system-dependent functionality
import customtkinter  # Custom module for creating customized Tkinter widgets
import sqlite3  # Module providing a lightweight disk-based database
import hashlib  # Module providing secure hash and digest algorithms
from tkinter import messagebox  # Module for creating message boxes in Tkinter
import tkinter as tk  # Standard Python interface to the Tk GUI toolkit
from subprocess import call  # Module allowing the spawning of new processes
import secrets  # Module for generating cryptographically strong random numbers
from PIL import ImageTk, Image  # Module for opening, manipulating, and saving many different image file formats

class RealEstateApp:
    # Real estate class 
    def __init__(self, root):
        # Initial root config
        self.root = root
        self.root.title('Register')  # Set the title of the root window
        self.setup_styles()  # Call method to set up the UI styles
        self.conn = sqlite3.connect("userdata.db")  # Connect to the SQLite database
        self.cursor = self.conn.cursor()  # Create a cursor object for the database connection
        self.create_database_table()  # Call method to create the database table
        self.create_ui()  # Call method to create the user interface
        
        # Get the screen resolution
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Set the window geometry to match the screen resolution
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")

    # Sets the color theme to green and mode to dark 
    def setup_styles(self):
        customtkinter.set_appearance_mode("dark")  # Set the appearance mode to dark
        customtkinter.set_default_color_theme("green")  # Set the default color theme to green

    # Logininfo SQL creation command
    def create_database_table(self):
        # Execute SQL command to create the logininfo table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logininfo (
                username TEXT PRIMARY KEY,
                password_hash TEXT,
                salt TEXT,
                email TEXT,
                security_question INTEGER,
                security_answer_hash TEXT,
                user_logged_in BOOLEAN
            )
        ''')
        # Commit the transaction
        self.conn.commit()

    # Function to create User interface
    def create_ui(self):
        # Get the screen resolution
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Call method to create the background image
        self.create_background_image()
        # Create and place a label widget for the welcome message
        l1 = customtkinter.CTkLabel(master=self.root, text="Welcome To The PortFolio Planner!", font=("Century Gothic", int(screen_width/80), "bold"))
        l1.place(relx=0.4, rely=screen_height*0.05/screen_height)
        # Call method to create the registration frame
        self.create_registration_frame()

    # Function to display background home image  
    def create_background_image(self):
        # Construct the image file path using 'os.path.join'
        image_path = os.path.join(os.path.dirname(__file__), "Background.jpg")
        # Open the image file
        original_image = Image.open(image_path)
        # Set the desired dimensions for the image
        new_width, new_height = 1920, 1080
        # Resize the image
        resized_image = original_image.resize((new_width, new_height))
        # Convert the resized image to Tkinter format
        resized_img1 = ImageTk.PhotoImage(resized_image)
        # Create a label widget to display the image
        label = tk.Label(self.root, image=resized_img1)
        # Keep a reference to the image to prevent it from being garbage collected
        label.image = resized_img1
        # Display the label in the root window
        label.pack()

    # Layout and entries for register frame
    def create_registration_frame(self):
        # Create a frame for the registration form
        frame = customtkinter.CTkFrame(master=self.root, width=420, height=575, corner_radius=15, border_width=1.5, border_color="gray")
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Create and place labels, entry fields, and buttons for the registration form
        l2 = customtkinter.CTkLabel(master=frame, text="Register Your Account!", font=('Century Gothic', 25, "bold"))
        l2.place(relx=0.18, rely=0.03)
        
        self.entry1 = customtkinter.CTkEntry(master=frame, width=300, height=30, placeholder_text='Username')
        self.entry1.place(relx=0.15, rely=0.12)
        
        self.entry2 = customtkinter.CTkEntry(master=frame, width=300, height=30, placeholder_text='Email Address')
        self.entry2.place(relx=0.15, rely=0.21)
        
        self.entry3 = customtkinter.CTkEntry(master=frame, width=300, height=30, placeholder_text='Password', show="*")
        self.entry3.place(relx=0.15, rely=0.30)
        
        self.entry4 = customtkinter.CTkEntry(master=frame, width=300, height=30, placeholder_text='Confirm Password', show="*")
        self.entry4.place(relx=0.15, rely=0.39)
        
        l4 = customtkinter.CTkLabel(master=frame, text="Please Choose A Security Question", font=('Century Gothic', 13, "bold"))
        l4.place(relx=0.25, rely=0.48)
        
        self.security_question = customtkinter.CTkOptionMenu(master=frame, values=["What is the name Of your First Pet?", "What is your Mothers Maiden Name?", "What is The Number of your First House?"], width=250, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.security_question.place(relx=0.15, rely=0.56)
        
        self.entry5 = customtkinter.CTkEntry(master=frame, width=300, height=30, placeholder_text='Security Question Answer', show="*")
        self.entry5.place(relx=0.15, rely=0.65)
        
        button1 = customtkinter.CTkButton(master=frame, width=300, text="Register", command=self.register_button_function, corner_radius=15)
        button1.place(relx=0.15, rely=0.73)
        
        l4 = customtkinter.CTkLabel(master=frame, text="Already have an account? \n Log in by clicking on the Login button", font=("Century Gothic", 12 , "bold"))
        l4.place(relx=0.25, rely=0.82)
        
        button2 = customtkinter.CTkButton(master=frame, width=300, text="Login", corner_radius=15, command=self.open_login_page)
        button2.place(relx=0.15, rely=0.90)

    # Login page open function 
    def open_login_page(self):
        # Destroy the current root window
        self.root.destroy()
        # Open the login page
        call(["python", "Login.py"])

    # Register page open function
    def register_button_function(self):
        # Get the values entered in the registration form
        username = self.entry1.get()
        email = self.entry2.get()
        password = self.entry3.get()
        confirmpass = self.entry4.get()
        security_question = self.security_question.get()
        security_answer = self.entry5.get()
        
        # If statements for presence checks
        if not username or not email or not password or not confirmpass or not security_answer:
            messagebox.showerror("Input Error", "Please enter all fields")
            return
        
        # Minimum length checks
        if len(username) < 4 or len(email) < 5 or len(password) < 4 or len(confirmpass) < 4 or len(security_answer) < 1:
            messagebox.showerror("Registration Failed", "One of your fields is too short, Please retry")
            return
        
        # Maximum length checks
        if len(username) > 25 or len(email) > 30 or len(password) > 30 or len(security_answer) > 25:
            messagebox.showerror("Registration Failed", "One of your fields is too long, Please retry")
            return
        
        # Error handling 
        if username and email and password and confirmpass and security_answer and security_question:
            if self.check_username_exists(username):
                messagebox.showerror("Registration Failed", "Username already exists. Please choose another one.")
            if self.check_email_exists(email):
                messagebox.showerror("Registration Failed", "Email already exists. Please use another one.")
            elif not self.is_valid_email(email):
                messagebox.showerror("Registration Failed", "Invalid email format. Please enter a valid email address.")
            elif not self.is_pass_valid(password):
                messagebox.showerror("Registration Failed", "Password must contain at least one upper case character, one lower case character, one number, and one special character.")
            elif password != confirmpass:
                messagebox.showerror("Registration Failed", "Passwords do not match! Please retry.")
            else:
                try:
                    # Generates random salt
                    salt = secrets.token_hex(16)

                    # Concatenates the password and salt, then hashes it
                    hashed_password = hashlib.sha3_512((password + salt).encode()).hexdigest()

                    # Concatenates the security answer and salt, then hashes 
                    hashed_security_answer = hashlib.sha3_512((security_answer + salt).encode()).hexdigest()

                    # Sets user_logged_in to 0 for all other users
                    self.cursor.execute("UPDATE logininfo SET user_logged_in = 0 WHERE username != ?", (username,))
                    self.conn.commit()

                    # Saves the hashed password, security answer, and salt to the database
                    self.cursor.execute("INSERT INTO logininfo (username, password_hash, salt, email, security_question, security_answer_hash, user_logged_in) VALUES (?, ?, ?, ?, ?, ?, 1)", (username, hashed_password, salt, email, security_question, hashed_security_answer))
                    self.conn.commit()

                    print("User data saved successfully.")
                    messagebox.showinfo("Registration Successful", "Account created successfully.")
                    self.root.destroy()
                    call(["python", "Dashboard.py"])
                except Exception as e: # Error handling for issues
                    print("An error occurred:", str(e))
                    messagebox.showerror("Registration Failed", "An error occurred while registering.")
        else:
            messagebox.showerror("Registration Failed", "Please enter a username, email, password, and security answer.")

    # Function to check if a username already exists
    def check_username_exists(self, username):
        self.cursor.execute("SELECT username FROM logininfo WHERE username = ?", (username,))
        existing_user = self.cursor.fetchone()
        return existing_user is not None
    
    # Function to check whether an email already exists
    def check_email_exists(self, email):
        self.cursor.execute("SELECT email FROM logininfo WHERE email = ?", (email,))
        existing_user = self.cursor.fetchone()
        return existing_user is not None
    
    # Function to check whether a password meets the criteria
    def is_pass_valid(self, password):
        lowerCase, upperCase, num, special = False, False, False, False
        for char in password:
            if char.isdigit():
                num = True
            if char.islower():
                lowerCase = True
            if char.isupper():
                upperCase = True
            if not char.isalnum():
                special = True
        return lowerCase and upperCase and num and special

    def is_valid_email(self, email):
        # A very simple email format check
        return "@" in email
    

if __name__ == "__main__":
    root = customtkinter.CTk()
    app = RealEstateApp(root)
    root.mainloop()
