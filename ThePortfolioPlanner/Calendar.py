# Importing necessary imports for GUI development, operating system interaction, and Google authentication process.

import os  # Operating system functionality.
import pytz  # Time zone management.
import tkinter as tk  # GUI development.
from tkinter import (  # Specific GUI components.
messagebox, Scrollbar, ttk
)
from google_auth_oauthlib.flow import InstalledAppFlow  # Google authentication.
from googleapiclient.discovery import build  # Google API interaction.
from google.oauth2.credentials import Credentials  # Google credentials handling.
from google.auth.transport.requests import Request  # HTTP requests with credentials.
from datetime import datetime, timedelta  # Date and time manipulation.
from tkcalendar import DateEntry  # Calendar widget for tkinter.
from subprocess import call  # Executing system commands.
import sqlite3  # SQLite database management.
import customtkinter as ctk  # Custom tkinter appearance.


#required Google scopes
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

#database connection
DATABASE_PATH = 'userdata.db'
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

#open login page function
def open_login():
    app.destroy()
    call(["python", "Login.py"])

#open finance page function
def open_finances():
    app.destroy()
    call(["python", "Finances.py"]) 

#open dashboard page function
def open_dash():
    app.destroy()
    call(["python", "Dashboard.py"])

#defines google calendar class 
class GoogleCalendarApp(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"1920x1080+{int((screen_width - 1920) / 2)}+0") 
        self.conn = sqlite3.connect("userdata.db")
        self.cursor = self.conn.cursor()
        self.find_last_username()
        sidebar_width = int(screen_width * 0.075)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            start_datetime TEXT,
            end_datetime TEXT,
            num_guests INTEGER,
            location TEXT,
            google_event_id TEXT,
            username TEXT,
            FOREIGN KEY (username) REFERENCES logininfo(username)
        )""")
        self.conn.commit()  

        self.title("Google Calendar")
        self.username = username

        if self.username_has_changed(username):
            self.refresh_google_auth()
            
        self.service = self.authorize_google_calendar()

        self.sidebar_frame = ctk.CTkFrame(self, width=sidebar_width, height=screen_height, corner_radius=0)
        self.sidebar_frame.place(relx=0, rely=0, relwidth=0.09, relheight=1)

        # Logo label
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Welcome!", font=ctk.CTkFont("Century Gothic", int(screen_width/80), weight="bold"))
        self.logo_label.place(relx=0.5, rely=0.02, anchor="n", relwidth=0.8)

        # Buttons in the sidebar frame
        # Configure and place the buttons in the sidebar frame
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Dashboard", height=50, command=open_dash)
        self.sidebar_button_1.place(relx=0.5, rely=0.1, anchor="n", relwidth=0.8)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="Finances", height=50, command=open_finances)
        self.sidebar_button_2.place(relx=0.5, rely=0.3, anchor="n", relwidth=0.8)

        # Calendar button
        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Calendar", height=50)
        self.sidebar_button_3.place(relx=0.5, rely=0.5, anchor="n", relwidth=0.8)

        self.logoutbtnlb = ctk.CTkLabel(self.sidebar_frame, text="Log Out:", font=ctk.CTkFont(size=12, weight="bold"))
        self.logoutbtnlb.place(relx=0.12, rely=0.88, anchor="nw", relwidth=0.8)
        
        title_label = ctk.CTkLabel(self, text="Calendar", font=("Century Gothic", int(screen_width/50), "bold"))
        title_label.place(relx=0.15, rely=0.03)
        
        self.logoutbtn = ctk.CTkButton(self.sidebar_frame, text="Logout", anchor="c", command=open_login)
        self.logoutbtn.place(relx=0.5, rely=0.92, anchor="n", relwidth=0.8)

        self.create_event_frame = ctk.CTkFrame(self)
        self.create_event_frame.configure(bg_color="gray", height=1000, width=800)
        self.create_event_frame.place(relx=0.109, rely=0.15, relwidth=0.415, relheight=0.75)

        self.create_event_label = ctk.CTkLabel(self.create_event_frame, text="Create New Calendar Event", font=ctk.CTkFont(size=20, weight="bold"))
        self.create_event_label.place(relx=0.33, rely=0.02)
    
        self.title_label = ctk.CTkLabel(self.create_event_frame, text="Title:", font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.place(relx=0.48, rely=0.1)
        self.event_title = ctk.CTkEntry(self.create_event_frame)
        self.event_title.place(relx=0.3, rely=0.15, relwidth=0.4)

        self.event_date_label = ctk.CTkLabel(self.create_event_frame, text="Date:", font=ctk.CTkFont(size=14, weight="bold"))
        self.event_date_label.place(relx=0.48, rely=0.25)
        self.event_date = DateEntry(self.create_event_frame, date_pattern="dd/mm/yyyy")
        self.event_date.place(relx=0.3, rely=0.3, relwidth=0.4)

        self.start_time_label = ctk.CTkLabel(self.create_event_frame, text="Start Time:", font=ctk.CTkFont(size=14, weight="bold"))
        self.start_time_label.place(relx=0.15, rely=0.4)
        self.start_time = ctk.CTkEntry(self.create_event_frame, placeholder_text="08:00")
        self.start_time.place(relx=0.1, rely=0.45)

        self.end_time_label = ctk.CTkLabel(self.create_event_frame, text="End Time:", font=ctk.CTkFont(size=14, weight="bold"))
        self.end_time_label.place(relx=0.75, rely=0.4)
        self.end_time = ctk.CTkEntry(self.create_event_frame, placeholder_text="09:00")
        self.end_time.place(relx=0.7, rely=0.45)
        
        self.all_day_var = tk.BooleanVar() 
        self.all_day_checkbutton = tk.Checkbutton(self.create_event_frame, text="All Day", variable=self.all_day_var)
        self.all_day_checkbutton.place(relx=0.46, rely=0.45)

        self.num_guests_label = ctk.CTkLabel(self.create_event_frame, text="Number of Guests:",font=ctk.CTkFont(size=14, weight="bold"))
        self.num_guests_label.place(relx=0.425, rely=0.55)
        self.num_guests = ctk.CTkEntry(self.create_event_frame)
        self.num_guests.place(relx=0.41, rely=0.6)

        self.location_label = ctk.CTkLabel(self.create_event_frame, text="Location:", font=ctk.CTkFont(size=14, weight="bold"))
        self.location_label.place(relx=0.46, rely=0.7)
        self.location = ctk.CTkEntry(self.create_event_frame)
        self.location.place(relx=0.3, rely=0.75, relwidth=0.4)

        self.add_event_button = ctk.CTkButton(self.create_event_frame, text="Add Event", command=self.add_event)
        self.add_event_button.place(relx=0.4, rely=0.9)
        
        self.events_frame = ctk.CTkFrame(self)
        self.events_frame.configure(bg_color="gray", height=800, width=800)
        self.events_frame.place(relx=0.54, rely=0.15, relwidth=0.445, relheight=0.75)  
        
        #treeview config
        self.event_tree = ttk.Treeview(self.events_frame, columns=("ID", "Title", "Start Time", "End Time", "Guests", "Location"), show="headings", height=30)
        self.event_tree.heading("ID", text="ID")
        self.event_tree.heading("Title", text="Title")
        self.event_tree.heading("Start Time", text="Start Time")
        self.event_tree.heading("End Time", text="End Time")
        self.event_tree.heading("Guests", text="Guests")
        self.event_tree.heading("Location", text="Location")
        self.event_tree.column("#0", width=0, stretch=tk.NO)
        self.event_tree.column("ID", width=25, anchor=tk.CENTER)
        self.event_tree.column("Title", width=135, anchor=tk.CENTER)
        self.event_tree.column("Start Time", width=92, anchor=tk.CENTER) 
        self.event_tree.column("End Time", width=92, anchor=tk.CENTER)
        self.event_tree.column("Guests", width=90, anchor=tk.CENTER)
        self.event_tree.column("Location", width=175, anchor=tk.CENTER)
        self.event_tree.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.85)

        #scrollbar config for treeview
        self.scrollbar = Scrollbar(self.events_frame, orient="vertical")
        self.scrollbar.config(command=self.event_tree.yview)
        self.scrollbar.place(relx=0.98, rely=0.02, relheight=0.85, relwidth=0.02)

        self.event_tree.config(yscrollcommand=self.scrollbar.set)
        self.event_tree.bind('<Double-Button-1>', self.delete_selected_event)

        self.populate_events_tree()

        self.delete_event_button = ctk.CTkButton(self.events_frame, text="Delete Event", command=self.delete_selected_event)
        self.delete_event_button.place(relx=0.44, rely=0.9)
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.place(relx=0.09, rely=0.84, anchor="sw", relwidth=0.8)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance" "\n" "Mode:", anchor="n", font=ctk.CTkFont(size=12, weight="bold"))
        self.appearance_mode_label.place(relx=0.10, rely=0.80, anchor="sw", relwidth=0.8)




#function to display past events in treeview
    def populate_events_tree(self):
        self.event_tree.delete(*self.event_tree.get_children())
        self.cursor.execute("SELECT * FROM user_events WHERE username = (SELECT username FROM logininfo WHERE user_logged_in = 1)")

        events = self.cursor.fetchall()
        for event in events:
            self.event_tree.insert("", "end", values=event)

#function to add event 
    def add_event(self):
        event_title = self.event_title.get()
        event_date = self.event_date.get()
        all_day = self.all_day_var.get()
        start_time = self.start_time.get()
        end_time = self.end_time.get()
        num_guests = self.num_guests.get()
        event_location = self.location.get()

        # Input validation
        if not event_title or not event_date or not start_time or not end_time or not num_guests or not event_location:
            messagebox.showerror("Input Error", "Please enter all fields")
            return
        if len(event_title) > 50 or len(event_location) > 50  or len(num_guests) > 10:
            messagebox.showerror("Input Error", "At least one of your inputs is too long")
            return
        if not num_guests.isdigit():
            messagebox.showerror("Input Error", "Guest Value must be an integer")
            return

        # Parses date input
        event_date = datetime.strptime(event_date, "%d/%m/%Y").date()
        event_datetime = datetime.combine(event_date, datetime.min.time())

        if all_day:
            # Sets start and end times for all-day events
            start_datetime = event_datetime.replace(hour=0, minute=0)
            end_datetime = event_datetime.replace(hour=23, minute=59)
        else:
            # Parses start and end times
            start_datetime = datetime.strptime(start_time, "%H:%M")
            end_datetime = datetime.strptime(end_time, "%H:%M")
            # Combines date and times
            start_datetime = event_datetime.replace(hour=start_datetime.hour, minute=start_datetime.minute)
            end_datetime = event_datetime.replace(hour=end_datetime.hour, minute=end_datetime.minute)

        # Converts start and end times to UTC
        start_datetime_utc = self.convert_to_utc(start_datetime)
        end_datetime_utc = self.convert_to_utc(end_datetime)
      
      #dictionary of the foramt of the event for google calendar  
        event = {
            'summary': event_title,
            'start': {
                'dateTime': start_datetime_utc.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_datetime_utc.isoformat(),
                'timeZone': 'UTC',
            },
            'description': f"Guests =  {num_guests}",
            'location': event_location,
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            messagebox.showinfo("Event Created", "Your event has been created! \n Please check Google Calendar to see your event")

            # Adds event to the database
            self.add_event_to_database(event)
            # Updates the treeview
            self.populate_events_tree()
        except Exception as e:
            messagebox.showerror("Error!", f'Error creating the event!: {str(e)}')
            
            
    def convert_to_utc(self, dt):
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            local_tz = pytz.timezone('Europe/London')
            local_dt = local_tz.localize(dt, is_dst=None)
        else:
            local_dt = dt
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt




    def add_event_to_database(self, event):
        try:
            # Converts datetime values to strings without "T" and "Z"
            start_datetime_str = event['start']['dateTime'].replace("T", " ").replace("Z", "")
            end_datetime_str = event['end']['dateTime'].replace("T", " ").replace("Z", "")

            # Inserts the event details along with the username into the user_events table
            self.cursor.execute("""
            INSERT INTO user_events (username, title, start_datetime, end_datetime, num_guests, location)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (self.username, event['summary'], start_datetime_str, end_datetime_str, event['description'], event['location']))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Error!", f'Error adding event to database: {str(e)}')


    def delete_selected_event(self, event=None):
        selected_item = self.event_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an event to delete.")
            return

        # Gets the ID, title, and start date of the selected item in the treeview
        event_id, event_title, start_datetime_str = self.event_tree.item(selected_item, "values")[0:3]
        print("Local Event ID:", event_id)  # Debugging statement

        # Prompts the user to confirm deletion
        confirm_delete = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this event?")

        if confirm_delete:
            try:
                # Deletes the event from the database
                self.cursor.execute("DELETE FROM user_events WHERE id=?", (event_id,))
                self.conn.commit()

                # Finds the event in Google Calendar based on title and start date
                google_event_id = self.find_google_event_id(event_title, start_datetime_str)
                print("Google Event ID:", google_event_id)  # Debugging statement
                if google_event_id:
                    # Deletes  the event from Google Calendar
                    self.service.events().delete(calendarId='primary', eventId=google_event_id).execute()
                    messagebox.showinfo("Success", "Event deleted successfully!")
                else:
                    messagebox.showwarning("Warning", "Event not found in Google Calendar!")

                # Updates the treeview
                self.populate_events_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete event: {str(e)}")





    def find_google_event_id(self, event_title, start_datetime_str):
        try:
            start_datetime = datetime.fromisoformat(start_datetime_str)
        except ValueError:
            start_datetime = datetime.strptime(start_datetime_str[:-6], "%Y-%m-%d %H:%M:%S")

        # Converts start datetime to the same timezone as Google Calendar (UTC)
        start_datetime_utc = self.convert_to_utc(start_datetime)

        # Defines start and end datetime for searching events (considering a small time range around the start time)
        start_time_min = start_datetime_utc - timedelta(minutes=30)
        start_time_max = start_datetime_utc + timedelta(minutes=30)

        # Defines the query parameters for searching events
        query_params = {
            'q': event_title,  # Event title
            'timeMin': start_time_min.isoformat(),  # Start time (minimum)
            'timeMax': start_time_max.isoformat(),  # Start time (maximum)
            'orderBy': 'startTime',
            'singleEvents': True,
        }

        try:
            # Searches for events in Google Calendar
            events_result = self.service.events().list(calendarId='primary', **query_params).execute()
            events = events_result.get('items', [])

            #find event with corresponding inforamtion 
            for event in events:
                if event.get('summary') == event_title:
                    event_start = event.get('start', {}).get('dateTime')
                    if event_start:
                        event_start_datetime = datetime.fromisoformat(event_start)
                        # Checks if the start time of the event matches closely with the provided start time
                        if abs((event_start_datetime - start_datetime_utc).total_seconds()) <= 1800:  # 30 minutes tolerance
                            return event['id']  # Returns the Google Calendar event ID if found

            # If no matching event is found, return None
            return None
        except Exception as e:
            print(f"Error finding event in Google Calendar: {str(e)}")
            return None

