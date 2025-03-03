import tkinter as tk    
from tkinter import messagebox  
import customtkinter          
from tkcalendar import Calendar 
from subprocess import call 
import sqlite3      
from datetime import datetime  


# Sets color theme to green and color mode to dark
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

# Database connection
conn = sqlite3.connect("userdata.db")
cursor = conn.cursor()

# Open login page function
def open_login():
    app.destroy()
    call(["python", "Login.py"])

# Open calendar page function
def open_cal():
    app.destroy()
    call(["python", "Calendar.py"])

# Open dashboard page function
def open_dash():
    app.destroy()
    call(["python", "Dashboard.py"])

# Creates paymentinfo database table
def create_paymentinfo_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paymentinfo (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            payment_amount REAL,
            reason TEXT,
            title TEXT,
            payer_details TEXT,
            payment_date DATE,
            FOREIGN KEY (username) REFERENCES logininfo(username)
        )
    ''')
    conn.commit()

# Function for passing data into paymentinfo database table
def insert_payment():
    payment_amount = app.enter_amount.get()
    reason = app.enter_reason.get()
    title = app.drop_title.get()
    payer_details = app.payer_details.get()
    payment_date = app.pay_date.get()
    
    if len(payment_amount) > 15 or len(reason) > 30 or len(payer_details) > 30:
        messagebox.showerror("Input Error", "One of your inputs is too large")
        return
    
    if not payment_amount or not reason or not payer_details or not payment_date:
        messagebox.showerror("Input Error", "Please enter all fields")
        return
    
    try:
        payment_amount = float(app.enter_amount.get())  # Convert to float
    except ValueError:
        messagebox.showerror("Input Error", "Invalid input for Payment Amount. Please enter a valid number.")
        return

    cursor.execute("SELECT username FROM logininfo WHERE user_logged_in = 1")
    user = cursor.fetchone()
    if user:
        username = user[0]
        cursor.execute('''
            INSERT INTO paymentinfo (username, payment_amount, reason, title, payer_details, payment_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, payment_amount, reason, title, payer_details, payment_date))
        conn.commit()
        messagebox.showinfo("Success", "Payment Successfully Created!")
        app.display_past_records()  # Update past payments display
    else:
        messagebox.showerror("Error", "No user is currently logged in.")

# Function to create expenditureinfo database table
def create_expenditureinfo_table():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenditureinfo (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            expenditure_amount REAL,
            reason TEXT,
            companyname TEXT,
            expenditure_date DATE,
            FOREIGN KEY (username) REFERENCES logininfo(username)
        )
    ''')
    conn.commit()

# Function to store data in expenditureinfo database table
def insert_expenditure():
    expenditure_amount = app.amount_expen.get()
    reason = app.enter_reason_expen.get()
    company_name = app.payee_name.get()
    expenditure_date = app.expen_date.get()
    
    if len(expenditure_amount) > 15 or len(reason) > 30 or len(company_name) > 30:
        messagebox.showerror("Input Error", "One of your inputs is too large")
        return
    
    if not expenditure_amount or not reason or not company_name or not expenditure_date:
        messagebox.showerror("Input Error", "Please enter all fields")
        return
    
    try:
        expenditure_amount = float(app.amount_expen.get())  # Convert to float
    except ValueError:
        messagebox.showerror("Error", "Invalid input for Expenditure Amount. Please enter a valid number.")
        return

    cursor.execute("SELECT username FROM logininfo WHERE user_logged_in = 1")
    user = cursor.fetchone()
    if user:
        username = user[0]
        cursor.execute('''
            INSERT INTO expenditureinfo (username, expenditure_amount, reason, companyname, expenditure_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, expenditure_amount, reason, company_name, expenditure_date))
        conn.commit()
        messagebox.showinfo("Success", "Expenditure Successfully Created!")
    else:
        messagebox.showerror("Error", "No user is currently logged in.")

