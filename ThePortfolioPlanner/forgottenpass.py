import sqlite3                
import customtkinter as ctk     
from tkinter import messagebox   
from subprocess import call 
import tkinter as tk  
import hashlib
import re 


# Forgotten password class creation
class ForgottenPass(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("userdata.db")
        self.cursor = self.conn.cursor()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.title("Forgotten Password")
        screen_width = self.winfo_screenwidth()
        self.geometry(f"1920x1080+{int((screen_width - 1920) / 2)}+0") 

        self.forgotten_pass_frame = ctk.CTkFrame(self)
        self.forgotten_pass_frame.configure(bg_color="transparent", height=350, width=500, corner_radius=50)
        self.forgotten_pass_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.title_label = ctk.CTkLabel(self.forgotten_pass_frame, text="Forgotten Password \n \n Please enter your Username and Email", font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.place(relx=0.5, rely=0.05, anchor=tk.N)

        self.username_label = ctk.CTkLabel(self.forgotten_pass_frame, text="Username:")
        self.username_label.place(relx=0.1, rely=0.45, anchor=tk.W)
        self.username_entry = ctk.CTkEntry(self.forgotten_pass_frame, width=int(screen_width*0.115))
        self.username_entry.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        self.email_label = ctk.CTkLabel(self.forgotten_pass_frame, text="Email:")
        self.email_label.place(relx=0.1, rely=0.65, anchor=tk.W)
        self.email_entry = ctk.CTkEntry(self.forgotten_pass_frame, width=int(screen_width*0.115))
        self.email_entry.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        self.submit_button = ctk.CTkButton(self.forgotten_pass_frame, text="Submit", command=self.submit_button_function)
        self.submit_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        self.back_button = ctk.CTkButton(self.forgotten_pass_frame, text="Back", command=self.open_login, width=int(screen_width*0.025))
        self.back_button.place(relx=0.05, rely=0.05, anchor=tk.NW)

    # Function for when user clicks on submit button
    def submit_button_function(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()

        if not username or not email:
            messagebox.showerror("Input Error", "Please enter all fields")
            return

        if self.check_user_existence(username, email):
            # Users found, proceed to the change password frame
            messagebox.showinfo("Account Found", "Account Successfully Found, Please proceed " + username)
            self.show_change_password_frame(username)
        else:
            messagebox.showerror("Account Error", "Username or Email Incorrect")

    # Checks whether user has an account or not
    def check_user_existence(self, username, email):
        # Check if username and email exist in the database
        self.cursor.execute("SELECT * FROM logininfo WHERE username = ? AND email = ?", (username, email))
        user_data = self.cursor.fetchone()
        return True if user_data else False

    # Gets security question based on username
    def get_security_question(self, username):
        # Retrieves the security question based on their username
        self.cursor.execute("SELECT security_question FROM logininfo WHERE username = ?", (username,))
        security_question = self.cursor.fetchone()
        return security_question[0] if security_question else None

    # Shows second frame after user has been verified
    def show_change_password_frame(self, username):
        screen_width = self.winfo_screenwidth()
        # Hides the forgotten_pass_frame
        self.forgotten_pass_frame.place_forget()

        # Retrieves security question based on their username
        security_question = self.get_security_question(username)

        # Creates change_password_frame
        self.change_password_frame = ctk.CTkFrame(self)
        self.change_password_frame.configure(bg_color="transparent", height=400, width=500, corner_radius=50)
        self.change_password_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        if security_question:
            # Displays security question as a label
            self.security_question_label = ctk.CTkLabel(self.change_password_frame, text=f"Security Question: {security_question}")
            self.security_question_label.place(relx=0.15, rely=0.1, anchor=tk.W)

            self.security_answer_label = ctk.CTkLabel(self.change_password_frame, text="Answer:")
            self.security_answer_label.place(relx=0.1, rely=0.25, anchor=tk.W)
            self.security_answer_entry = ctk.CTkEntry(self.change_password_frame, width=int(screen_width*0.125), show="*")
            self.security_answer_entry.place(relx=0.6, rely=0.25, anchor=tk.CENTER)

            self.new_password_label = ctk.CTkLabel(self.change_password_frame, text="Enter New Password:")
            self.new_password_label.place(relx=0.1, rely=0.4375, anchor=tk.W)
            self.new_password_entry = ctk.CTkEntry(self.change_password_frame, width=int(screen_width*0.125), show="*")
            self.new_password_entry.place(relx=0.6, rely=0.4375, anchor=tk.CENTER)

            self.confirm_password_label = ctk.CTkLabel(self.change_password_frame, text="Confirm Password:")
            self.confirm_password_label.place(relx=0.1, rely=0.625, anchor=tk.W)
            self.confirm_password_entry = ctk.CTkEntry(self.change_password_frame, width=int(screen_width*0.125), show="*")
            self.confirm_password_entry.place(relx=0.6, rely=0.625, anchor=tk.CENTER)

            self.submit_password_button = ctk.CTkButton(self.change_password_frame, text="Submit", command=self.submit_password_function)
            self.submit_password_button.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
        else:
            messagebox.showerror("Error", "Security question not found for this user.")

    # Second submit button on second frame
    def submit_password_function(self):
        # Retrieves the entered answer to the security question and gets rid of whitespace
        security_answer = self.security_answer_entry.get().strip()

        # Retrieves the entered new password and gets rid of whitespace
        new_password = self.new_password_entry.get().strip()

        # Retrieves the entered confirm password and gets rid of whitespace
        confirm_password = self.confirm_password_entry.get().strip()

        if security_answer and new_password and confirm_password:
            # Checks if the passwords match
            if new_password == confirm_password:
                # Checks if the password meets requirements
                if self.validate_password(new_password):
                    # Fetches the salt from the database for the specified username
                    username = self.username_entry.get().strip()
                    self.cursor.execute("SELECT salt, security_answer_hash FROM logininfo WHERE username = ?", (username,))
                    result = self.cursor.fetchone()
                    if result:
                        salt = result[0]
                        security_answer_hash_from_db = result[1]

                        # Concatenates the entered security answer with the fetched salt
                        concatenated_security_answer = security_answer + salt

                        # Hashes the concatenated string
                        hashed_security_answer = hashlib.sha3_512(concatenated_security_answer.encode()).hexdigest()

                        # Compares the hashed security answer with the stored security_answer_hash
                        if hashed_security_answer == security_answer_hash_from_db:
                            # Concatenates the password and new salt, then hash
                            hashed_password = hashlib.sha3_512((new_password + salt).encode()).hexdigest()

                            # Updates the password and salt in the database for the specified username
                            self.cursor.execute("UPDATE logininfo SET password_hash = ?, salt = ? WHERE username = ?", (hashed_password, salt, username))
                            self.conn.commit()

                            messagebox.showinfo("Success", "Password updated successfully!")

                            # Closes the application/navigate to the login page
                            self.open_login()
                        else: # Error handling
                            messagebox.showerror("Security Error", "Security answer is incorrect.")
                    else:
                        messagebox.showerror("Account Error", "User not found.")
                else:
                    messagebox.showerror("Password Error", "Password must contain at least 1 digit, 1 special character, 1 uppercase letter, and 1 lowercase letter.")
            else:
                messagebox.showerror("Password Error", "Passwords do not match.")
        else:
            messagebox.showerror("Input Error", "Please enter all fields.")

    # Validates the user's new password
    def validate_password(self, password):
        # Validate the password against the requirements
        if re.match(r"^(?=.*[0-9])(?=.*[!@#$%^&*()])(?=.*[a-z])(?=.*[A-Z]).{8,}$", password):
            return True
        return False

    # Function to open the login screen
    def open_login(self):
        # Close the application or navigate to the login page
        self.destroy()
        call(["python", "Login.py"])


if __name__ == '__main__':
    app = ForgottenPass()
    app.mainloop()








