import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
import re
import os
from tkinter import PhotoImage


class Event:
    def __init__(self, name, date, time, location, description, ticket_price, email_admin):
        self.name = name
        self.date = date
        self.time = time
        self.location = location
        self.description = description
        self.ticket_price = ticket_price
        self.email = email_admin
        self.participants = []  # لیست شرکت‌کنندگان

    def add_participant(self, participant):
        self.participants.append(participant)

    def remove_participant(self, participant):
        self.participants.remove(participant)

    def edit_participant(self, old_participant, new_participant):
        index = self.participants.index(old_participant)
        self.participants[index] = new_participant



class EventManager:
    def __init__(self):
        self.events = []

    def create_event(self, name, date, time, location, description,
                     ticket_price, admin_email):
        event = Event(name, date, time, location, description, ticket_price, admin_email)
        self.events.append(event)

    def find_admin_email(self, event_name):
        for event in self.events:
            if event.name == event_name:
                return event.email
        return None

    def show_calendar(self):
        self.calendar_window = tk.Toplevel(window)
        self.calendar_window.title("Calendar events")

        self.calendar = Calendar(self.calendar_window, selectmode='day',
                                 year=2024, month=5, day=29)
        self.calendar.pack(pady=20)

        select_date_button = tk.Button(self.calendar_window,
                                       text="Select date",
                                       command=self.select_date)
        select_date_button.pack(pady=10)

    def refresh_event_listbox(self):
        event_listbox.delete(0, tk.END)
        for event in self.events:
            event_listbox.insert(tk.END, event.name)

    def select_date(self):
        selected_date = self.calendar.get_date()
        # selected_date = standardize_date(selected_date)
        self.calendar_window.destroy()

        event_found = False
        for event in self.events:
            print(event.date, selected_date)
            if event.date == selected_date:
                event_found = True
                event_details = f"Event:{event.name}\nDate:{event.date}\
                \nTime:{event.name}\nLocation:{event.location}\
                \nDiscription:{event.description}"
                messagebox.showinfo("Event found", event_details)
                break
        if not event_found:
            messagebox.showinfo("Event not found", "There are no events on this date")


def show_participants(event):
    participants_window = tk.Toplevel(window)
    participants_window.title(f"Participants for {event.name}")

    participants_listbox = tk.Listbox(participants_window, font=("arial", 12))
    participants_listbox.pack()

    for participant in event.participants:
        participants_listbox.insert(tk.END, participant)

    def remove_selected_participant():
        selected_indices = participants_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            participant = event.participants[index]
            event.remove_participant(participant)
            participants_listbox.delete(index)

    def edit_selected_participant():
        selected_indices = participants_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            old_participant = event.participants[index]

            edit_window = tk.Toplevel(participants_window)
            edit_window.title("Edit Participant")

            new_participant_entry = tk.Entry(edit_window, font=("arial", 12))
            new_participant_entry.pack()
            new_participant_entry.insert(0, old_participant)

            def save_edit():
                new_participant = new_participant_entry.get()
                event.edit_participant(old_participant, new_participant)
                participants_listbox.delete(index)
                participants_listbox.insert(index, new_participant)
                edit_window.destroy()

            save_button = tk.Button(edit_window, text="Save", command=save_edit)
            save_button.pack()
            
    remove_button = tk.Button(participants_window, text="Remove Selected", command=remove_selected_participant)
    remove_button.pack()

    edit_button = tk.Button(participants_window, text="Edit Selected", command=edit_selected_participant)
    edit_button.pack()


def close_all_top_levels():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()


