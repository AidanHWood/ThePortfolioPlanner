# Import necessary modules
import sqlite3  # For interacting with SQLite database
from collections import defaultdict  # For creating defaultdict
import customtkinter  # For customized appearance of tkinter widgets
import matplotlib.pyplot as plt  # For creating plots
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # For embedding matplotlib figures in tkinter
from subprocess import call  # For calling external commands
from datetime import datetime, timedelta  # For working with dates and times

# Connect to the SQLite database
conn = sqlite3.connect("userdata.db")
cursor = conn.cursor()

# Set appearance mode of tkinter widgets to dark
customtkinter.set_appearance_mode("dark")
# Set default color theme to green
customtkinter.set_default_color_theme("green")

# Define method to open the login page
def open_login():
    app.destroy()  # Close the current window
    call(["python", "Login.py"])  # Open the login page

# Define method to open the finances page
def open_finances():
    app.destroy()  # Close the current window
    call(["python", "Finances.py"])  # Open the finances page

# Define method to open the calendar page
def open_cal():
    app.destroy()  # Close the current window
    call(["python", "Calendar.py"])  # Open the calendar page

# Create the main application window using customtkinter
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # Create paymentinfo and expenditureinfo tables if they don't exist
        self.create_paymentinfo_table()
        self.create_expenditureinfo_table()
        # Configure the window
        self.title("Dashboard")  # Set window title
        screen_width = self.winfo_screenwidth()  # Get screen width
        # Set window size and position
        self.geometry(f"1920x1080+{int((screen_width - 1920) / 2)}+0")

        # Create a grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Create sidebar frame
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((2, 4, 6, 8, 10, 12), weight=1)
        self.sidebar_frame.grid_rowconfigure((8, 10, 12), weight=0)

        # Add welcome label to the sidebar
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Welcome!", font=("Century Gothic", int(screen_width/80), "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Add buttons to the sidebar for navigation
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Dashboard", height=50)
        self.sidebar_button_1.grid(row=2, column=0, padx=20, pady=5)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Finances", height=50, command=open_finances)
        self.sidebar_button_2.grid(row=4, column=0, padx=20, pady=5)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Calendar", height=50, command=open_cal)
        self.sidebar_button_3.grid(row=6, column=0, padx=20, pady=5)

        # Add appearance mode option menu to the sidebar
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance" "\n" "Mode:", anchor="n", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 10))  

        # Add logout button to the sidebar
        self.logoutbtnlabel = customtkinter.CTkLabel(self.sidebar_frame, text="Log Out:", anchor="w", font=customtkinter.CTkFont(size=12, weight="bold"))
        self.logoutbtnlabel.grid(row=11, column=0, padx=20, pady=(10, 0))
        self.logoutbtn = customtkinter.CTkButton(self.sidebar_frame, text="Logout", anchor="c", command=open_login)
        self.logoutbtn.grid(row=12, column=0, padx=20, pady=(10, 20))

        # Set default appearance mode to Dark
        self.appearance_mode_optionemenu.set("Dark")

        # Add title label to the main window
        title_label = customtkinter.CTkLabel(self, text="Dashboard", font=("Century Gothic", int(screen_width/50), "bold"))
        title_label.place(relx=0.15, rely=0.03)  

        self.current_user = self.get_current_user_username()

        # Buttons to toggle between income and expenditure pie charts
        self.toggle_pie_chart_button = customtkinter.CTkButton(self, text="Show Expenditure Pie Chart",command=self.toggle_pie_chart)
        self.toggle_pie_chart_button.place(relx=0.28, rely=0.45)

        # Creates initial pie chart (incomes)
        self.pie_chart_frame = None
        self.current_pie_chart = None
        self.create_pie_chart_income()

        # Create bar graphs for payments and expenditures
        self.create_bar_graph_payment()
        self.create_bar_graph_expenditure()
        
        # Create frame to display annual totals
        self.create_total_frame()

    # Method to change appearance mode
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    # Method to get the username of the currently logged in user
    def get_current_user_username(self):
        # Fetch the username of the current user from the 'current_user' table
        cursor.execute("SELECT username FROM logininfo WHERE user_logged_in = 1")
        row = cursor.fetchone()

        if row:
            username = row[0]
        else:
            username = None

        return username

    # SQL script to create paymentinfo table
    def create_paymentinfo_table(self):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS paymentinfo (
            username TEXT,
            payment_amount REAL,
            reason TEXT,
            title TEXT,
            first_name TEXT,
            last_name TEXT,
            payment_date DATE,
            FOREIGN KEY (username) REFERENCES logininfo(username)
        )
    ''')
        conn.commit()

    # SQL script to create expenditureinfo table
    def create_expenditureinfo_table(self):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenditureinfo (
            username TEXT,
            expenditure_amount REAL,
            reason TEXT,
            companyname TEXT,
            expenditure_date DATE,
            FOREIGN KEY (username) REFERENCES logininfo(username)
        )
    ''')
        conn.commit()

    # Method to switch between pie chart modes (incomes and expenditures)
    def toggle_pie_chart(self):
        # Toggle between income and expenditure pie charts
        if self.toggle_pie_chart_button.cget("text") =="Show Expenditure Pie Chart":
            self.create_pie_chart_expenditure()
            self.toggle_pie_chart_button.configure(text="Show Income Pie Chart")
        else:
            self.create_pie_chart_income()
            self.toggle_pie_chart_button.configure(text="Show Expenditure Pie Chart")

    # Method to create pie chart for income
    def create_pie_chart_income(self):
        if self.pie_chart_frame:
            self.pie_chart_frame.destroy()

        self.pie_chart_frame = customtkinter.CTkFrame(self)
        self.pie_chart_frame.place(relx=0.2, rely=0.55, relwidth=0.25, relheight=0.4)

        if self.current_user is not None:
            last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            cursor.execute("SELECT reason, payment_amount FROM paymentinfo WHERE username = ? AND payment_date >= ? AND payment_date <= ?", (self.current_user, last_year_date, datetime.now().strftime('%Y-%m-%d')))
            payment_data = cursor.fetchall()

            if payment_data:  
                payment_reason_totals = {}
                for reason, amount in payment_data:
                    if reason not in payment_reason_totals:
                        payment_reason_totals[reason] = 0
                    payment_reason_totals[reason] += amount

                labels = payment_reason_totals.keys()
                amounts = payment_reason_totals.values()

                self.current_pie_chart = plt.figure(figsize=(5  , 5))
                plt.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.axis('equal') 

                canvas = FigureCanvasTkAgg(self.current_pie_chart, master=self.pie_chart_frame)
                canvas.get_tk_widget().pack(fill='both', expand=True)
            else:
                no_data_label = customtkinter.CTkLabel(self.pie_chart_frame, text="No payment data found for the current user in the last year.")
                no_data_label.pack(fill='both', expand=True)
        else:
            no_user_label = customtkinter.CTkLabel(self.pie_chart_frame, text="No current user found.")
            no_user_label.pack(fill='both', expand=True)

    # Method to create pie chart for expenditure
    def create_pie_chart_expenditure(self):
        if self.pie_chart_frame:
            self.pie_chart_frame.destroy()
            self.pie_chart_frame = customtkinter.CTkFrame(self)
            self.pie_chart_frame.place(relx=0.2, rely=0.55, relwidth=0.25, relheight=0.4)

        if self.current_user is not None:
            last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            cursor.execute("SELECT reason, expenditure_amount FROM expenditureinfo WHERE username = ? AND expenditure_date >= ? AND expenditure_date <= ?", (self.current_user, last_year_date, datetime.now().strftime('%Y-%m-%d')))
            expenditure_data = cursor.fetchall()

            if expenditure_data:  
                expenditure_reason_totals = {}
                for reason, amount in expenditure_data:
                    if reason not in expenditure_reason_totals:
                        expenditure_reason_totals[reason] = 0
                    expenditure_reason_totals[reason] += amount

                labels = expenditure_reason_totals.keys()
                amounts = expenditure_reason_totals.values()

                self.current_pie_chart = plt.figure(figsize=(5, 5))
                plt.pie(amounts, labels=labels, autopct='%1.1f%%', startangle=140)
                plt.axis('equal') 

                canvas = FigureCanvasTkAgg(self.current_pie_chart, master=self.pie_chart_frame)
                canvas.get_tk_widget().pack(fill='both', expand=True)
            else:
                no_data_label = customtkinter.CTkLabel(self.pie_chart_frame, text="No expenditure data found for the current user in the last year.")
                no_data_label.pack(fill='both', expand=True)
        else:
            no_user_label = customtkinter.CTkLabel(self.pie_chart_frame, text="No current user found.")
            no_user_label.pack(fill='both', expand=True)

    # Method to create bar graph for payments
    def create_bar_graph_payment(self):
        graph_frame = customtkinter.CTkFrame(self)
        graph_frame.place(relx=0.55, rely=0.05, relwidth=0.4, relheight=0.4)

        if self.current_user is not None:
            last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            cursor.execute("SELECT payment_date, payment_amount FROM paymentinfo WHERE username = ? AND payment_date >= ? AND payment_date <= ?", (self.current_user, last_year_date, datetime.now().strftime('%Y-%m-%d')))
            payment_data = cursor.fetchall()

            if payment_data:  
                payment_dates, payment_amounts = zip(*payment_data)

                monthly_totals = {}
                for date, amount in zip(payment_dates, payment_amounts):
                    date = datetime.strptime(date, '%Y-%m-%d')
                    year_month = date.strftime('%Y-%m')

                    if year_month not in monthly_totals:
                        monthly_totals[year_month] = 0

                    monthly_totals[year_month] += amount

                sorted_monthly_totals = sorted(monthly_totals.items(), key=lambda x: x[0])

                labels = []
                total_amounts = []
                for date, total_amount in sorted_monthly_totals:
                    year, month = date.split('-')
                    labels.append(f"{month}/{year}")
                    total_amounts.append(total_amount)

                fig = plt.Figure(figsize=(6, 5), dpi=100)
                plot = fig.add_subplot(111)
                bar_width = 0.2
                x_positions = list(range(len(labels)))

                plot.bar(x_positions, total_amounts, color='#4caf50', width=bar_width)

                plot.set_xticks(x_positions)
                plot.set_xticklabels(labels, rotation=0, horizontalalignment="center")

                plot.set_ylabel("Total Payment Amount")
                plot.set_title("Total Payment Amounts by Month (Last Year)")

                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.get_tk_widget().pack(fill='both', expand=True)
            else:
                no_data_label = customtkinter.CTkLabel(graph_frame, text="No payment data found for the current user in the last year.")
                no_data_label.pack(fill='both', expand=True)
        else:
            no_user_label = customtkinter.CTkLabel(graph_frame, text="No current user found.")
            no_user_label.pack(fill='both', expand=True)

    # Method to create bar graph for expenditures
    def create_bar_graph_expenditure(self):
        graph_frame = customtkinter.CTkFrame(self)
        graph_frame.place(relx=0.55, rely=0.55, relwidth=0.4, relheight=0.4)

        if self.current_user is not None:
            last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            cursor.execute("SELECT expenditure_date, expenditure_amount FROM expenditureinfo WHERE username = ? AND expenditure_date >= ? AND expenditure_date <= ?", (self.current_user, last_year_date, datetime.now().strftime('%Y-%m-%d')))
            expenditure_data = cursor.fetchall()

            if expenditure_data:  
                expenditure_dates, expenditure_amounts = zip(*expenditure_data)

                monthly_totals = {}
                for date, amount in zip(expenditure_dates, expenditure_amounts):
                    date = datetime.strptime(date, '%Y-%m-%d')
                    year_month = date.strftime('%Y-%m')

                    if year_month not in monthly_totals:
                        monthly_totals[year_month] = 0

                    monthly_totals[year_month] += amount

                sorted_monthly_totals = sorted(monthly_totals.items(), key=lambda x: x[0])

                labels = []
                total_amounts = []
                for date, total_amount in sorted_monthly_totals:
                    year, month = date.split('-')
                    labels.append(f"{month}/{year}")
                    total_amounts.append(total_amount)
                    
                fig = plt.Figure(figsize=(6, 5), dpi=100)
                plot = fig.add_subplot(111)
                bar_width = 0.2
                x_positions = list(range(len(labels)))

                plot.bar(x_positions, total_amounts, color='#FF0000', width=bar_width)

                plot.set_xticks(x_positions)
                plot.set_xticklabels(labels, rotation=0, horizontalalignment="center")

                plot.set_ylabel("Total Expenditure Amount")
                plot.set_title("Total Expenditure Amounts by Month (Last Year)")

                canvas = FigureCanvasTkAgg(fig, master=graph_frame)
                canvas.get_tk_widget().pack(fill='both', expand=True)
            else:
                no_data_label = customtkinter.CTkLabel(graph_frame, text="No expenditure data found for the current user in the last year.")
                no_data_label.pack(fill='both', expand=True)
        else:
            no_user_label = customtkinter.CTkLabel(graph_frame, text="No current user found.")
            no_user_label.pack(fill='both', expand=True)

    # Method to create and display the annual totals 
    def create_total_frame(self):
        total_frame = customtkinter.CTkFrame(self)
        total_frame.place(relx=0.23, rely=0.15, relwidth=0.25, relheight=0.14)

        if self.current_user is not None:
            last_year_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            current_date = datetime.now().strftime('%Y-%m-%d')

            monthly_income = defaultdict(float)
            monthly_expenditure = defaultdict(float)

            cursor.execute("SELECT payment_date, payment_amount FROM paymentinfo WHERE username = ? AND payment_date >= ? AND payment_date <= ?", 
                        (self.current_user, last_year_date, current_date))
            payment_data = cursor.fetchall()

            for date, amount in payment_data:
                month_year = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
                monthly_income[month_year] += amount

            cursor.execute("SELECT expenditure_date, expenditure_amount FROM expenditureinfo WHERE username = ? AND expenditure_date >= ? AND expenditure_date <= ?", 
                        (self.current_user, last_year_date, current_date))
            expenditure_data = cursor.fetchall()

            for date, amount in expenditure_data:
                month_year = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')
                monthly_expenditure[month_year] += amount

            total_income = sum(monthly_income.values())
            total_expenditure = sum(monthly_expenditure.values())
            net_income = total_income - total_expenditure

            income_label = customtkinter.CTkLabel(total_frame, text=f"Total Annual Income: £{total_income:.2f}", font=customtkinter.CTkFont(size=16))
            income_label.pack(fill='both', expand=True)

            expenditure_label = customtkinter.CTkLabel(total_frame, text=f"Total Annual Expenditure: £{total_expenditure:.2f}", font=customtkinter.CTkFont(size=16))
            expenditure_label.pack(fill='both', expand=True)

            net_income_label = customtkinter.CTkLabel(total_frame, text=f"Net Income: £{net_income:.2f}", font=customtkinter.CTkFont(size=16))
            net_income_label.pack(fill='both', expand=True)
        else:
            no_user_label = customtkinter.CTkLabel(total_frame, text="No current user found.")
            no_user_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")


app = App()
app.mainloop()