# Define app class
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finances")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        # Calculate frame sizes based on screen dimensions
        sidebar_width = int(screen_width * 0.075)
        self.display_mode = "expenditure"      

        # Sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=sidebar_width, height=screen_height)
        self.sidebar_frame.place(relx=0, rely=0, relwidth=0.09, relheight=1)

        # Logo label
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Welcome!", font=("Century Gothic", int(screen_width/85), "bold"))
        self.logo_label.place(relx=0.5, rely=0.02, anchor="n", relwidth=0.8)

        # Buttons in the sidebar frame
        # Configure and place the buttons in the sidebar frame
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Dashboard", height=50, command=open_dash)
        self.sidebar_button_1.place(relx=0.5, rely=0.1, anchor="n", relwidth=0.8)

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Finances", height=50)
        self.sidebar_button_2.place(relx=0.5, rely=0.3, anchor="n", relwidth=0.8)

        # Calendar button
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Calendar", height=50, command=open_cal)
        self.sidebar_button_3.place(relx=0.5, rely=0.5, anchor="n", relwidth=0.8)

        # Logout button
        self.logoutbtn = customtkinter.CTkButton(self.sidebar_frame, text="Logout", command=open_login)
        self.logoutbtn.place(relx=0.5, rely=0.92, anchor="n", relwidth=0.8)

        self.logoutbtnlb = customtkinter.CTkLabel(self.sidebar_frame, text="Log Out:", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.logoutbtnlb.place(relx=0.12, rely=0.88, anchor="nw", relwidth=0.8)

        # Appearance mode label and option menu
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.place(relx=0.09, rely=0.84, anchor="sw", relwidth=0.8)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance" "\n" "Mode:", anchor="n", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.appearance_mode_label.place(relx=0.10, rely=0.80, anchor="sw", relwidth=0.8)

        # Income frame
        self.income_frame = customtkinter.CTkFrame(self, corner_radius=50)
        self.income_frame.place(relx=0.13, rely=0.01, relwidth=0.38, relheight=0.55)

        # Expenditure frame
        self.expenditure_frame = customtkinter.CTkFrame(self, corner_radius=50)
        self.expenditure_frame.place(relx=0.57, rely=0.01, relwidth=0.38, relheight=0.55)

        # Past payments frame
        self.past_payments_frame = customtkinter.CTkFrame(self, bg_color="gray")
        self.past_payments_frame.place(relx=0.125, rely=0.6, relwidth=0.85, relheight=0.35)
        
        self.create_expenditure_elements()
        self.create_income_elements()
        self.create_past_payments_treeview()



    def create_income_elements(self):

        # Widgets for creating income elements
        self.income_title = customtkinter.CTkLabel(self.income_frame, text="Create New Payment", font=customtkinter.CTkFont(size=18, weight="bold"))
        self.income_title.place(relx=0.5, rely=0.015, anchor="n")

        self.create_payment = customtkinter.CTkButton(self.income_frame, text="Create Payment", height=50, width=200, command=insert_payment)
        self.create_payment.place(relx=0.5, rely=0.95, anchor="s")

        self.pay_amount_lb = customtkinter.CTkLabel(self.income_frame, text="Payment Amount:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.pay_amount_lb.place(relx=0.5, rely=0.1, anchor="n")
        self.enter_amount = customtkinter.CTkEntry(self.income_frame, placeholder_text="Payment Amount (£)", width=250)
        self.enter_amount.place(relx=0.5, rely=0.18, anchor="n")

        self.pay_reason_lb = customtkinter.CTkLabel(self.income_frame, text="Reason for Payment:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.pay_reason_lb.place(relx=0.5, rely=0.28, anchor="n")
        self.enter_reason = customtkinter.CTkEntry(self.income_frame, placeholder_text="Reason for payment", width=250)
        self.enter_reason.place(relx=0.5, rely=0.36, anchor="n")
        
        self.drop_title = customtkinter.CTkOptionMenu(self.income_frame, values=["Mr", "Mrs", "Ms", "Dr", "N/A"], width=10, font=customtkinter.CTkFont(size=15, weight="bold"))
        self.drop_title.place(relx=0.20, rely=0.54, anchor="n")
        self.payer_details_lb = customtkinter.CTkLabel(self.income_frame, text="Payer Details:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.payer_details_lb.place(relx=0.5, rely=0.46, anchor="n")
        self.payer_details = customtkinter.CTkEntry(self.income_frame, placeholder_text="Payer Details", width=250)
        self.payer_details.place(relx=0.5, rely=0.54, anchor="n")

        self.pay_date_lb = customtkinter.CTkLabel(self.income_frame, text="Payment Date:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.pay_date_lb.place(relx=0.5, rely=0.62, anchor="n")
        self.pay_date = customtkinter.CTkEntry(self.income_frame, placeholder_text="Payment Date (YYYY-MM-DD)", width=185)
        self.pay_date.place(relx=0.5, rely=0.70, anchor="n")
        self.pay_date.bind("<Button-1>", self.open_calendar)

        # Create the calendar popup
        self.calendar_popup = Calendar(self, selectmode="day", date_pattern="YYYY-MM-DD")
        self.calendar_popup.bind("<<CalendarSelected>>", self.update_calendar_entry)


    def create_expenditure_elements(self):
        # Widgets for creating expenditure elements
        self.expen_title = customtkinter.CTkLabel(self.expenditure_frame, text="Create New Expenditure", font=customtkinter.CTkFont(size=18, weight="bold"))
        self.expen_title.place(relx=0.5, rely=0.015, anchor="n")

        self.create_expenditure = customtkinter.CTkButton(self.expenditure_frame, text="Create Expenditure", height=50, width=200, command=insert_expenditure)
        self.create_expenditure.place(relx=0.5, rely=0.95, anchor="s")

        self.expen_amount_lb = customtkinter.CTkLabel(self.expenditure_frame, text="Expenditure Amount:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.expen_amount_lb.place(relx=0.5, rely=0.1, anchor="n")
        self.amount_expen = customtkinter.CTkEntry(self.expenditure_frame, placeholder_text="Expenditure Amount (£)", width=250)
        self.amount_expen.place(relx=0.5, rely=0.18, anchor="n")

        self.expen_reason_lb = customtkinter.CTkLabel(self.expenditure_frame, text="Reason for Expenditure:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.expen_reason_lb.place(relx=0.5, rely=0.28, anchor="n")
        self.enter_reason_expen = customtkinter.CTkEntry(self.expenditure_frame, placeholder_text="Reason for Expenditure", width=250)
        self.enter_reason_expen.place(relx=0.5, rely=0.36, anchor="n")

        self.payee_details_lb_expen = customtkinter.CTkLabel(self.expenditure_frame, text="Payee/Company Details:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.payee_details_lb_expen.place(relx=0.5, rely=0.46, anchor="n")
        self.payee_name = customtkinter.CTkEntry(self.expenditure_frame, placeholder_text="Payee/Company Name", width=250)
        self.payee_name.place(relx=0.5, rely=0.54, anchor="n")

        self.expen_date_lb = customtkinter.CTkLabel(self.expenditure_frame, text="Expenditure Date:", font=customtkinter.CTkFont(size=13, weight="bold"))
        self.expen_date_lb.place(relx=0.5, rely=0.62, anchor="n")
        self.expen_date = customtkinter.CTkEntry(self.expenditure_frame, placeholder_text="Expenditure Date (YYYY-MM-DD)", width=200)
        self.expen_date.place(relx=0.5, rely=0.70, anchor="n")
        self.expen_date.bind("<Button-1>", self.open_calendar)

        # Create the calendar popup
        self.calendar_popup = Calendar(self, selectmode="day", date_pattern="YYYY-MM-DD")
        self.calendar_popup.bind("<<CalendarSelected>>", self.update_calendar_entry)


    def create_past_payments_treeview(self):
        # Configure past payments treeview
        past_payments_columns = ["Record ID", "Username", "Payment Amount", "Reason", "Title", "Payer Details", "Payment Date"]
        self.past_payments_treeview = tk.ttk.Treeview(self.past_payments_frame, columns=past_payments_columns, show="headings")
        for col in past_payments_columns:
            self.past_payments_treeview.heading(col, text=col)
            self.past_payments_treeview.column(col, anchor="center")
        self.display_past_records()
        self.past_payments_treeview.pack(expand=True, fill="both")

        # Frame to contain buttons
        button_frame = customtkinter.CTkFrame(self.past_payments_frame)
        button_frame.place(relx=0, rely=0.8, relheight=0.2, relwidth=1)

        # Delete button
        self.delete_button = customtkinter.CTkButton(button_frame, text="Delete Record", command=self.delete_past_payment)
        self.delete_button.place(relx=0.4, rely=0.1)

        # Toggle button
        self.toggle_button_text = tk.StringVar()
        self.toggle_button_text.set("View All Payments")
        self.toggle_button = customtkinter.CTkButton(button_frame, textvariable=self.toggle_button_text, command=self.toggle_display_mode)
        self.toggle_button.place(relx=0.6, rely=0.1)



    def display_past_records(self):
        # Clears previous data in the treeview
        for item in self.past_payments_treeview.get_children():
            self.past_payments_treeview.delete(item)

        # Retrieves the current user's username
        cursor.execute("SELECT username FROM logininfo WHERE user_logged_in =1")
        user = cursor.fetchone()
        if not user:
            messagebox.showwarning("No User", "No user is currently logged in.")
            return

        username = user[0]

        # Retrieves all records based on the current mode and the current username from the database
        if self.display_mode == "payments":
            cursor.execute("SELECT * FROM paymentinfo WHERE username=?", (username,))
            columns = ["Record ID", "Username", "Payment Amount", "Reason", "Title", "Payer Details", "Payment Date"]
        else:
            cursor.execute("SELECT * FROM expenditureinfo WHERE username=?", (username,))
            columns = ["Record ID", "Username", "Expenditure Amount", "Reason", "Company Name", "Expenditure Date"]

        records = cursor.fetchall()

        # Calculate the column widths based on the screen resolution
        screen_width = self.winfo_screenwidth()
        column_widths = [int(screen_width * fraction) for fraction in [0.1, 0.1, 0.15, 0.2, 0.1, 0.15, 0.2]]  # Adjust fractions as needed

        # Adds data to the treeview
        for record in records:
            self.past_payments_treeview.insert("", "end", values=record)

        # Updates columns based on the current treeview mode
        self.past_payments_treeview["columns"] = columns
        for col, width in zip(columns, column_widths):
            self.past_payments_treeview.column(col, width=width, anchor="center")
            self.past_payments_treeview.heading(col, text=col)


    def delete_past_payment(self):
        selected_item = self.past_payments_treeview.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return

        # Gets the ID and details of the selected record
        record_id = self.past_payments_treeview.item(selected_item, "values")[0]
        record_details = self.past_payments_treeview.item(selected_item, "values")[1:]

        # Determines the table and mode based on the display mode
        if self.display_mode == "payments":
            table_name = "paymentinfo"
            mode = "payment"
        else:
            table_name = "expenditureinfo"
            mode = "expenditure"

        # Asks for confirmation from user before deletion
        confirmation = messagebox.askyesno("Delete Confirmation",
                                           f"Are you sure you want to delete {mode} record with Record ID {record_id}?\n\nDetails: {record_details}")
        if not confirmation:
            return

        # Deletes the record from the database
        cursor.execute(f"DELETE FROM {table_name} WHERE record_id=?", (record_id,))
        conn.commit()
        messagebox.showinfo("Deletion Successful", "Record Deleted Successfully.")

        # Refreshes the displayed records
        self.display_past_records()
        
        
    def open_calendar(self, event):
        if not hasattr(self, "calendar_popup"):
            return
        widget = event.widget
        self.current_calendar_entry = widget
        
        # Gets the current date
        current_date = datetime.today().date()
        
        # Sets the calendar selection to the current date
        self.calendar_popup.selection_set(current_date)
        
        self.calendar_popup.place(in_=widget, anchor="sw", bordermode="outside")
        self.calendar_popup.lift()


    def update_calendar_entry(self, event):
        selected_date = self.calendar_popup.get_date()
        if hasattr(self, "current_calendar_entry"):
            self.current_calendar_entry.delete(0, "end")
            self.current_calendar_entry.insert(0, selected_date)
        self.calendar_popup.place_forget()

    def toggle_display_mode(self):
        if self.display_mode == "payments":
            self.display_mode = "expenditure"
            self.toggle_button_text.set("View All Payments")
            self.delete_button.configure(command=self.delete_past_payment)
            self.delete_button.configure(text="Delete Record")
        else:
            self.display_mode = "payments"
            self.toggle_button_text.set("View All Expenditures")
            self.delete_button.configure(command=self.delete_past_payment)
            self.delete_button.configure(text="Delete Record")
        self.display_past_records()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

# Initialize and run the app
app = App()
app.mainloop()

# Close database connection
conn.close()