def create_event_button_clicked():

    name = name_entry.get()
    date = date_entry.get()
    time = time_entry.get()
    time_pattern = r'^(0?[0-9]|1[0-9]|2[0-3]):([0-5][0-9])$'
    if not bool(re.match(time_pattern, time)):
        messagebox.showerror("pattern error", "time is wrong")
        return 0
    location = location_entry.get()
    description = description_entry.get()
    ticket_price = ticket_price_entry.get()
    price_pattern = r'^\d*\.?\d+$'
    if not bool(re.match(price_pattern, ticket_price)):
        messagebox.showerror("pattern error", "ticket price is wrong\nplease use float number")
        return 0
    email_admin = admin_email_entry.get()
    email_pattern = r'^[a-zA-Z](\.?[a-zA-Z0-9]){5,29}@gmail\.com'
    if not bool(re.match(email_pattern, email_admin)):
        messagebox.showerror("pattern error", "gmail is wrong")
        return 0
    event_manager.create_event(name, date, time, location,
                               description, ticket_price, email_admin)

    event_listbox.insert(tk.END, name)


def buy_ticket_button_clicked(buyer, email):
    selected_indices = event_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Error", "No event selected")
        return
    index = selected_indices[0]
    selected_event = event_manager.events[index]

    email_pattern = r'^[a-zA-Z](\.?[a-zA-Z0-9]){5,29}@gmail\.com'
    if not bool(re.match(email_pattern, email)):
        messagebox.showinfo(selected_event.name, "Gmail is wrong\nUnsuccessful purchase")
        return 0
    else:
        message = f"Event: {selected_event.name}\nDate: {selected_event.date}\nTime: {selected_event.time}\nLocation: {selected_event.location}\nDescription: {selected_event.description}"

        if send_email(email, "Event information", message):
            messagebox.showinfo(selected_event.name, "Successful purchase")
            selected_event.add_participant(buyer)  # اضافه کردن شرکت‌کننده به لیست

            admin_g = event_manager.find_admin_email(selected_event.name)
            send_email(admin_g, "Task your event", f"A person named {buyer} bought your event\nPlease do the work for this buyer and manage the event for this person\n\n\nEvent management system")

    event_manager.refresh_event_listbox()
    close_all_top_levels()


def send_email(receiver_email, subject, message):
    if not gmail_user or not gmail_password:
        messagebox.showerror("Environment variable")
        return 0

    server = None
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_user, gmail_password)

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server.send_message(msg)
        del msg
        return 1
    except smtplib.SMTPAuthenticationError:
        messagebox.showerror("Athentication error")
        return 0
    except smtplib.SMTPException:
        messagebox.showerror("An error occurred while sending email")
        return 0
    finally:
        server.quit()