#runs program loop
    def run(self):
        self.mainloop()

#function to refresh Google token file
    def refresh_google_auth(self):
        # Delete the existing token file
        if os.path.exists('token.json'):
            os.remove('token.json')

    def username_has_changed(self, new_username):
        # Retrieves the last username from the database
        self.cursor.execute("SELECT username FROM logininfo WHERE user_logged_in = 0")
        last_username = self.cursor.fetchone()

        # Checks if there is a last username and if it's different
        return last_username and last_username[0] != new_username

    def authorize_google_calendar(self):
        creds = None
        # Retrieves the last username from the database
        self.find_last_username()

        # Checks if the token file exists and if the stored credentials are still valid
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # Checks if credentials need to be refreshed
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Saves the refreshed credentials to the token file
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f'Token refresh failed: {str(e)}')
                creds = None

        # If credentials are still not available, initiates the authorization flow
        if not creds or not creds.valid:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

                # Saves the obtained credentials to the token file
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f'Error obtaining credentials: {str(e)}')
                creds = None

        return build('calendar', 'v3', credentials=creds)

#function to find the last user that logged in 
    def find_last_username(self):
        self.cursor.execute("SELECT username FROM logininfo WHERE user_logged_in = 0")
        last_username = self.cursor.fetchone()

        # Loads existing credentials if available
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # Checks if credentials need to be refreshed
        if creds and creds.valid:
            return build('calendar', 'v3', credentials=creds)

        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        except Exception as e:
            if 'Token has been expired or revoked' in str(e):
                self.refresh_google_auth()
            else:
                print(f'Error obtaining or refreshing credentials: {str(e)}')
                creds = None

        if not creds or not creds.valid:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f'Error obtaining credentials: {str(e)}')
                creds = None

        return build('calendar', 'v3', credentials=creds)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == '__main__':
    # Retrieves the username from the current_user table in the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM logininfo WHERE user_logged_in = 1")
    username_result = cursor.fetchone()
    conn.close()

    if username_result:
        username = username_result[0]
        app = GoogleCalendarApp(username)
        app.run()
    else:
        print("No current user logged in.")


        