def save_to_database(username, password, email):
    email_pattern = r'^[a-zA-Z](\.?[a-zA-Z0-9]){5,29}@gmail\.com'
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
    if not bool(re.match(email_pattern, email)):
        messagebox.showerror("pattern error", "email is wrong")
        return 0
    if not bool(re.match(password_pattern, password)):
        messagebox.showerror("pattern error", "password is weak\npassword must include [a-zA-Z0-9] and 8 character")
        return 0
    conn = sqlite3.connect('user.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL,
              email TEXT NOT NULL)''')

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        messagebox.showerror("Error", "Username already exists")
    else:
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully")
    conn.close()


def open_registration_window():
    registration_window = tk.Toplevel(window)
    registration_window.title('Sign up')

    username_label = tk.Label(registration_window, text='Username')
    username_label.pack()
    username_entry = tk.Entry(registration_window)
    username_entry.pack()

    password_label = tk.Label(registration_window, text='Password')
    password_label.pack()
    password_entry = tk.Entry(registration_window, show='*')
    password_entry.pack()

    email_label = tk.Label(registration_window, text='Gmail')
    email_label.pack()
    email_entry = tk.Entry(registration_window)
    email_entry.pack()

    save_button = tk.Button(registration_window, text="Save", command=lambda: save_to_database(username_entry.get(), password_entry.get(), email_entry.get()))
    save_button.pack()

    # open_registration_button = tk.Button(registration_window, text="Open Registration", command=open_registration_window)
    # open_registration_button.pack()


def check_info(username, password):
    conn = sqlite3.connect('user.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    if user:
        if user[2] == password:
            buy_ticket_button_clicked(user[1], user[3])
        else:
            messagebox.showerror("Error", "Incorrect password")
    else:
        messagebox.showerror("Error", "Username does not exist, Please first sign up!")


def sign_inup(name_event):
    def callback():
        popup_window2 = tk.Toplevel(window)
        popup_window2.title(f"buy ticket for {name_event}")

        sing_in_label = tk.Label(popup_window2, text="Sign in")
        sing_in_label.pack()

        user_label = tk.Label(popup_window2, text="Username")
        user_label.pack()
        user_entry = tk.Entry(popup_window2)
        user_entry.pack()

        pass_label = tk.Label(popup_window2, text="Password")
        pass_label.pack()
        pass_entry = tk.Entry(popup_window2, show="*")
        pass_entry.pack()

        buy_ticket_bitton = tk.Button(popup_window2, text="Sign in & buy ticket", command=lambda: check_info(user_entry.get(), pass_entry.get()))
        buy_ticket_bitton.pack()
        sign_up_button = tk.Button(popup_window2, text="Sign up", command=open_registration_window)
        sign_up_button.pack()

    return callback


def on_event_select(event):
    index = event_listbox.curselection()[0]
    selected_event = event_manager.events[index]
    popup_window = tk.Toplevel(window)
    popup_window.title(selected_event.name)

    details_label = tk.Label(popup_window, text=f"Date: {selected_event.date}\nTime: {selected_event.time}\nLocation: {selected_event.location}\nDescription: {selected_event.description}")
    details_label.pack()

    buy_ticket_button = tk.Button(popup_window, text="Buy ticket", command=sign_inup(selected_event.name))
    buy_ticket_button.pack()

    show_participants_button = tk.Button(popup_window, text="Show Participants", command=lambda: show_participants(selected_event))
    show_participants_button.pack()


event_manager = EventManager()

gmail_user = os.environ.get('GMAIL_USER')
gmail_password = os.environ.get('GMAIL_PASSWORD')

window = tk.Tk()
window.title("Event management system")

background_image = PhotoImage(file=r"C:\Users\yasin\Downloads\11zon_converted\time___the_world_clock___worldwide-wallpaper-2880x1800_2_11zon.png")
background_label = tk.Label(window, image=background_image)
background_label.place(relwidth=1, relheight=1)

window.configure(bg="#34495e")

label_style = {"font": ("arial", 12), "bg": "#d9d9d9", "fg": "black"}
entry_style = {"font": ("arial", 12), "bg": "#ecf0f1"}
button_style = {"font": ("arial", 12), "bg": "silver", "fg": "black"}

name_label = tk.Label(window, text="Name event", **label_style)
name_label.pack()
name_entry = tk.Entry(window, **entry_style)
name_entry.pack()

date_label = tk.Label(window, text="Date", **label_style)
date_label.pack()
date_entry = DateEntry(window, **entry_style)
date_entry.pack()

time_label = tk.Label(window, text="Time(XX:XX)", **label_style)
time_label.pack()
time_entry = tk.Entry(window, **entry_style)
time_entry.pack()

location_label = tk.Label(window, text="Location", **label_style)
location_label.pack()
location_entry = tk.Entry(window, **entry_style)
location_entry.pack()

description_label = tk.Label(window, text="Discription", **label_style)
description_label.pack()
description_entry = tk.Entry(window, **entry_style)
description_entry.pack()

ticket_price_label = tk.Label(window, text="Ticket price", **label_style)
ticket_price_label.pack()
ticket_price_entry = tk.Entry(window, **entry_style)
ticket_price_entry.pack()

admin_email = tk.Label(window, text="Admin email", **label_style)
admin_email.pack()
admin_email_entry = tk.Entry(window, **entry_style)
admin_email_entry.pack()

create_event_button = tk.Button(window, text="Create event",
                                command=create_event_button_clicked, **button_style)
create_event_button.pack()

show_calendar_button = tk.Button(window, text="Show calendar",
                                 command=event_manager.show_calendar, **button_style)
show_calendar_button.pack()

list_label = tk.Label(window, text="Event list", **label_style)
list_label.pack()
event_listbox = tk.Listbox(window, bg="silver", font=("arial", 12))
event_listbox.pack()

event_listbox.bind('<<ListboxSelect>>', on_event_select)

window.mainloop()
